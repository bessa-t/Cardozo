# Estrutura da pasta `src`

Este documento resume como o codigo dentro de `src/` esta organizado e como os modulos principais se conectam.

## Visao geral

O projeto usa layout `src`, ou seja, o pacote Python principal fica em:

```text
src/cardozo/
```

O pacote se chama `cardozo`. Para executar o app em desenvolvimento, o `PYTHONPATH` precisa apontar para `src`, como ja fazem os scripts em `scripts/`.

```bash
PYTHONPATH=src python -m cardozo.main
```

## Arvore principal

```text
src/
└── cardozo/
    ├── __init__.py
    ├── main.py
    ├── backend/
    │   ├── __init__.py
    │   ├── dxf_parser.py
    │   └── geometry_builder.py
    ├── data/
    │   ├── __init__.py
    │   ├── nbr6118.py
    │   └── std_materials.py
    └── frontend/
        ├── __init__.py
        └── app_window.py
```

## Responsabilidades por pacote

### `cardozo.main`

Arquivo de entrada da aplicacao.

Responsabilidades:

- Configura o caminho de importacao quando necessario.
- Define tema visual do `customtkinter`.
- Importa `App` de `cardozo.frontend.app_window`.
- Cria a janela principal e inicia o loop da interface com `app.mainloop()`.

Este modulo nao deve conter regra de negocio estrutural. Ele deve continuar sendo apenas o inicializador da aplicacao.

### `cardozo.frontend`

Contem a interface grafica.

Arquivo principal:

```text
src/cardozo/frontend/app_window.py
```

Responsabilidades:

- Montar a janela principal com `CustomTkinter`.
- Controlar os campos de entrada: material, forca normal e arquivo DXF.
- Controlar idioma da interface: ingles e portugues.
- Abrir o seletor de arquivo DXF.
- Chamar o backend quando o usuario executa a analise.
- Exibir a previa da geometria e o diagrama usando `matplotlib`.

Fluxo interno mais importante:

```text
App.calculate_event()
    -> le entradas da UI
    -> valida arquivo e forca normal
    -> cria DXFParser
    -> cria GeometryBuilder
    -> busca materiais em CONCRETE_LIBRARY e STEEL_LIBRARY
    -> parser.parse()
    -> builder.build_section(...)
    -> section.plot_section(...)
    -> section.biaxial_bending_diagram(...)
    -> results.plot_diagram(...)
```

O frontend conhece o backend, mas o backend nao deve conhecer a interface grafica.

### `cardozo.backend`

Contem a logica de leitura e transformacao da geometria.

#### `dxf_parser.py`

Responsavel por ler arquivos DXF com `ezdxf` e extrair apenas os elementos estruturais relevantes.

Entidades esperadas:

- Concreto: `LWPOLYLINE` fechada na layer `concrete`.
- Barras de aco: `CIRCLE` na layer `steel bars`.

Principais tipos:

- `ParsedSteelBar`: dataclass com `center` e `radius`.
- `ParsedGeometry`: dataclass com `concrete_polygons` e `steel_bars`.
- `DXFParser`: classe que abre o arquivo DXF e retorna `ParsedGeometry`.

Validacoes importantes:

- Polilinha de concreto precisa ser fechada.
- Barras de aco precisam ser circulos.
- Circulos na layer de concreto geram erro.
- Polylines na layer de aco geram erro.
- O arquivo precisa ter ao menos uma geometria de concreto.
- Atualmente suporta uma secao simples ou uma secao vazada com ate 2 poligonos de concreto.

#### `geometry_builder.py`

Responsavel por transformar o resultado do parser em objetos das bibliotecas de analise.

Bibliotecas usadas:

- `shapely`: cria e manipula poligonos.
- `sectionproperties`: cria `Geometry`.
- `concreteproperties`: cria `ConcreteSection` e adiciona barras.

Fluxo:

```text
ParsedGeometry
    -> Shapely Polygon
    -> identifica maior poligono como contorno externo
    -> trata os demais poligonos como vazios
    -> cria Geometry com material de concreto
    -> subtrai vazios
    -> adiciona barras de aco com add_bar(...)
    -> retorna ConcreteSection
```

O metodo publico principal e:

```python
GeometryBuilder.build_section(raw_data, concrete_material, steel_material)
```

Ele recebe dados ja parseados e materiais prontos, e devolve uma `ConcreteSection`.

### `cardozo.data`

Contem dados tecnicos usados pela analise.

#### `std_materials.py`

Define materiais padrao conforme NBR 6118 para uso na interface e no calculo.

Exporta:

- `CONCRETE_LIBRARY`: dicionario de classes de concreto.
- `STEEL_LIBRARY`: dicionario de tipos de aco.

Esses dicionarios sao usados pelo frontend para preencher os menus e pelo backend como objetos reais de material.

Exemplos de chaves:

- `C20 (NBR 6118)`
- `C30 (NBR 6118)`
- `CA-50 (500 MPa)`
- `CA-60 (600 MPa)`

#### `nbr6118.py`

Arquivo reservado para regras ou funcoes relacionadas a NBR 6118.

No estado atual, ele esta vazio. Se futuramente houver calculos normativos reutilizaveis, este e um bom lugar para concentra-los, desde que nao sejam apenas definicoes de materiais ja cobertas por `std_materials.py`.

## Fluxo de dados da aplicacao

```text
Usuario
  seleciona material, forca normal e DXF
        |
        v
frontend/app_window.py
  valida entrada e coordena a analise
        |
        v
backend/dxf_parser.py
  le DXF e retorna ParsedGeometry
        |
        v
backend/geometry_builder.py
  monta ConcreteSection com materiais
        |
        v
concreteproperties
  calcula diagrama de flexao biaxial
        |
        v
frontend/app_window.py
  plota geometria e resultados
```

## Convencoes importantes

- Imports internos devem usar o pacote `cardozo`, por exemplo:

```python
from cardozo.backend.dxf_parser import DXFParser
```

- Codigo de interface deve ficar em `frontend`.
- Codigo de parsing, geometria e calculo deve ficar em `backend`.
- Dados tecnicos e bibliotecas de materiais devem ficar em `data`.
- O backend deve receber dados e devolver objetos/resultado; ele nao deve abrir janelas, mostrar mensagens ou depender de widgets.
- `__init__.py` existe para marcar os diretorios como pacotes Python. Eles podem ficar vazios quando nao houver API publica a expor.

## Pontos de atencao atuais

- `src/cardozo/data/nbr6118.py` esta vazio.
- O parser suporta no maximo dois poligonos de concreto: uma secao cheia ou uma secao com um vazio.
- A GUI depende de `tkinter`, que e modulo da instalacao do Python/sistema operacional, nao um pacote instalado via `pip`.
- Os arquivos `__pycache__` dentro de `src` sao cache local e nao devem ser versionados.
