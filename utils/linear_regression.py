from shiny import ui, render, reactive
from shinywidgets import output_widget, render_plotly
import numpy as np
import plotly.express as px

def linear_regression_ui():
    return ui.div(
        ui.h4("Regressão Linear Simples"),

        ui.output_text("regression_warning"),

        ui.layout_columns(
            ui.input_select(
                "reg_x",
                "Variável explicativa (x):",
                choices=[]
            ),
            ui.input_select(
                "reg_y",
                "Variável resposta (y):",
                choices=[]
            ),
        ),

        ui.h5(),

        ui.layout_columns(
            ui.card(
                ui.card_header("Coeficiente de Correlação R"),
                ui.output_text("correlation_r")
            ),
            ui.card(
                ui.card_header("Coeficiente de Determinação R²"),
                ui.output_text("determination_r2")
            ),
            ui.card(
                ui.card_header("Equação da Reta Ajustada"),
                ui.output_text("regression_equation")
            ),
        ),

        ui.h5(),

        ui.card(
            ui.card_header("Gráfico de Dispersão com Linha de Regressão"),
            output_widget("regression_plot")
        )
    )


def get_numeric_columns(df):
    """Retorna apenas as colunas quantitativas da base."""
    return df.select_dtypes(include=np.number).columns.tolist()


def format_result(result, key):
    """Formata os resultados numéricos exibidos nos cards."""
    if result is None:
        return "Selecione as variáveis."

    if "error" in result:
        return result["error"]

    return f"{result[key]:.4f}"


def format_equation(y_var, x_var, slope, intercept):
    """Monta a equação da reta ajustada: y = a*x + b."""
    signal = "+" if intercept >= 0 else "-"
    return f"{y_var} = {slope:.8f} * {x_var} {signal} {abs(intercept):.4f}"


def linear_regression_server(input, output, session, data_fn):

    @output
    @render.text
    def regression_warning():
        df = data_fn()

        if df is None:
            return "Faça o upload de um arquivo CSV."

        numeric_cols = get_numeric_columns(df)

        if len(numeric_cols) < 2:
            return "A base precisa ter pelo menos duas variáveis quantitativas para realizar a regressão linear simples."

        return ""

    @reactive.effect
    def update_regression_choices():
        df = data_fn()

        if df is None:
            return

        numeric_cols = get_numeric_columns(df)

        if len(numeric_cols) == 0:
            return

        # Define uma seleção inicial adequada para o dataset usado.
        if "Tempo_decorrido_segundos" in numeric_cols and "Velocidade" in numeric_cols:
            selected_x = "Tempo_decorrido_segundos"
            selected_y = "Velocidade"
        else:
            selected_x = numeric_cols[0]
            selected_y = numeric_cols[1] if len(numeric_cols) > 1 else numeric_cols[0]

        ui.update_select("reg_x", choices=numeric_cols, selected=selected_x)
        ui.update_select("reg_y", choices=numeric_cols, selected=selected_y)

    @reactive.calc
    def regression_results():
        df = data_fn()
        x_var = input.reg_x()
        y_var = input.reg_y()

        if df is None or x_var is None or y_var is None:
            return None

        if x_var not in df.columns or y_var not in df.columns:
            return None

        if x_var == y_var:
            return {"error": "Selecione variáveis diferentes para x e y."}

        reg_df = df[[x_var, y_var]].dropna()

        if len(reg_df) < 2:
            return {"error": "É necessário ter pelo menos duas observações válidas."}

        x = reg_df[x_var]
        y = reg_df[y_var]

        if x.nunique() < 2:
            return {"error": "A variável x precisa ter pelo menos dois valores diferentes."}

        if y.nunique() < 2:
            return {"error": "A variável y precisa ter pelo menos dois valores diferentes."}

        # Ajusta a reta y = slope*x + intercept.
        slope, intercept = np.polyfit(x, y, 1)

        # Correlação de Pearson e coeficiente de determinação.
        r = x.corr(y)

        return {
            "df": reg_df,
            "x_var": x_var,
            "y_var": y_var,
            "slope": slope,
            "intercept": intercept,
            "r": r,
            "r2": r ** 2
        }

    @output
    @render.text
    def correlation_r():
        return format_result(regression_results(), "r")

    @output
    @render.text
    def determination_r2():
        return format_result(regression_results(), "r2")

    @output
    @render.text
    def regression_equation():
        result = regression_results()

        if result is None:
            return "Selecione as variáveis."

        if "error" in result:
            return result["error"]

        return format_equation(
            result["y_var"],
            result["x_var"],
            result["slope"],
            result["intercept"]
        )

    @output
    @render_plotly
    def regression_plot():
        result = regression_results()

        if result is None or "error" in result:
            return None

        reg_df = result["df"]
        x_var = result["x_var"]
        y_var = result["y_var"]
        slope = result["slope"]
        intercept = result["intercept"]

        fig = px.scatter(
            reg_df,
            x=x_var,
            y=y_var,
            title=f"Regressão Linear Simples: {y_var} em função de {x_var}"
        )

        # Cria os pontos da linha de regressão.
        x_line = np.linspace(reg_df[x_var].min(), reg_df[x_var].max(), 100)
        y_line = slope * x_line + intercept

        fig.add_scatter(
            x=x_line,
            y=y_line,
            mode="lines",
            name="Reta ajustada"
        )

        fig.update_layout(
            font=dict(color="white"),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            xaxis_title=x_var,
            yaxis_title=y_var,
            margin=dict(t=50, l=40, r=20, b=40)
        )

        return fig