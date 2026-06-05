<!-- keywords: biaxial bending, oblique bending, reinforced concrete, arbitrary cross-section, interaction diagram, N-Mx-My surface, structural analysis, DXF, NBR 6118, concreto armado, flexão oblíqua, seção arbitrária, diagrama de interação, cálculo estrutural, engenharia computacional, computational structural engineering, concrete column, moment interaction, cross-section analysis -->
Cardozo

⚠️ Estado atual / Current status: prototype — not yet widely tested.
Esta ferramenta é um protótipo de pesquisa e ainda não foi amplamente validada. Os resultados não devem ser utilizados como única base de verificação estrutural sem validação independente. / This tool is a research prototype and has not been widely validated. Results must not be used as the sole basis for structural verification without independent validation.


English version below

Cardozo — Português
Software computacional para geração automática da superfície de resistência a flexão composta oblíqua (N–Mx–My) de seções transversais arbitrárias de concreto armado, a partir de arquivos DXF.

Motivação
Mostrar Imagem
Catedral Metropolitana de Brasília — Oscar Niemeyer, cálculo estrutural de Joaquim Cardozo. Os 16 pilares com seção transversal parabólica e perfil hiperbólico representam o problema central que motivou o desenvolvimento desta ferramenta. Foto: Wikimedia Commons.
A verificação estrutural de pilares com geometria não convencional exige a construção da superfície de resistência completa no espaço N–Mx–My. Essa superfície define, para cada nível de força normal, o conjunto de combinações de momentos fletores que a seção consegue suportar no estado limite último.
Na prática, porém, a esmagadora maioria dos softwares disponíveis — livres ou comerciais — só oferece suporte direto a seções padronizadas: retangulares, circulares, em I, T, L ou similares. Quando o usuário precisa trabalhar com uma geometria arbitrária, as alternativas típicas são:

inserir manualmente as coordenadas de todos os vértices do contorno e de cada barra de armadura em formulários de entrada de dados;
recorrer a scripts numéricos desenvolvidos caso a caso;
simplificar a geometria real para uma forma padrão, perdendo fidelidade ao modelo.

Nenhuma dessas abordagens é adequada quando a geometria já existe como desenho CAD e o que se quer é aproveitá-la diretamente na análise estrutural.
O Cardozo resolve esse problema: o usuário exporta a seção transversal do AutoCAD (ou qualquer software CAD compatível) como arquivo DXF, e a ferramenta constrói automaticamente a superfície de resistência correspondente, aplicando os modelos constitutivos da NBR 6118.
O nome é uma homenagem ao engenheiro Joaquim Cardozo, responsável pelo cálculo estrutural da Catedral de Brasília e figura central na engenharia estrutural brasileira — colaborador fundamental nas obras de Oscar Niemeyer.

O que o Cardozo faz
A entrada é um arquivo DXF. A saída é o diagrama de interação biaxial N–Mx–My.
Entre esses dois pontos, o Cardozo:

Lê os contornos de concreto e as barras de armadura diretamente do DXF.
Identifica automaticamente o contorno externo e os vazios internos.
Constrói a seção armada como objeto computacional usando shapely, sectionproperties e concreteproperties.
Cria os materiais de concreto e aço segundo a NBR 6118:2023, a partir apenas de fck e fy.
Executa a integração numérica da seção por varredura angular da linha neutra.
Apresenta os diagramas de interação para avaliação da capacidade resistente.

Isso elimina a etapa de relançamento manual da geometria, que é a principal barreira ao uso de ferramentas de análise seccional em projetos com formas não convencionais.

Contexto técnico
O desenvolvimento do Cardozo foi motivado por necessidades de diagnóstico estrutural da Catedral de Brasília, em contexto associado aos professores doutores Marco Aurelio Souza Bessa, Lenildo Santos da Silva e José Humberto Matias de Paula.
A estrutura da catedral é formada por 16 colunas curvas com perfil hiperbólico e seção transversal parabólica — colunas que afinam na base dando a impressão de que tocam de leve o chão. Essas seções não se enquadram em nenhuma forma padronizada suportada pelos métodos simplificados usuais, o que torna a análise seccional rigorosa especialmente relevante nesse contexto.

Aviso sobre o estado do software
O Cardozo é um protótipo de pesquisa. Isso significa:

A implementação ainda não foi amplamente validada contra casos de referência publicados.
Podem existir inconsistências entre o modelo computacional e as prescrições normativas em situações específicas.
A interface e a estrutura do código estão sujeitas a alterações sem aviso prévio.
Os resultados não devem ser utilizados como única base de verificação estrutural sem validação independente.

Contribuições, identificação de erros e comparações com resultados de referência são bem-vindas.

Implementação da NBR 6118
A biblioteca concreteproperties não possui originalmente suporte à norma brasileira. O Cardozo implementa o módulo src/cardozo/backend/nbr6118.py, que define a classe NBR6118 derivada da classe base DesignCode da biblioteca.
O usuário fornece apenas fck e fy. Os coeficientes γ꜀ e γₛ são definidos na instanciação da classe. A classe deriva automaticamente:
Concreto (C20 a C90)
Parâmetrofck ≤ 50 MPafck > 50 MPaε꜀ᵤ₂3,5 ‰(2,6 + 35·((90−fck)/100)⁴) ‰α꜀0,850,85·(1−(fck−50)/200)λ0,800,80−(fck−50)/400Eci5600·√fck MPa5600·√fck MPafctm0,3·fck^(2/3)2,12·ln(1+fck/10)fcdα꜀·fck / γ꜀α꜀·fck / γ꜀
Aço (inferido por fy)
ClassefyEsεsuCA-25≤ 250 MPa210 000 MPa20 %CA-50≤ 500 MPa210 000 MPa10 %CA-60≤ 600 MPa210 000 MPa6,7 %
γ꜀ e γₛ são embutidos diretamente nas resistências de cálculo (fcd, fyd). O diagrama de interação gerado já é o diagrama de projeto — não há fator de redução global aplicado posteriormente.

Formato do arquivo DXF
O arquivo deve conter:

Camada concrete: polilinhas fechadas (LWPOLYLINE) representando os contornos da seção. O maior contorno é tratado como limite externo; os demais são interpretados como vazios.
Camada steel bars: círculos (CIRCLE) representando as barras de armadura. O raio do círculo define a área equivalente da barra.

Mais detalhes em docs/dxf_specs.md.

Estrutura do projeto
textCardozo/
├── README.md
├── requirements.txt
├── requirements-build.txt
├── pyproject.toml
├── Cardozo.spec
├── docs/
│   ├── dxf_specs.md
│   └── windows_release_github_actions.md
├── examples/
│   └── dxf_files/
├── scripts/
│   ├── build_exe.bat
│   ├── run_dev.bat
│   └── run_dev.sh
├── src/
│   └── cardozo/
│       ├── main.py
│       ├── backend/
│       │   ├── dxf_parser.py
│       │   ├── geometry_builder.py
│       │   └── nbr6118.py
│       └── frontend/
│           └── app_window.py
└── tests/

Instalação
bashpython -m venv .venv
source .venv/bin/activate      # Linux/macOS
# ou: .venv\Scripts\activate   (Windows)
pip install -r requirements.txt
Execução
bash# Linux
PYTHONPATH=src python -m cardozo.main
# ou: scripts/run_dev.sh

# Windows
scripts\run_dev.bat
Geração do executável Windows
batpip install -r requirements.txt
pip install -r requirements-build.txt
scripts\build_exe.bat
O executável será gerado em dist/Cardozo/Cardozo.exe. Para distribuição via GitHub Releases, consulte docs/windows_release_github_actions.md.

Hipóteses de engenharia

Seções planas permanecem planas após a deformação (hipótese de Bernoulli).
Aderência perfeita entre aço e concreto.
Resistência à tração do concreto desprezada no estado limite último.
Os esforços solicitantes devem ser fornecidos já considerando os efeitos globais e locais aplicáveis (efeitos de 2ª ordem, imperfeições geométricas, etc.).
A validade dos resultados depende da qualidade da geometria importada, da discretização adotada e da correta escolha dos parâmetros normativos.


Futuras melhorias

Discretização configurável pelo usuário: permitir que o nível de refinamento da malha da seção seja definido diretamente na interface, com controle sobre o número de elementos e a tolerância geométrica.
Suite de testes automatizados: implementação de casos de referência extraídos de livros-texto consagrados (Fusco, Montoya, MacGregor) e de normas técnicas, com verificação automática dos resultados contra valores publicados.
Biblioteca de exemplos verificados: conjunto de seções com geometria, armadura, parâmetros de material e resultados esperados documentados — tanto de casos acadêmicos quanto de casos reais de estruturas existentes.
Suporte a outras normas: extensão do módulo de materiais para ACI 318 e Eurocode 2, permitindo comparação direta entre normas para a mesma seção.
Exportação de resultados: geração de relatório em PDF com geometria, parâmetros de material e diagramas de interação.


Autor
Tarso Bessa — bessatarso@gmail.com


Cardozo (English)
Computational tool for automatic generation of the biaxial bending resistance surface (N–Mx–My) for arbitrary reinforced concrete cross-sections, from DXF files.

Motivation
Mostrar Imagem
Cathedral of Brasília — Oscar Niemeyer, structural engineering by Joaquim Cardozo. The 16 columns with parabolic cross-section and hyperbolic profile represent the structural problem that motivated this tool. Photo: Wikimedia Commons.
Structural verification of columns with non-conventional geometry requires constructing the full resistance surface in the N–Mx–My space. This surface defines, for each level of axial force, the set of biaxial bending moment combinations the section can sustain at the ultimate limit state.
In practice, however, the vast majority of available software — free or commercial — only supports standard cross-section shapes directly: rectangular, circular, I, T, L, and similar. When working with arbitrary geometry, the typical alternatives are:

manually entering the coordinates of every vertex of the cross-section boundary and every reinforcement bar;
writing case-by-case numerical scripts;
simplifying the real geometry to a standard shape, losing fidelity to the actual structure.

None of these alternatives is adequate when the geometry already exists as a CAD drawing and the goal is to use it directly for structural analysis.
Cardozo solves this problem: the user exports the cross-section from AutoCAD (or any compatible CAD software) as a DXF file, and the tool automatically builds the corresponding resistance surface, applying the constitutive models of NBR 6118.
The name is a tribute to engineer Joaquim Cardozo, responsible for the structural calculations of the Cathedral of Brasília and a central figure in Brazilian structural engineering — a fundamental collaborator in Oscar Niemeyer's works.

What Cardozo does
The input is a DXF file. The output is the biaxial interaction diagram N–Mx–My.
Between these two points, Cardozo:

Reads concrete boundaries and reinforcement bars directly from the DXF.
Automatically identifies the outer boundary and internal voids.
Builds the reinforced section as a computational object using shapely, sectionproperties, and concreteproperties.
Creates concrete and steel materials according to NBR 6118:2023, from fck and fy alone.
Performs numerical integration of the section by angular sweep of the neutral axis.
Presents the interaction diagrams for assessment of the section's load-carrying capacity.

This eliminates the manual geometry re-entry step, which is the main barrier to using sectional analysis tools in projects with non-conventional shapes.

Technical context
The development of Cardozo was motivated by the structural assessment of the Cathedral of Brasília, in a research context involving professors Marco Aurelio Souza Bessa, Lenildo Santos da Silva, and José Humberto Matias de Paula.
The cathedral's structure consists of 16 curved columns with a hyperbolic profile and parabolic cross-section — columns that taper at the base, giving the impression of barely touching the ground. These sections do not fit into any standard shape supported by conventional simplified methods, making rigorous sectional analysis especially relevant in this context.

Software status
Cardozo is a research prototype. This means:

The implementation has not yet been widely validated against published reference cases.
Inconsistencies between the computational model and the normative prescriptions may exist for specific situations.
The interface and code structure are subject to change without notice.
Results must not be used as the sole basis for structural verification without independent validation.

Contributions, bug reports, and comparisons against reference results are welcome.

NBR 6118 implementation
The concreteproperties library does not natively support the Brazilian standard. Cardozo implements src/cardozo/backend/nbr6118.py, which defines the NBR6118 class derived from the library's DesignCode base class.
The user provides only fck and fy. The partial safety factors γ꜀ and γₛ are set at class instantiation. All other parameters are derived automatically:
Concrete (C20 to C90)
Parameterfck ≤ 50 MPafck > 50 MPaε꜀ᵤ₂3.5 ‰(2.6 + 35·((90−fck)/100)⁴) ‰α꜀0.850.85·(1−(fck−50)/200)λ0.800.80−(fck−50)/400Eci5600·√fck MPa5600·√fck MPafctm0.3·fck^(2/3)2.12·ln(1+fck/10)fcdα꜀·fck / γ꜀α꜀·fck / γ꜀
Steel (inferred from fy)
ClassfyEsεsuCA-25≤ 250 MPa210,000 MPa20%CA-50≤ 500 MPa210,000 MPa10%CA-60≤ 600 MPa210,000 MPa6.7%
γ꜀ and γₛ are embedded directly into the design resistances (fcd, fyd). The resulting interaction diagram is already in design space — no global reduction factor is applied afterwards.

DXF file format
The file must contain:

Layer concrete: closed polylines (LWPOLYLINE) representing the section boundaries. The largest closed contour is treated as the outer boundary; all others are treated as internal voids.
Layer steel bars: circles (CIRCLE) representing the reinforcement bars. The circle radius defines the equivalent bar area.

See docs/dxf_specs.md for full specifications.

Project structure
textCardozo/
├── README.md
├── requirements.txt
├── requirements-build.txt
├── pyproject.toml
├── Cardozo.spec
├── docs/
│   ├── dxf_specs.md
│   └── windows_release_github_actions.md
├── examples/
│   └── dxf_files/
├── scripts/
│   ├── build_exe.bat
│   ├── run_dev.bat
│   └── run_dev.sh
├── src/
│   └── cardozo/
│       ├── main.py
│       ├── backend/
│       │   ├── dxf_parser.py
│       │   ├── geometry_builder.py
│       │   └── nbr6118.py
│       └── frontend/
│           └── app_window.py
└── tests/

Installation
bashpython -m venv .venv
source .venv/bin/activate      # Linux/macOS
# or: .venv\Scripts\activate   (Windows)
pip install -r requirements.txt
Running
bash# Linux
PYTHONPATH=src python -m cardozo.main
# or: scripts/run_dev.sh

# Windows
scripts\run_dev.bat
Building the Windows executable
batpip install -r requirements.txt
pip install -r requirements-build.txt
scripts\build_exe.bat
The executable will be generated at dist/Cardozo/Cardozo.exe. For distribution via GitHub Releases, see docs/windows_release_github_actions.md.

Engineering assumptions

Plane sections remain plane after deformation (Bernoulli–Navier hypothesis).
Perfect bond between steel and concrete.
Concrete tensile strength neglected at the ultimate limit state.
Applied forces must already account for global and local effects (second-order effects, geometric imperfections, etc.).
The validity of results depends on the quality of the imported geometry, the mesh discretization, and the correct choice of normative parameters.


Future work

User-configurable mesh discretization: allow the section mesh refinement level to be set directly in the interface, with control over element count and geometric tolerance.
Automated test suite: implementation of reference cases drawn from established textbooks (Fusco, Montoya, MacGregor) and technical standards, with automatic verification of computed results against published values.
Verified example library: a curated set of sections with documented geometry, reinforcement layout, material parameters, and expected results — covering both academic examples and real structures.
Additional design codes: extension of the materials module to ACI 318 and Eurocode 2, enabling direct cross-code comparison for the same section.
Result export: generation of a PDF report containing section geometry, material parameters, and interaction diagrams.


Author
Tarso Bessa — bessatarso@gmail.com
