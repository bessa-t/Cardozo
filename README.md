# Cardozo

Software computacional para analise de secoes de concreto armado submetidas a flexao composta obliqua.

O Cardozo gera diagramas de interacao biaxial (`N-Mx-My`) para secoes transversais arbitrarias de concreto armado a partir de arquivos DXF. A ferramenta foi desenvolvida para apoiar a analise de pilares com geometrias nao convencionais, especialmente quando os metodos simplificados usuais deixam de representar adequadamente a forma real da secao.

## Motivacao

A motivacao inicial do projeto esta associada ao estudo dos pilares da Catedral de Brasilia, que possuem geometrias estruturais singulares, secoes transversais nao convencionais e comportamento espacial associado aos pilares hiperbolicos da obra.

Nesses casos, a verificacao estrutural demanda uma ferramenta capaz de:

- importar geometrias reais de CAD;
- representar secoes arbitrarias, incluindo vazios;
- posicionar armaduras individualmente;
- aplicar modelos constitutivos compativeis com a NBR 6118;
- gerar superficies ou diagramas de resistencia para diferentes combinacoes de esforcos normais e momentos fletores.

O nome Cardozo e uma homenagem ao engenheiro Joaquim Cardozo, figura central na engenharia estrutural brasileira e colaborador fundamental nas obras de Oscar Niemeyer, incluindo a Catedral de Brasilia.

## Contexto tecnico e validade

O desenvolvimento do Cardozo foi orientado por necessidades de diagnostico estrutural da Catedral de Brasilia, em contexto tecnico associado aos professores PhDs Marco Aurelio Souza Bessa, Lenildo Santos da Silva e Jose Humberto Matias de Paula.

A ferramenta deve ser entendida como um apoio computacional para analise, verificacao e diagnostico de secoes de concreto armado com geometria arbitraria. Os resultados dependem da correta definicao da geometria, das armaduras, dos materiais, dos coeficientes de seguranca e das hipoteses normativas adotadas.

## Metodologia

O fluxo de calculo adotado pelo Cardozo segue as seguintes etapas:

1. O usuario prepara um arquivo DXF contendo a geometria da secao transversal.
2. O parser DXF identifica os contornos de concreto e as barras de armadura.
3. A geometria e convertida para objetos geometricos computacionais usando `shapely`, `sectionproperties` e `concreteproperties`.
4. O contorno de maior area e tratado como secao principal de concreto.
5. Os demais contornos sao tratados como vazios internos.
6. As barras de aco sao inseridas individualmente na secao com area equivalente ao raio lido no DXF.
7. Os materiais de concreto e aco sao criados segundo parametros da NBR 6118.
8. A biblioteca `concreteproperties` executa a integracao numerica da secao e gera os resultados de resistencia.
9. O Cardozo apresenta os diagramas de interacao para avaliacao da capacidade resistente.

Essa abordagem permite trabalhar com secoes nao retangulares, vazadas, assimetricas ou compostas por formas que nao se enquadram diretamente em solucoes manuais simplificadas.

## Uso da biblioteca concreteproperties

O Cardozo utiliza a biblioteca `concreteproperties` como nucleo numerico para analise de secoes de concreto armado.

A biblioteca fornece recursos robustos para:

- representar secoes de concreto armado;
- combinar geometrias de concreto e barras de aco;
- calcular capacidade resistente a flexao composta;
- gerar diagramas de interacao momento-normal;
- avaliar flexao biaxial por varredura angular da linha neutra.

No Cardozo, a construcao da secao e feita em `src/cardozo/backend/geometry_builder.py`. Esse modulo atua como ponte entre o DXF interpretado e os objetos esperados por `concreteproperties`.

O processo consiste em:

- ler os poligonos de concreto extraidos do DXF;
- identificar o poligono externo principal;
- subtrair furos ou vazios;
- adicionar barras de armadura com `add_bar`;
- criar uma instancia final de `ConcreteSection`.

## Implementacao da NBR 6118

A biblioteca `concreteproperties` ja possui suporte para alguns codigos normativos internacionais, como normas australianas. Entretanto, ela nao possui originalmente uma classe de dimensionamento especifica para a norma brasileira NBR 6118.

Por esse motivo, o projeto implementa o modulo:

```text
src/cardozo/backend/nbr6118.py
```

Esse modulo define a classe `NBR6118`, derivada da classe base `DesignCode` da propria `concreteproperties`.

A implementacao adapta o fluxo da biblioteca para o contexto brasileiro:

- cria materiais de concreto com parametros derivados da NBR 6118:2023;
- considera concretos de C20 a C90;
- calcula `Eci`, `Ecs`, `fctm`, `fctk_inf`, `fcd`, `alpha_c`, `lambda`, `epsilon_c2` e `epsilon_cu2`;
- cria materiais de aco CA-25, CA-50 e CA-60;
- aplica `gamma_c` e `gamma_s` diretamente nas resistencias de projeto dos materiais;
- retorna fator de reducao `phi = 1.0`, pois a reducao normativa ja esta embutida em `fcd` e `fyd`;
- gera diagramas de interacao ja no espaco de projeto (`Nd`, `Md`).

Essa decisao evita aplicar um fator global posterior, como ocorre em algumas normas internacionais, e segue a logica de coeficientes parciais de seguranca adotada pela NBR 6118.

## Funcionalidades

- Leitura de arquivos DXF com contornos de concreto e barras de aco.
- Suporte a secoes arbitrarias com vazios internos.
- Criacao automatica de secoes de concreto armado para `concreteproperties`.
- Implementacao de materiais segundo a NBR 6118:2023.
- Interface desktop com CustomTkinter.
- Visualizacao da geometria importada.
- Geracao de diagramas de interacao para flexao composta.
- Suporte ao empacotamento como executavel Windows com PyInstaller.

## Facilidade de execucao

O Cardozo foi estruturado para permitir uso direto por pesquisadores, engenheiros e estudantes sem exigir a montagem manual de modelos numericos em scripts.

A interface desktop concentra o fluxo principal:

- selecao dos materiais;
- carregamento do arquivo DXF;
- visualizacao da secao importada;
- montagem automatica da secao de concreto armado;
- execucao da analise;
- visualizacao dos diagramas de interacao.

Para desenvolvimento, o projeto pode ser executado diretamente em Python. Para distribuicao, pode ser empacotado como executavel Windows, permitindo que usuarios finais executem a ferramenta sem configurar manualmente o ambiente Python.

## Formato do arquivo DXF

O arquivo DXF deve conter camadas com os seguintes nomes:

- `concrete`: polilinhas fechadas (`LWPOLYLINE`) representando os contornos de concreto.
- `steel bars`: circulos (`CIRCLE`) representando as barras de armadura.

O maior contorno fechado da camada `concrete` e interpretado como o limite externo da secao. Os demais contornos sao interpretados como vazios.

Mais detalhes estao em [docs/dxf_specs.md](docs/dxf_specs.md).

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

## Instalacao

Crie e ative um ambiente virtual:

```bash
python -m venv .venv
source .venv/bin/activate
```

Instale as dependencias:

```bash
pip install -r requirements.txt
```

No Windows:

```bat
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Execucao

No Linux, a partir da raiz do projeto:

```bash
PYTHONPATH=src python -m cardozo.main
```

Ou use o script:

```bash
scripts/run_dev.sh
```

No Windows:

```bat
scripts\run_dev.bat
```

## Testes

Execute:

```bash
PYTHONPATH=src python -m unittest discover -s tests
```

## Geracao do executavel Windows

O projeto usa PyInstaller com o arquivo `Cardozo.spec`.

Em um ambiente Windows:

```bat
pip install -r requirements.txt
pip install -r requirements-build.txt
scripts\build_exe.bat
```

O executavel sera gerado em:

```text
dist/Cardozo/Cardozo.exe
```

Para distribuicao profissional usando GitHub Actions e GitHub Releases, consulte:

[docs/windows_release_github_actions.md](docs/windows_release_github_actions.md)

## Hipoteses de engenharia

- As secoes planas permanecem planas apos a deformacao.
- A aderencia entre aco e concreto e perfeita.
- A resistencia a tracao do concreto e desprezada no estado limite ultimo.
- Os esforcos solicitantes devem ser fornecidos ja considerando os efeitos globais e locais aplicaveis.
- A validade dos resultados depende da discretizacao, da qualidade da geometria importada e da correta escolha dos parametros normativos.

## Autor

Tarso Bessa  
bessatarso@gmail.com
