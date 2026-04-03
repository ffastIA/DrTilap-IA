import reflex as rx
from ..styles import PRIMARY, ACCENT, BACKGROUND

def index():
    return rx.box(
        rx.box(
            rx.vstack(
                rx.heading("Dr. Tilápia 2.0", size="9", color="white"),
                rx.text("IA a serviço da sua piscicultura.", color="white", font_size="1.5em"),
                rx.link(
                    rx.button("Entrar no Sistema", bg=ACCENT, color="white", size="4"),
                    href="/login",
                ),
                spacing="5", align="center",
            ),
            background_image="url('/bg_hero.png')",
            background_size="cover",
            background_position="center",
            background_blend_mode="overlay",
            background_color="rgba(0, 8, 20, 0.6)",
            height="100vh", display="flex", align_items="center", justify_content="center", width="100%",
        ),
        bg=BACKGROUND, width="100%",
    )