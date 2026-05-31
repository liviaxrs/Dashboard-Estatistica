from shiny import ui, render, reactive
import numpy as np
from scipy.stats import norm


def confidence_interval_ui():
    return ui.div(
        ui.h4("Intervalo de Confiança Normal para a Média"),
        ui.input_slider(
            "conf_level",
            "Nível de confiança (%):",
            min=80,
            max=99,
            value=95,
            step=1,
            post="%"
        ),
        ui.h5(),
        ui.layout_columns(
            ui.card(
                ui.card_header("Limite Inferior"),
                ui.output_text("ci_lower")
            ),
            ui.card(
                ui.card_header("Limite Superior"),
                ui.output_text("ci_upper")
            ),
            ui.card(
                ui.card_header("Nível de Confiança"),
                ui.output_text("ci_level")
            ),
        ),
    )


def confidence_interval_server(input, output, data_fn):

    @reactive.calc
    def ci_results():
        df = data_fn()
        var = input.variable()
        if df is None or var not in df.columns:
            return None

        series = df[var].dropna()
        n = len(series)
        mean = series.mean()
        std = series.std(ddof=1)
        alpha = 1 - input.conf_level() / 100
        z = norm.ppf(1 - alpha / 2)
        margin = z * std / np.sqrt(n)

        return {
            "lower": mean - margin,
            "upper": mean + margin,
            "level": input.conf_level()
        }

    @output
    @render.text
    def ci_lower():
        result = ci_results()
        if result is None:
            return "Selecione uma variável"
        return f"{result['lower']:.4f}"

    @output
    @render.text
    def ci_upper():
        result = ci_results()
        if result is None:
            return "Selecione uma variável"
        return f"{result['upper']:.4f}"

    @output
    @render.text
    def ci_level():
        result = ci_results()
        if result is None:
            return "Selecione uma variável"
        return f"{result['level']}%"
