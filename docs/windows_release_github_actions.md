# Gerando o executavel Windows com GitHub Actions

Este guia descreve um fluxo profissional para gerar o executavel Windows do Cardozo usando GitHub Actions e publicar o pacote final em uma Release do GitHub.

## Por que usar GitHub Actions

O PyInstaller deve gerar o executavel no mesmo sistema operacional do destino. Portanto, para distribuir um `.exe` para Windows, o build deve ser feito em um ambiente Windows.

Mesmo desenvolvendo no Linux, o caminho recomendado e:

1. Manter o codigo-fonte no repositorio.
2. Gerar o `.exe` automaticamente em um runner Windows do GitHub Actions.
3. Compactar a pasta gerada pelo PyInstaller em um arquivo `.zip`.
4. Publicar o `.zip` em GitHub Releases.

Nao e recomendado commitar o `.exe` diretamente no repositorio. Binarios de distribuicao devem ficar nas Releases.

## Estrutura ja existente no projeto

Este projeto ja possui os arquivos principais para empacotamento:

```text
Cardozo.spec
requirements.txt
requirements-build.txt
scripts/build_exe.bat
```

O arquivo `Cardozo.spec` define como o PyInstaller monta a aplicacao. O build gera o executavel em:

```text
dist/Cardozo/Cardozo.exe
```

## Criando o workflow

Crie o arquivo:

```text
.github/workflows/windows-release.yml
```

Com o seguinte conteudo:

```yaml
name: Build Windows Release

on:
  push:
    tags:
      - "v*"

permissions:
  contents: write

jobs:
  build-windows:
    name: Build Windows executable
    runs-on: windows-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install -r requirements-build.txt

      - name: Run tests
        run: python -m unittest discover -s tests

      - name: Build executable with PyInstaller
        run: pyinstaller Cardozo.spec

      - name: Package Windows build
        run: Compress-Archive -Path dist/Cardozo/* -DestinationPath Cardozo-Windows-${{ github.ref_name }}.zip

      - name: Publish GitHub Release
        uses: softprops/action-gh-release@v2
        with:
          files: Cardozo-Windows-${{ github.ref_name }}.zip
```

## Como publicar uma nova versao

Atualize a versao do projeto em `pyproject.toml`, se necessario:

```toml
[project]
version = "0.1.0"
```

Depois faca o commit das alteracoes:

```bash
git add pyproject.toml .github/workflows/windows-release.yml
git commit -m "Add Windows release workflow"
git push
```

Crie uma tag de versao:

```bash
git tag v0.1.0
git push origin v0.1.0
```

Quando a tag for enviada, o GitHub Actions sera executado automaticamente. Ao final do processo, o GitHub criara uma Release contendo um arquivo parecido com:

```text
Cardozo-Windows-v0.1.0.zip
```

Dentro desse `.zip` estara o executavel:

```text
Cardozo.exe
```

## Padrao recomendado para versoes

Use versionamento semantico:

```text
vMAJOR.MINOR.PATCH
```

Exemplos:

```text
v0.1.0
v0.2.0
v1.0.0
```

Uma regra pratica:

- `PATCH`: correcoes pequenas, sem alterar funcionalidades principais.
- `MINOR`: novas funcionalidades compativeis com a versao anterior.
- `MAJOR`: mudancas grandes ou incompatibilidades.

## O que deve ir para o GitHub

Deve ser commitado:

```text
src/
tests/
docs/
requirements.txt
requirements-build.txt
pyproject.toml
Cardozo.spec
.github/workflows/windows-release.yml
```

Nao deve ser commitado:

```text
build/
dist/
*.exe
*.zip
.venv/
```

Esses arquivos sao saidas de build ou arquivos locais. O `.gitignore` do projeto ja cobre os diretorios principais `build/` e `dist/`.

## Testando o workflow

Depois de enviar a tag, abra no GitHub:

```text
Actions -> Build Windows Release
```

Verifique se as etapas passaram:

```text
Install dependencies
Run tests
Build executable with PyInstaller
Package Windows build
Publish GitHub Release
```

Se alguma etapa falhar, abra o log da etapa correspondente.

## Observacoes profissionais

Para uma distribuicao mais madura, considere:

- Criar releases com notas claras do que mudou.
- Testar o `.zip` em uma maquina Windows limpa.
- Adicionar icone ao executavel no `Cardozo.spec`.
- Assinar digitalmente o executavel no futuro, caso a ferramenta seja distribuida publicamente.
- Criar instalador com Inno Setup ou NSIS se o projeto precisar de instalacao tradicional.

O fluxo com GitHub Actions e GitHub Releases ja e suficiente para distribuir uma versao profissional inicial sem colocar binarios dentro do repositorio.
