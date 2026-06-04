"""NBR6118 class for designing to the Brazilian Standard NBR 6118:2023."""

from __future__ import annotations

from copy import deepcopy
from math import sqrt
from typing import TYPE_CHECKING

import numpy as np

import concreteproperties.results as res
import concreteproperties.stress_strain_profile as ssp
from concreteproperties.design_codes.design_code import DesignCode
from concreteproperties.material import Concrete, SteelBar

if TYPE_CHECKING:
    from concreteproperties.concrete_section import ConcreteSection


class NBR6118(DesignCode):
    """Design code class for Brazilian standard NBR 6118:2023.

    Usage
    -----
    Instantiate the class with ``gamma_c`` and ``gamma_s``. Then call
    ``create_concrete_material(fck)`` and ``create_steel_material(fy)``.
    All other parameters (Eci, fcd, fyd, alpha_c, lambda, epsilon_cu,
    fctk_inf) are derived automatically from the standard equations.

    Concrete grades supported: C20 to C90.
    Steel classes supported: CA-25, CA-50, CA-60 (identified by ``fy``).

    Notes
    -----
    ``gamma_c`` and ``gamma_s`` are set once at instantiation and applied
    inside ``create_concrete_material`` (fcd = alpha_c*fck/gamma_c) and
    ``create_steel_material`` (fyd = fy/gamma_s). Because the design
    resistances are embedded in the materials, ``capacity_reduction_factor``
    always returns 1.0 and the resulting interaction diagram is already
    the design interaction diagram.

    Examples
    --------
    ::

        from nbr6118 import NBR6118

        # Normal combination (default)
        code = NBR6118(gamma_c=1.4, gamma_s=1.15)

        # Accidental / fire combination
        code_acc = NBR6118(gamma_c=1.2, gamma_s=1.0)

        concrete = code.create_concrete_material(fck=30)
        steel    = code.create_steel_material(fy=500)

        code.assign_concrete_section(concrete_section)
        mi_res, _, _ = code.moment_interaction_diagram()
    """

    # ------------------------------------------------------------------
    # Initialisation
    # ------------------------------------------------------------------

    def __init__(self, gamma_c: float = 1.4, gamma_s: float = 1.15) -> None:
        """Inits the NBR6118 class.

        Parameters
        ----------
        gamma_c : float, optional
            Partial safety factor for concrete. Defaults to ``1.4``.
            Use ``1.2`` for accidental or fire load combinations.
        gamma_s : float, optional
            Partial safety factor for steel. Defaults to ``1.15``.
            Use ``1.0`` for accidental or fire load combinations.
        """
        super().__init__()
        self.gamma_c = gamma_c
        self.gamma_s = gamma_s

    # ------------------------------------------------------------------
    # Section assignment
    # ------------------------------------------------------------------

    def assign_concrete_section(
        self,
        concrete_section: ConcreteSection,
    ) -> None:
        """Assigns a concrete section to the design code.

        Parameters
        ----------
        concrete_section : ConcreteSection
            Concrete section object to analyse.

        Raises
        ------
        ValueError
            If meshed reinforcement regions are present (not supported).
        """
        self.concrete_section = concrete_section

        if self.concrete_section.reinf_geometries_meshed:
            msg = "Meshed reinforcement is not supported in NBR6118."
            raise ValueError(msg)

    # ------------------------------------------------------------------
    # Material factories — public API
    # ------------------------------------------------------------------

    def create_concrete_material(
        self,
        fck: float,
        colour: str = "lightgrey",
    ) -> Concrete:
        r"""Return a ``Concrete`` material object calibrated to NBR 6118.

        Parameters
        ----------
        fck : float
            Characteristic compressive strength at 28 days [MPa].
            Must be between 20 MPa and 90 MPa.
        colour : str, optional
            Rendering colour. Defaults to ``"lightgrey"``.

        Returns
        -------
        Concrete
            Concrete material object ready to use in a ``ConcreteSection``.

        Notes
        -----
        ``gamma_c`` is taken from ``self.gamma_c`` set at instantiation.

        The following NBR 6118:2023 equations are applied:

        **Valid for all concrete (C20-C90)**

        * ``Eci = 5600 * sqrt(fck)``  — initial tangent modulus, cl. 8.2.8
        * ``Ecs = alpha_i * Eci``     — secant modulus
        * ``alpha_i = 0.8 + 0.2 * fck / 80``  capped at 1.0

        **fck <= 50 MPa (normal-strength)**

        * ``epsilon_c2  = 2.0 per mille``  — strain at peak stress
        * ``epsilon_cu2 = 3.5 per mille``  — ultimate compressive strain
        * ``alpha_c = 0.85``               — stress-block intensity factor
        * ``lambda  = 0.80``               — stress-block depth factor

        **fck > 50 MPa (high-strength)**

        * ``epsilon_c2  = 2.0 + 0.085*(fck-50)^0.53  per mille``
        * ``epsilon_cu2 = 2.6 + 35*((90-fck)/100)^4  per mille``
        * ``alpha_c = 0.85 * (1 - (fck-50)/200)``
        * ``lambda  = 0.80 - (fck-50)/400``

        **Tensile strength** (cl. 8.2.5)

        * ``fctm     = 0.3 * fck^(2/3)``       for C20-C50
        * ``fctm     = 2.12 * ln(1+fck/10)``   for C55-C90
        * ``fctk_inf = 0.7 * fctm``

        **Design compressive strength**

        * ``fcd = alpha_c * fck / gamma_c``

        Raises
        ------
        ValueError
            If ``fck`` is not between 20 MPa and 90 MPa.
        """
        if not (20 <= fck <= 90):
            msg = "fck must be between 20 MPa and 90 MPa (NBR 6118 cl. 8.2.3)."
            raise ValueError(msg)

        # ----------------------------------------------------------
        # Elastic modulus  (NBR 6118 cl. 8.2.8)
        # ----------------------------------------------------------
        Eci = 5600.0 * sqrt(fck)                         # initial tangent [MPa]
        alpha_i = min(0.8 + 0.2 * fck / 80.0, 1.0)
        Ecs = alpha_i * Eci                               # secant modulus [MPa]

        # ----------------------------------------------------------
        # Stress-block and strain parameters — split at fck = 50 MPa
        # ----------------------------------------------------------
        if fck <= 50.0:
            # Normal-strength concrete  (NBR 6118 Tab. 8.1 and cl. 17.2.2)
            epsilon_c2  = 2.0e-3                         # strain at peak [dec]
            epsilon_cu2 = 3.5e-3                         # ultimate strain
            alpha_c     = 0.85                           # intensity factor
            lambda_val  = 0.80                           # depth factor
        else:
            # High-strength concrete  (NBR 6118 Tab. 8.1 and cl. 17.2.2)
            epsilon_c2  = (2.0 + 0.085 * (fck - 50.0) ** 0.53) * 1e-3
            epsilon_cu2 = (2.6 + 35.0 * ((90.0 - fck) / 100.0) ** 4) * 1e-3
            alpha_c     = 0.85 * (1.0 - (fck - 50.0) / 200.0)
            lambda_val  = 0.80 - (fck - 50.0) / 400.0

        # ----------------------------------------------------------
        # Design compressive strength
        # ----------------------------------------------------------
        fcd = alpha_c * fck / self.gamma_c                  # [MPa]

        # ----------------------------------------------------------
        # Tensile strength  (NBR 6118 cl. 8.2.5)
        # ----------------------------------------------------------
        if fck <= 50.0:
            fctm = 0.3 * fck ** (2.0 / 3.0)
        else:
            fctm = 2.12 * np.log(1.0 + fck / 10.0)

        fctk_inf = 0.7 * fctm

        # ----------------------------------------------------------
        # Build material
        # ----------------------------------------------------------
        name = (
            f"C{fck:.0f} (NBR 6118:2023) | "
            f"fcd={fcd:.1f} MPa | ecu={epsilon_cu2*1e3:.2f}permille"
        )

        return Concrete(
            name=name,
            density=2.4e-6,
            stress_strain_profile=ssp.ConcreteLinearNoTension(
                # Service: secant modulus, no tension, plateau at 0.85*fck
                elastic_modulus=Ecs,
                ultimate_strain=epsilon_cu2,
                compressive_strength=0.85 * fck,
            ),
            ultimate_stress_strain_profile=ssp.RectangularStressBlock(
                # ULS: rectangular block with fcd already embedding gamma_c
                compressive_strength=fcd,
                alpha=alpha_c,
                gamma=lambda_val,
                ultimate_strain=epsilon_cu2,
            ),
            flexural_tensile_strength=fctk_inf,
            colour=colour,
        )

    def create_steel_material(
        self,
        fy: float,
        colour: str = "firebrick",
    ) -> SteelBar:
        r"""Return a ``SteelBar`` material object calibrated to NBR 6118.

        Parameters
        ----------
        fy : float
            Characteristic yield strength [MPa].
            Typical values: 250 (CA-25), 500 (CA-50), 600 (CA-60).
        colour : str, optional
            Rendering colour. Defaults to ``"firebrick"``.

        Returns
        -------
        SteelBar
            Steel bar material object ready to use in a ``ConcreteSection``.

        Notes
        -----
        ``gamma_s`` is taken from ``self.gamma_s`` set at instantiation.

        Steel class is inferred from ``fy``:

        * CA-25: fy <= 250 MPa  |  Es = 210 000 MPa  |  esu = 20%
        * CA-50: fy <= 500 MPa  |  Es = 210 000 MPa  |  esu = 10%
        * CA-60: fy <= 600 MPa  |  Es = 210 000 MPa  |  esu = 6.7%

        Design yield strength: ``fyd = fy / gamma_s``

        The elastic modulus is ``Es = 210 000 MPa`` (NBR 6118 cl. 8.3.10).

        Raises
        ------
        ValueError
            If ``fy`` exceeds 600 MPa (not covered by NBR 6118).
        """
        if fy <= 0 or fy > 600:
            msg = "fy must be between 1 MPa and 600 MPa (NBR 6118 cl. 8.3.5)."
            raise ValueError(msg)

        Es = 210_000.0                                   # NBR 6118 cl. 8.3.10

        # ----------------------------------------------------------
        # Identify steel class and fracture strain  (NBR 7480 Tab. 4)
        # ----------------------------------------------------------
        if fy <= 250.0:
            steel_class = "CA-25"
            epsilon_su  = 0.20
        elif fy <= 500.0:
            steel_class = "CA-50"
            epsilon_su  = 0.10
        else:
            steel_class = "CA-60"
            epsilon_su  = 0.067

        fyd = fy / self.gamma_s

        name = (
            f"{steel_class} fy={fy:.0f} MPa (NBR 6118:2023) | "
            f"fyd={fyd:.1f} MPa"
        )

        return SteelBar(
            name=name,
            density=7.85e-6,
            stress_strain_profile=ssp.SteelElasticPlastic(
                yield_strength=fyd,                      # gamma_s already embedded
                elastic_modulus=Es,
                fracture_strain=epsilon_su,
            ),
            colour=colour,
        )

    # ------------------------------------------------------------------
    # Analysis methods (override DesignCode)
    # ------------------------------------------------------------------

    def ultimate_bending_capacity(
        self,
        theta: float = 0,
        n_design: float = 0,
    ) -> tuple[res.UltimateBendingResults, res.UltimateBendingResults, float]:
        r"""Calculate the ultimate bending capacity to NBR 6118.

        Because ``fcd`` and ``fyd`` are already embedded in the material
        definitions, the capacity reduction factor is identically 1.0.

        Parameters
        ----------
        theta : float
            Angle of neutral axis with horizontal [rad]. Defaults to 0.
        n_design : float
            Design axial force N* [N]. Defaults to 0.

        Returns
        -------
        tuple
            ``(factored_results, unfactored_results, phi=1.0)``
        """
        ult_res = self.concrete_section.ultimate_bending_capacity(
            theta=theta,
            n=n_design,
        )
        return ult_res, deepcopy(ult_res), 1.0

    def moment_interaction_diagram(
        self,
        theta: float = 0,
        limits: list[tuple[str, float]] | None = None,
        control_points: list[tuple[str, float]] | None = None,
        labels: list[str] | None = None,
        n_points: int = 24,
        n_spacing: int | None = None,
        progress_bar: bool = True,
    ) -> tuple[res.MomentInteractionResults, res.MomentInteractionResults, list[float]]:
        r"""Generate the design moment interaction diagram to NBR 6118.

        The diagram is produced directly in design space (Nd x Md)
        because ``fcd`` and ``fyd`` are embedded in the materials.
        phi = 1.0 for every point.

        Parameters
        ----------
        theta : float
            Angle of neutral axis [rad]. Defaults to 0.
        limits : list or None
            Start/end control points. Defaults to [("D",1.0),("N",0.0)].
        control_points : list or None
            Additional control points. Defaults to [("fy",1.0)].
        labels : list or None
            Labels for plotting.
        n_points : int
            Number of points. Defaults to 24.
        n_spacing : int or None
            Overrides n_points with equally spaced axial loads.
        progress_bar : bool
            Show progress bar. Defaults to True.

        Returns
        -------
        tuple
            ``(factored_results, unfactored_results, phis)``
        """
        if limits is None:
            limits = [("D", 1.0), ("N", 0.0)]
        if control_points is None:
            control_points = [("fy", 1.0)]

        mi_res = self.concrete_section.moment_interaction_diagram(
            theta=theta,
            limits=limits,
            control_points=control_points,
            labels=labels,
            n_points=n_points,
            n_spacing=n_spacing,
            progress_bar=progress_bar,
        )

        # phi = 1.0 everywhere — fcd and fyd already embedded in materials
        phis = [1.0] * len(mi_res.results)
        f_mi_res = deepcopy(mi_res)

        return f_mi_res, mi_res, phis

    def biaxial_bending_diagram(
        self,
        n_design: float = 0,
        n_points: int = 48,
        progress_bar: bool = True,
    ) -> tuple[res.BiaxialBendingResults, list[float]]:
        """Generate the biaxial bending diagram to NBR 6118.

        Parameters
        ----------
        n_design : float
            Design axial force [N]. Defaults to 0.
        n_points : int
            Angular calculation points. Defaults to 48.
        progress_bar : bool
            Show progress bar. Defaults to True.

        Returns
        -------
        tuple
            ``(factored_results, phis)`` where all phis are 1.0.
        """
        bb_res = res.BiaxialBendingResults(
            default_units=self.concrete_section.default_units,
            n=n_design,
        )
        phis = []
        d_theta = 2 * np.pi / n_points
        theta_list = np.linspace(
            start=-np.pi,
            stop=np.pi - d_theta,
            num=n_points,
        )

        for theta in theta_list:
            f_ult_res, _, phi = self.ultimate_bending_capacity(
                theta=theta,
                n_design=n_design,
            )
            bb_res.results.append(f_ult_res)
            phis.append(phi)

        # Close the curve
        bb_res.results.append(bb_res.results[0])
        phis.append(phis[0])

        return bb_res, phis

    def capacity_reduction_factor(self, *args, **kwargs) -> float:
        """Return 1.0 — gamma_c and gamma_s are embedded in the materials.

        The NBR 6118 approach applies partial safety factors at the
        material level (fcd = fck/gamma_c; fyd = fy/gamma_s). There is
        no post-calculation reduction factor as in AS3600 or ACI 318.
        """
        return 1.0