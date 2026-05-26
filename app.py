from shiny import App, ui, reactive, render
from shinywidgets import output_widget, render_plotly
import pandas as pd
import plotly.express as px
import numpy as np
from src.preprocessing import preprocess_data


app_ui = ui.page_fluid(
    ui.h2("Análise Descritiva de Variável Quantitativa"),

    ui.input_file(
        "file",
        "Selecione o arquivo CSV",
        accept=[".csv"]
    ),

    ui.input_select(
        "variable",
        "Selecione a variável quantitativa",
        choices=[]
    ),

    ui.hr(),

    ui.layout_columns(
        output_widget("histogram"),
        output_widget("boxplot")
    ),

    ui.hr(),

    ui.output_table("stats")
)

def server(input, output, session):
    
    @reactive.calc
    def data():
        if input.file() is None:
            return None

        df = pd.read_csv(input.file()[0]["datapath"],delimiter=';')
        df = preprocess_data(df)
        print(df.head())
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
            title=f"Histograma de {var}"
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
                title=f"Boxplot de {var}"
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
    
app = App(app_ui, server)