import reflex as rx
from ui.styles import PRIMARY, ACCENT, WHITE, BACKGROUND_GRADIENT, BUTTON_ACCENT

def index() -> rx.Component:
    return rx.center(
        rx.vstack(
            rx.image(src="/ImagemPrincipal.png", width="250px", margin_bottom="2em"),
            rx.heading("Bem-vindo ao Dr. Tilápia 2.0", size="9", color=WHITE),
            rx.text(
                "A próxima geração em inteligência para piscicultura tecnológica.",
                color="rgba(255,255,255,0.7)",
                font_size="1.2em",
                text_align="center",
            ),
            rx.spacer(),
            rx.link(
                rx.button(
                    "Entrar no Sistema",
                    size="4",
                    **BUTTON_ACCENT
                ),
                href="/login",
            ),
            spacing="6",
            align="center",
            padding="4em",
        ),
        height="100vh",
        width="100%",
        background=BACKGROUND_GRADIENT,
    )