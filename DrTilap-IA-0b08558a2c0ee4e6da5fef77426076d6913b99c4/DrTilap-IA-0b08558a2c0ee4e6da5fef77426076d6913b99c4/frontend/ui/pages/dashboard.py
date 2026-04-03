import reflex as rx
from ..state import State
from ..styles import PRIMARY, ACCENT, SECONDARY, GLASSMORPHISM_BG, GLASSMORPHISM_BORDER


def metric_card(label: str, value: str, icon: str) -> rx.Component:
    """Card de métrica individual."""
    return rx.box(
        rx.vstack(
            rx.text(icon, font_size="2em"),
            rx.text(label, font_size="0.9em", color="rgba(255,255,255,0.7)"),
            rx.text(value, font_size="1.5em", font_weight="bold", color="white"),
            spacing="2",
            align_items="center",
            text_align="center",
        ),
        background=GLASSMORPHISM_BG,
        border=GLASSMORPHISM_BORDER,
        border_radius="1em",
        padding="1.5em",
        width="150px",
        backdrop_filter="blur(10px)",
        _hover={"transform": "scale(1.05)", "opacity": "0.95"},
    )


def dashboard_content() -> rx.Component:
    """Conteúdo do dashboard."""
    return rx.vstack(
        # Header
        rx.box(
            rx.vstack(
                rx.heading(
                    "Métricas do Sistema",
                    size="5",  # CORRIGIDO: "md" → "5"
                    color="white"
                ),
                rx.text(
                    "Monitoramento em tempo real do sistema Dr. Tilápia",
                    color="rgba(255,255,255,0.7)",
                    font_size="0.9em"
                ),
                spacing="2",
            ),
            padding="2em",
            background="rgba(255, 255, 255, 0.05)",
            backdrop_filter="blur(5px)",
            width="100%",
        ),

        # Grid de Métricas
        rx.grid(
            metric_card("Temperatura", State.temperatura, "🌡️"),
            metric_card("Oxigênio", State.oxigenio, "💨"),
            metric_card("pH", State.ph, "⚗️"),
            metric_card("Amônia", State.amonia, "☠️"),
            columns="4",
            spacing="4",
            padding="2em",
            width="100%",
        ),

        # Gráfico (placeholder)
        rx.box(
            rx.text(
                "Gráfico de Tendências (Implementação Futura)",
                color="rgba(255,255,255,0.5)",
                text_align="center",
                padding="3em",
            ),
            background=GLASSMORPHISM_BG,
            border=GLASSMORPHISM_BORDER,
            border_radius="1em",
            margin="2em",
            width="calc(100% - 4em)",
            height="300px",
        ),

        # Botão de Atualização
        rx.button(
            "Atualizar Métricas",
            on_click=State.fetch_metrics,
            background=ACCENT,
            color="white",
            width="200px",
            margin="2em auto",
            is_loading=State.loading_metrics,
        ),

        width="100%",
        height="100vh",
        background="url('/hub01.jpeg')",
        background_size="cover",
        background_position="center",
        spacing="0",
        overflow_y="auto",
    )


def page_protegida(component: rx.Component) -> rx.Component:
    """Wrapper de proteção de rota."""
    return rx.fragment(
        rx.cond(
            State.is_authenticated,
            component,
            rx.center(rx.spinner(size="3"), height="100vh")
        ),
        on_mount=State.check_login
    )


def dashboard() -> rx.Component:
    """Página de dashboard."""
    return page_protegida(dashboard_content())