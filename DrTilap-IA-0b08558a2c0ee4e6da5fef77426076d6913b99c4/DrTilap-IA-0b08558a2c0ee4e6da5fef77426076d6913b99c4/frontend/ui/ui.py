import reflex as rx
from .pages.index import index
from .pages.login import login_page
from .pages.hub import hub
from .pages.consultoria import consultoria
from .pages.dashboard import dashboard
from .state import State

app = rx.App()

# Rotas Públicas
app.add_page(index, route="/")
app.add_page(login_page, route="/login")

# Rotas Protegidas: O evento check_login roda antes da renderização
app.add_page(hub, route="/hub", on_load=State.check_login)
app.add_page(consultoria, route="/consultoria", on_load=State.check_login)
app.add_page(dashboard, route="/dashboard", on_load=State.check_login)