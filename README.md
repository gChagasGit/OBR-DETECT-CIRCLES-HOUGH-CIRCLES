# Comparação de Filtros de Pré-Processamento para identificação de Esferas com Hough Circles na OBR
Bem vindo!

Me chamo Gustavo Chagas, desenvolvi esse projeto na disciplina de Processamento de Imagens 
da Universidade Federal de São Paulo (UNIFESP) - São José dos Campos (SJC).

As imagens estão em 4640 x 3488, com 24 de intensidade de bits, não possui apenas as esferas anotadas/rotuladas,
como tbm possuem outras registradas, para caso futuramente desejem produzir outros trabalhos.

annotations foi construido possuindo as esferas evidentes, rutuladas como 'esferas' e
esferas oclusas rotuladas como 'esferas2'.

# Detecção de Esferas usando Filtros e Hough Circles

Este repositório contém um script Python para detectar esferas em imagens usando diferentes filtros e a transformada de Hough.

## Estrutura do Repositório

- [Baixe as Imagens](https://drive.google.com/file/d/11EiaMbnUO2u8ymdRK7S7gVkEKjQiAhQf/view?usp=drive_link): Link para baixar o arquivo `Imagens.zip` contendo imagens de teste.
- `filtersAndHoughCircles.py`: Script principal para detecção de esferas.
- `labels/annotations.xml`: Arquivo XML com anotações das posições das esferas nas imagens.
- `Readme.txt`: Este arquivo.

## Instruções

### Configuração

1. **Baixando as Imagens:**
   - Baixe e descompacte o arquivo `Imagens.zip`.
   - Coloque as imagens descompactadas em um diretório específico.

2. **Configurando o Ambiente:**
   - Instale as dependências necessárias listadas no arquivo `requirements.txt`, se houver.

### Executando o Código

1. **Executando o Script:**
   - Abra um terminal e navegue até o diretório onde o script `filtersAndHoughCircles.py` está localizado.
   - Execute o script usando o Python: `python filtersAndHoughCircles.py --dp 1.05 --minDist 20 ...` (substitua os parâmetros conforme necessário).

### XML de Anotações

O arquivo `annotations.xml` contém informações detalhadas sobre as posições e tamanhos das esferas nas imagens. Certifique-se de revisar este arquivo para entender como as anotações estão estruturadas.

### Resultados Esperados

Ao executar o script, você obterá resultados que incluem a taxa de correspondência das esferas detectadas com as anotadas, médias das relações de raios, entre outros detalhes importantes.

## Dependências

Para garantir que o script `filtersAndHoughCircles.py` funcione corretamente, você precisará das seguintes bibliotecas e pacotes Python instalados:

1. `xml.etree.ElementTree` (já incluído no Python padrão)
2. `cv2` (OpenCV)
3. `numpy` (NumPy)
4. `os` (já incluído no Python padrão)
5. `time` (já incluído no Python padrão)
6. `argparse` (já incluído no Python padrão)

### Passos para instalar os requerimentos

1. Há um arquivo chamado `requirements.txt`.
2. Abra um terminal e navegue até o diretório do seu projeto.
3. Execute o seguinte comando para instalar os pacotes listados no `requirements.txt`:

```sh
pip install -r requirements.txt
```

Este comando instalará o NumPy e o OpenCV, que são os pacotes adicionais necessários para o seu script. Os outros módulos (`xml.etree.ElementTree`, `os`, `time`, e `argparse`) são parte da biblioteca padrão do Python e não requerem instalação adicional.

## Contato

Para mais informações ou para reportar problemas, entre em contato pelo email: chagasgustavo10@gmail.com.
