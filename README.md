# Cardozo

> **Estado atual: protótipo em desenvolvimento. A ferramenta ainda não foi amplamente testada e não deve ser utilizada como único instrumento de verificação estrutural sem validação independente dos resultados.**

Software computacional para geração automática da superfície de resistência a flexão composta oblíqua de seções transversais arbitrárias de concreto armado, a partir de arquivos DXF.

---

## Motivação

![Catedral de Brasília](https://upload.wikimedia.org/wikipedia/commons/thumb/1/1e/Catedral_de_Brasilia_aerea.jpg/1280px-Catedral_de_Brasilia_aerea.jpg)
*Catedral Metropolitana de Brasília — Oscar Niemeyer, cálculo estrutural de Joaquim Cardozo. Os 16 pilares com seção transversal parabólica e perfil hiperbólico representam o problema central que motivou o desenvolvimento desta ferramenta. Foto: Wikimedia Commons.*

A verificação estrutural de pilares com geometria não convencional exige a construção da superfície de resistência completa no espaço `N–Mx–My`. Essa superfície define, para cada nível de força normal, o conjunto de combinações de momentos fletores que a seção consegue suportar no estado limite último.

Na prática, porém, **a esmagadora maioria dos softwares disponíveis — livres ou comerciais — só oferece suporte direto a seções padronizadas**: retangulares, circulares, em I, T, L ou similares. Quando o usuário precisa trabalhar com uma geometria arbitrária, as alternativas típicas são:

- inserir manualmente as coordenadas de todos os vértices do contorno e de cada barra de armadura em formulários de entrada de dados;
- recorrer a scripts numéricos desenvolvidos caso a caso;
- simplificar a geometria real para uma forma padrão, perdendo fidelidade ao modelo.

Nenhuma dessas abordagens é adequada quando a geometria já existe como desenho CAD e o que se quer é aproveitá-la diretamente na análise estrutural.

O **Cardozo** resolve esse problema: o usuário exporta a seção transversal do AutoCAD (ou qualquer software CAD compatível) como arquivo DXF, e a ferramenta constrói automaticamente a superfície de resistência correspondente, aplicando os modelos constitutivos da NBR 6118.

O nome é uma homenagem ao engenheiro **Joaquim Cardozo**, responsável pelo cálculo estrutural da Catedral de Brasília e figura central na engenharia estrutural brasileira — colaborador fundamental nas obras de Oscar Niemeyer.

---

## O que o Cardozo faz

A entrada é um arquivo DXF. A saída é o diagrama de interação biaxial `N–Mx–My`.

Entre esses dois pontos, o Cardozo:

1. Lê os contornos de concreto e as barras de armadura diretamente do DXF.
2. Identifica automaticamente o contorno externo e os vazios internos.
3. Constrói a seção armada como objeto computacional usando `shapely`, `sectionproperties` e `concreteproperties`.
4. Cria os materiais de concreto e aço segundo a NBR 6118:2023, a partir apenas de `fck` e `fy`.
5. Executa a integração numérica da seção por varredura angular da linha neutra.
6. Apresenta os diagramas de interação para avaliação da capacidade resistente.

Isso elimina a etapa de relançamento manual da geometria, que é a principal barreira ao uso de ferramentas de análise seccional em projetos com formas não convencionais.

---

## Contexto técnico

O desenvolvimento do Cardozo foi motivado por necessidades de diagnóstico estrutural da Catedral de Brasília, em contexto associado aos professores doutores Marco Aurelio Souza Bessa, Lenildo Santos da Silva e José Humberto Matias de Paula.

A estrutura da catedral é formada por 16 colunas curvas com perfil hiperbólico e seção transversal parabólica — colunas que afinam na base dando a impressão de que tocam de leve o chão. Essas seções não se enquadram em nenhuma forma padronizada suportada pelos métodos simplificados usuais, o que torna a análise seccional rigorosa especialmente relevante nesse contexto.

---

## Aviso sobre o estado do software

O Cardozo é um **protótipo de pesquisa**. Isso significa:

- A implementação ainda não foi amplamente validada contra casos de referência publicados.
- Podem existir inconsistências entre o modelo computacional e as prescrições normativas em situações específicas.
- A interface e a estrutura do código estão sujeitas a alterações sem aviso prévio.
- **Os resultados não devem ser utilizados como única base de verificação estrutural sem validação independente.**

Contribuições, identificação de erros e comparações com resultados de referência são bem-vindas.

---

## Implementação da NBR 6118

A biblioteca `concreteproperties` não possui originalmente suporte à norma brasileira. O Cardozo implementa o módulo `src/cardozo/backend/nbr6118.py`, que define a classe `NBR6118` derivada da classe base `DesignCode` da biblioteca.

O usuário fornece apenas `fck` e `fy`. A classe deriva automaticamente:

**Concreto (C20 a C90)**

| Parâmetro | fck ≤ 50 MPa | fck > 50 MPa |
|---|---|---|
| `epsilon_cu2` | 3,5 ‰ | `2,6 + 35·((90−fck)/100)⁴` ‰ |
| `alpha_c` | 0,85 | `0,85·(1−(fck−50)/200)` |
| `lambda` | 0,80 | `0,80−(fck−50)/400` |
| `Eci` | `5600·√fck` | `5600·√fck` |
| `fctm` | `0,3·fck^(2/3)` | `2,12·ln(1+fck/10)` |

**Aço (inferido por `fy`)**

| Classe | fy | Es | εsu |
|---|---|---|---|
| CA-25 | ≤ 250 MPa | 210 000 MPa | 20 % |
| CA-50 | ≤ 500 MPa | 210 000 MPa | 10 % |
| CA-60 | ≤ 600 MPa | 210 000 MPa | 6,7 % |

Os coeficientes `gamma_c` e `gamma_s` são definidos na instanciação da classe e embutidos diretamente nas resistências de cálculo (`fcd`, `fyd`). O diagrama de interação gerado já é o diagrama de projeto — não há fator de redução aplicado posteriormente.

---

## Formato do arquivo DXF

O arquivo deve conter:

- Camada `concrete`: polilinhas fechadas (`LWPOLYLINE`) representando os contornos da seção. O maior contorno é tratado como limite externo; os demais são interpretados como vazios.
- Camada `steel bars`: círculos (`CIRCLE`) representando as barras de armadura. O raio do círculo define a área equivalente da barra.

Mais detalhes em [docs/dxf_specs.md](docs/dxf_specs.md).

---

## Estrutura do projeto

```text
Cardozo/
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
```

---

## Instalação

```bash
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
# ou: .venv\Scripts\activate  (Windows)
pip install -r requirements.txt
```

## Execução

```bash
# Linux
PYTHONPATH=src python -m cardozo.main
# ou: scripts/run_dev.sh

# Windows
scripts\run_dev.bat
```

## Testes

```bash
PYTHONPATH=src python -m unittest discover -s tests
```

## Geração do executável Windows

```bat
pip install -r requirements.txt
pip install -r requirements-build.txt
scripts\build_exe.bat
```

O executável será gerado em `dist/Cardozo/Cardozo.exe`. Para distribuição via GitHub Releases, consulte [docs/windows_release_github_actions.md](docs/windows_release_github_actions.md).

---

## Hipóteses de engenharia

- Seções planas permanecem planas após a deformação (hipótese de Bernoulli).
- Aderência perfeita entre aço e concreto.
- Resistência à tração do concreto desprezada no estado limite último.
- Os esforços solicitantes devem ser fornecidos já considerando os efeitos globais e locais aplicáveis (efeitos de 2ª ordem, imperfeições geométricas, etc.).
- A validade dos resultados depende da qualidade da geometria importada, da discretização adotada e da correta escolha dos parâmetros normativos.

---

## Autor

Tarso Bessa — bessatarso@gmail.com
