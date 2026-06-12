from shiny import ui, render, reactive
import numpy as np
from scipy.stats import norm


def hypothesis_test_ui():
    return ui.div(
        ui.h4("Teste de Hipóteses para a Média (variância conhecida)"),

        ui.layout_columns(
            ui.input_numeric(
                "ht_variance",
                "Variância populacional (σ²):",
                value=1,
                min=0.0001,
                step=1
            ),
            ui.input_radio_buttons(
                "ht_type",
                "Tipo de teste:",
                choices={
                    "bilateral": "Bilateral (μ ≠ μ₀)",
                    "right": "Unilateral à direita (μ > μ₀)",
                    "left": "Unilateral à esquerda (μ < μ₀)"
                },
                selected="bilateral"
            ),
        ),

        ui.input_slider(
            "ht_mu0",
            "Valor de μ₀:",
            min=0,
            max=100,
            value=50,
            step=0.1
        ),

        ui.input_slider(
            "ht_alpha",
            "Nível de significância (α):",
            min=0.01,
            max=0.10,
            value=0.05,
            step=0.01
        ),

        ui.h5(),

        ui.layout_columns(
            ui.card(
                ui.card_header("Estatística do teste (Z)"),
                ui.output_text("ht_statistic")
            ),
            ui.card(
                ui.card_header("Valor crítico"),
                ui.output_text("ht_critical")
            ),
            ui.card(
                ui.card_header("Valor-p"),
                ui.output_text("ht_pvalue")
            ),
        ),

        ui.card(
            ui.card_header("Decisão do teste"),
            ui.output_ui("ht_decision")
        ),
    )


def hypothesis_test_server(input, output, data_fn):

    # Ajusta o slider de mu0 ao intervalo da variável selecionada.
    @reactive.effect
    def update_mu0_slider():
        df = data_fn()
        var = input.variable()
        if df is None or var not in df.columns:
            return

        series = df[var].dropna()
        if len(series) == 0:
            return

        v_min = float(series.min())
        v_max = float(series.max())
        v_mean = float(series.mean())

        # Evita min == max (slider degenerado).
        if v_min == v_max:
            v_min -= 1
            v_max += 1

        ui.update_slider(
            "ht_mu0",
            min=round(v_min, 2),
            max=round(v_max, 2),
            value=round(v_mean, 2),
            step=round((v_max - v_min) / 100, 4) or 0.1
        )

    @reactive.calc
    def ht_results():
        df = data_fn()
        var = input.variable()
        if df is None or var not in df.columns:
            return None

        variance = input.ht_variance()
        if variance is None or variance <= 0:
            return {"error": "Informe uma variância populacional positiva."}

        series = df[var].dropna()
        n = len(series)
        if n == 0:
            return None

        mean = series.mean()
        sigma = np.sqrt(variance)
        mu0 = input.ht_mu0()
        alpha = input.ht_alpha()
        test_type = input.ht_type()

        # Estatística do teste Z (variância conhecida).
        z = (mean - mu0) / (sigma / np.sqrt(n))

        if test_type == "bilateral":
            critical = norm.ppf(1 - alpha / 2)
            p_value = 2 * (1 - norm.cdf(abs(z)))
            reject = abs(z) > critical
            critical_label = f"±{critical:.4f}"
        elif test_type == "right":
            critical = norm.ppf(1 - alpha)
            p_value = 1 - norm.cdf(z)
            reject = z > critical
            critical_label = f"{critical:.4f}"
        else:  # left
            critical = norm.ppf(alpha)
            p_value = norm.cdf(z)
            reject = z < critical
            critical_label = f"{critical:.4f}"

        return {
            "z": z,
            "critical_label": critical_label,
            "p_value": p_value,
            "reject": reject,
            "alpha": alpha,
        }

    @output
    @render.text
    def ht_statistic():
        result = ht_results()
        if result is None:
            return "Selecione uma variável"
        if "error" in result:
            return result["error"]
        return f"{result['z']:.4f}"

    @output
    @render.text
    def ht_critical():
        result = ht_results()
        if result is None or "error" in result:
            return "—"
        return result["critical_label"]

    @output
    @render.text
    def ht_pvalue():
        result = ht_results()
        if result is None or "error" in result:
            return "—"
        return f"{result['p_value']:.4f}"

    @output
    @render.ui
    def ht_decision():
        result = ht_results()
        if result is None:
            return ui.span("Selecione uma variável")
        if "error" in result:
            return ui.span(result["error"], style="color: orange;")

        if result["reject"]:
            texto = (
                f"Rejeita-se H₀ ao nível de significância α = {result['alpha']:.2f} "
                f"(valor-p = {result['p_value']:.4f})."
            )
            cor = "#e74c3c"
        else:
            texto = (
                f"Não se rejeita H₀ ao nível de significância α = {result['alpha']:.2f} "
                f"(valor-p = {result['p_value']:.4f})."
            )
            cor = "#2ecc71"

        return ui.strong(texto, style=f"color: {cor};")
