from shiny import App, ui

app_ui = ui.page_fluid(
    ui.h2("Dashboard de Estatística"),
    ui.p("Projeto em Shiny for Python")
)

def server(input, output, session):
    pass

app = App(app_ui, server)