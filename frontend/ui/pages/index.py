import reflex as rx
from ui.styles import (
    WHITE,
    BUTTON_ACCENT,
    HERO_BG_STYLE
)


def index() -> rx.Component:
    """Landing Page minimalista com fundo hub01.jpeg."""
    return rx.center(
        rx.vstack(
            # Título e Subtítulo (ImagemPrincipal removida)
            rx.heading(
                "Dr. Tilápia 2.0",
                size="9",
                color=WHITE,
                text_shadow="0 4px 15px rgba(0,0,0,0.6)"
            ),

            rx.text(
                "A inteligência artificial que transforma a sua piscicultura.",
                color="rgba(255,255,255,0.8)",
                font_size="1.4em",
                text_align="center",
                max_width="700px",
                font_weight="medium"
            ),

            rx.spacer(),

            # Botão de Acesso
            rx.link(
                rx.button(
                    "Entrar no Sistema",
                    size="4",
                    padding="2em 4em",
                    **BUTTON_ACCENT
                ),
                href="/login",
            ),

            spacing="6",
            align="center",
            padding="4em",
            # Overlay escuro para destacar o texto sobre a hub01.jpeg
            bg="rgba(0, 8, 20, 0.55)",
            width="100%",
            height="100vh",
        ),
        # Aplica o fundo hub01.jpeg definido no styles.py
        **HERO_BG_STYLE,
        height="100vh",
        width="100%",
    )