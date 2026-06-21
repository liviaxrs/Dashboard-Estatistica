# Dashboard de Análise Estatística

Dashboard web interativo em **Shiny for Python** para análise estatística de datasets `.csv`. Permite explorar dados de forma descritiva e aplicar técnicas de estatística inferencial diretamente no navegador.

## Funcionalidades

O dashboard é organizado em quatro abas:

| Aba | Descrição |
|-----|-----------|
| **Análise descritiva** | Histograma e boxplot interativos (Plotly) e tabela de estatísticas (média, mediana, desvio-padrão, tamanho da amostra, mínimo e máximo). |
| **Teste de hipótese** | Teste Z para a média populacional com variância conhecida. Suporta testes bilateral, unilateral à direita e à esquerda, com controle do nível de significância (α). Exibe estatística Z, valor crítico, valor-p e a decisão do teste. |
| **Intervalo de confiança** | Intervalo de confiança normal para a média, com nível de confiança ajustável (80% a 99%). |
| **Regressão linear** | Regressão linear simples entre duas variáveis quantitativas, com coeficiente de correlação (R), coeficiente de determinação (R²), equação da reta ajustada e gráfico de dispersão com a reta. |

Os controles na barra lateral permitem **selecionar o dataset** (entre os arquivos da pasta `data/`) e a **variável quantitativa** a ser analisada.

## Tecnologias

- [Shiny for Python](https://shiny.posit.co/py/) — framework do dashboard
- [Plotly](https://plotly.com/python/) / [shinywidgets](https://github.com/posit-dev/py-shinywidgets) — gráficos interativos
- [pandas](https://pandas.pydata.org/) / [NumPy](https://numpy.org/) — manipulação de dados
- [SciPy](https://scipy.org/) — funções estatísticas

## Estrutura do projeto

```
Dashboard-Estatistica/
├── app.py                        # Aplicação principal (UI + servidor)
├── data/                         # Datasets .csv disponíveis no dashboard
│   ├── Consumo_Combustivel.csv
│   ├── StudentsPerformance.csv
│   └── winequality-red.csv
├── utils/
│   ├── preprocessing.py          # Limpeza e transformação dos dados
│   ├── confidence_interval.py    # Intervalo de confiança
│   ├── hypothesis_test.py        # Teste de hipótese
│   └── linear_regression.py      # Regressão linear simples
├── requirements.txt
└── README.md
```

Cada técnica estatística fica em seu próprio módulo dentro de `utils/`, expondo um par de funções `*_ui()` e `*_server()` que são montadas em `app.py`.

## Datasets

Os datasets incluídos na pasta `data/` foram obtidos do Kaggle:

| Arquivo | Descrição | Fonte |
|---------|-----------|-------|
| `Consumo_Combustivel.csv` | Consumo de combustível de automóveis (Auto MPG) | [Auto-MPG Dataset](https://www.kaggle.com/datasets/uciml/autompg-dataset) |
| `StudentsPerformance.csv` | Desempenho de estudantes em provas | [Students Performance in Exams](https://www.kaggle.com/datasets/spscientist/students-performance-in-exams) |
| `winequality-red.csv` | Qualidade de vinhos tintos (Cortez et al., 2009) | [Red Wine Quality](https://www.kaggle.com/datasets/uciml/red-wine-quality-cortez-et-al-2009) |

## Instalação

Requer **Python 3.12+**.

```bash
# Clonar o repositório
git clone <url-do-repositorio>
cd Dashboard-Estatistica

# Criar e ativar o ambiente virtual
python -m venv venv
source venv/bin/activate        # Linux/macOS
# venv\Scripts\activate         # Windows

# Instalar as dependências
pip install -r requirements.txt
```

## Como executar

```bash
shiny run app.py
```

O comando inicia o servidor local; acesse o endereço exibido no terminal (por padrão, `http://127.0.0.1:8000`) no navegador.

Para recarregar automaticamente a cada alteração no código durante o desenvolvimento:

```bash
shiny run --reload app.py
```

## Adicionando novos datasets

Basta colocar um arquivo `.csv` na pasta `data/`. Ele aparecerá automaticamente no seletor de datasets da barra lateral. O dashboard detecta o separador automaticamente e disponibiliza para análise as colunas quantitativas do arquivo.
