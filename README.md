# Rede de Competências Lattes - Dashbooard INCTs & Áreas

## 1. Contextualização
Esse projeto é uma análise dos pesquisadores distribuídos nos 103 INCTs e nas 7 grandes Áreas.
E um relátorio/dash no formato do streamlit. Nele é possível ver as análises tanto por área quando por INCT:

- Descrição de cada INCT/Área feita por consultores capacitados
- Análise de redes
- Distribuição de palavras por período
- Nuvem de palavras
- Quantitativo de tipos de produção bibliográfica
- Quantitativo das maiores formações
- Distribuição por estado dos endereços das Instituições/Empresas
- Quantitivo de pesquisadores


## 2. Executar o projeto

### 2.1 Pré-Requisitos
- Ambiente com python instalado
- Sugestão: Docker ou ambiente virtual (virtualenv)


### 2.2 Como executar
Para executar o projeto, crie um ambiente virtual e dentro da pasta `app`, rode o comando:

#### 2.2.1 Ambiente Virtual 
```python
pip install -r requirements.txt
```

Com todas as bibliotecas necessárias instaladas, suba a aplicação via streamlit.

```python
streamlit run main_app.py
```


#### 2.2.2 Docker 

Na pasta `app`, onde se encontra o arquivo **Dockerfile**, é preciso primiero fazer o build da imagem:

```python
docker build -t app-inct .
```

Execute o container na porta 8502:

```python
docker run -p 8502:8502 app-inct
```

Depois é só abrir no navegador:
👉 `http://localhost:8502`

Para subir em modo detatched e com restart:

```python
docker run -d \
  --name cgee-inct \
  --restart=always \
  -p 8502:8502 \
  app-inct
```
