import os
from shiny import App, ui, reactive, render
from shinywidgets import output_widget, render_plotly
import pandas as pd
import plotly.express as px
import numpy as np

from utils.preprocessing import preprocess_data
from utils.confidence_interval import confidence_interval_ui, confidence_interval_server
from utils.linear_regression import linear_regression_ui, linear_regression_server
from utils.hypothesis_test import hypothesis_test_ui, hypothesis_test_server

data_dir = "data"
try:
    datasets_disponiveis = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
except FileNotFoundError:
    datasets_disponiveis = []

app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.h4("Controles"),

        ui.input_select(
            "dataset",
            "Selecione o Dataset:",
            choices=datasets_disponiveis
        ),

        ui.input_select(
            "variable",
            "Selecione a variável quantitativa:",
            choices=[]
        ),
    ),

    ui.tags.style("""
        table {
            width: 100%;
        }

        table thead th {
            text-align: left;
            white-space: nowrap;
        }
    """),

    ui.h2("Dashboard de Análise Descritiva"),

    ui.navset_tab(
        ui.nav_panel(
            "Analise descritiva",

            ui.layout_columns(
                ui.card(
                    ui.card_header("Histograma"),
                    output_widget("histogram")
                ),
                ui.card(
                    ui.card_header("Boxplot"),
                    output_widget("boxplot")
                )
            ),

            ui.br(),

            ui.div(
                ui.card(
                    ui.card_header("Estatísticas Descritivas"),
                    ui.output_table("stats")
                ),
                style="max-width: 800px; margin: auto;"
            ),
        ),

        ui.nav_panel(
            "Teste de hipótese",
            hypothesis_test_ui()
        ),

        ui.nav_panel(
            "Intervalo de confiança",
            confidence_interval_ui()
        ),

        ui.nav_panel(
            "Regressão linear",
            linear_regression_ui()
        )
    ),

    theme=ui.Theme("slate"),
)


def server(input, output, session):

    @reactive.calc
    def data():
        if not input.dataset():
            return None

        caminho = os.path.join(data_dir, input.dataset())

        try:
            df = pd.read_csv(caminho, sep=None, engine="python")
        except Exception:
            df = pd.read_csv(caminho, sep=";")

        df = preprocess_data(df)

        return df

    @reactive.effect
    def update_variable_choices():
        df = data()

        if df is None:
            return

        numeric_cols = df.select_dtypes(include=np.number).columns.tolist()

        ui.update_select(
            "variable",
            choices=numeric_cols,
            selected=numeric_cols[0] if len(numeric_cols) > 0 else None
        )

    @output
    @render_plotly
    def histogram():
        df = data()
        var = input.variable()

        # Evita a condição de corrida checando se a coluna existe no df atual
        if df is None or var is None or var == "" or var not in df.columns:
            return None

        df[var] = pd.to_numeric(df[var], errors="coerce")
        df_plot = df.dropna(subset=[var])

        fig = px.histogram(
            df_plot,
            x=var,
            title=f"Distribuição da variável {var}"
        )

        fig.update_layout(
            font=dict(color="white"),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            xaxis_title=var,
            yaxis_title="Frequência",
            margin=dict(t=50, l=40, r=20, b=40)
        )

        return fig

    @output
    @render_plotly
    def boxplot():
        df = data()
        var = input.variable()

        # Evita a condição de corrida checando se a coluna existe no df atual
        if df is None or var is None or var == "" or var not in df.columns:
            return None

        df[var] = pd.to_numeric(df[var], errors="coerce")
        df_plot = df.dropna(subset=[var])

        fig = px.box(
            df_plot,
            y=var,
            title=f"Boxplot da variável {var}"
        )

        fig.update_layout(
            font=dict(color="white"),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            yaxis_title=var
        )

        return fig

    @output
    @render.table
    def stats():
        df = data()
        var = input.variable()

        # Evita a condição de corrida checando se a coluna existe no df atual
        if df is None or var is None or var == "" or var not in df.columns:
            return None

        series = pd.to_numeric(df[var], errors="coerce").dropna()

        stats_df = pd.DataFrame({
            "Estatística": [
                "Média",
                "Mediana",
                "Desvio-padrão",
                "Tamanho da amostra",
                "Mínimo",
                "Máximo"
            ],
            "Valor": [
                round(series.mean(), 4),
                round(series.median(), 4),
                round(series.std(), 4),
                int(series.count()),
                round(series.min(), 4),
                round(series.max(), 4)
            ]
        })

        return stats_df

    confidence_interval_server(input, output, data)
    linear_regression_server(input, output, session, data)
    hypothesis_test_server(input, output, data)

app = App(app_ui, server)