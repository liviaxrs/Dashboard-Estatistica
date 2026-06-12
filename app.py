from shiny import App, ui, reactive, render
from shinywidgets import output_widget, render_plotly
import pandas as pd
import plotly.express as px
import numpy as np
from utils.preprocessing import preprocess_data
from utils.confidence_interval import confidence_interval_ui, confidence_interval_server
from utils.linear_regression import linear_regression_ui, linear_regression_server
from utils.hypothesis_test import hypothesis_test_ui, hypothesis_test_server


app_ui = ui.page_sidebar(
    ui.sidebar(

        ui.h4("Controles"),

        ui.input_file(
            "file",
            "Faça upload do arquivo CSV:",
            accept=[".csv"]
        ),

        ui.input_select(
            "variable",
            "Selecione a variável quantitativa:",
            choices=[]
        ),
    ),
    #Serve para deixar os titulos da tabela centralizados
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
        #TAB - Analise descritiva:
        ui.nav_panel( "Analise descritiva",
            ui.h2(),
        # Graficos histograma e boxplot:
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
            ui.h2(),
        # Tabela de medidas estatisticas:
            ui.div(
                ui.card(
                    ui.card_header("Estatísticas Descritivas"),
                    ui.output_table("stats")
                ),
                style="max-width: 800px; margin: auto;"
            ),
        ),
        #TAB - teste de hipotese:
        ui.nav_panel(
            "Teste de hipótese",
            hypothesis_test_ui()
        ),
        #TAB - Intervalo de confiança
        ui.nav_panel(
            "Intervalo de confiança",
            confidence_interval_ui()
        ),

        #TAB - Regressão linear 
        ui.nav_panel(
            "Regressão linear",
            linear_regression_ui()
        )
        
    
    ),


    theme = ui.Theme("slate"),
    
)

def server(input, output, session):
    
    @reactive.calc
    def data():
        if input.file() is None:
            return None

        df = pd.read_csv(input.file()[0]["datapath"],delimiter=';')
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
            choices=numeric_cols
        )

    @output
    @render_plotly
    def histogram():
        df = data()
        var = input.variable()

        if df is None or var is None:
            return None

        fig = px.histogram(
            df,
            x=var,
            title=f"Distribuição da variável {var}"
        )
        fig.update_layout(
            font=dict(color="white"),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            xaxis_title=input.variable(),
            yaxis_title="Frequência",
            margin=dict(t=50, l=40, r=20, b=40)
        )

        return fig
    @output
    @render_plotly
    def boxplot():
        df = data()
        var = input.variable()

        if df is None or var is None:
                return None

        fig = px.box(
                df,
                y=var,
                title=f"Boxplot da variável {var}"
            )
        fig.update_layout(
            font=dict(color="white"),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)"
        )

        return fig
    
    @output
    @render.table
    def stats():
        df = data()
        var = input.variable()

        if df is None or var is None:
            return

        series = df[var]

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
                series.mean(),
                series.median(),
                series.std(),
                series.count(),
                series.min(),
                series.max()
            ]
        })

        return stats_df
    
    confidence_interval_server(input, output, data)
    linear_regression_server(input, output, session, data)
    hypothesis_test_server(input, output, data)

app = App(app_ui, server)