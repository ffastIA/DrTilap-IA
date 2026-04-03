import reflex as rx
from ..state import State
from ..styles import PRIMARY, ACCENT, BACKGROUND, WHITE, SECONDARY

def login_page() -> rx.Component:
    return rx.center(
        rx.vstack(
            rx.heading("Dr. Tilápia 1.3", size="8", color=WHITE), # Size 1-9
            rx.input(placeholder="E-mail", on_change=State.set_user_email, width="100%"),
            rx.input(placeholder="Senha", type="password", on_change=State.set_password, width="100%"),
            rx.button("Entrar", on_click=State.handle_login, width="100%", bg=ACCENT, is_loading=State.is_loading),
            rx.cond(State.error_message != "", rx.text(State.error_message, color="red")),
            spacing="4",
            padding="2em",
            bg="rgba(255,255,255,0.1)",
            border_radius="15px",
            backdrop_filter="blur(10px)",
        ),
        height="100vh",
        bg=BACKGROUND,
    )