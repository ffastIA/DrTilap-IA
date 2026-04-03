import reflex as rx
from ..state import State
from ..styles import PRIMARY, ACCENT, SECONDARY, GLASSMORPHISM_BG, GLASSMORPHISM_BORDER


def chat_message(message: tuple) -> rx.Component:
    """Renderiza uma mensagem individual do chat."""
    return rx.vstack(
        rx.box(
            rx.text(message[0], color="white", font_weight="bold"),
            background=PRIMARY,
            padding="1em",
            border_radius="1em 1em 0 1em",
            align_self="flex-end",
            max_width="80%",
        ),
        rx.box(
            rx.text(message[1], color="white"),
            background="rgba(255, 255, 255, 0.1)",
            padding="1em",
            border_radius="1em 1em 1em 0",
            align_self="flex-start",
            max_width="80%",
            backdrop_filter="blur(10px)",
            border=GLASSMORPHISM_BORDER,
        ),
        width="100%",
        spacing="2",
    )


def consultoria_content() -> rx.Component:
    """Conteúdo principal da Consultoria IA."""
    return rx.hstack(
        # Sidebar
        rx.vstack(
            rx.heading("Dr. Tilápia", size="6", color="white"),
            rx.divider(),
            rx.button(
                "Voltar ao Hub",
                on_click=rx.redirect("/hub"),
                variant="ghost",
                color_scheme="cyan",
                width="100%"
            ),
            width="250px",
            height="100vh",
            padding="2em",
            background="rgba(0, 0, 0, 0.4)",
            backdrop_filter="blur(15px)",
            border_right=GLASSMORPHISM_BORDER,
        ),

        # Área de Chat
        rx.vstack(
            rx.box(
                rx.heading(
                    "Consultoria IA - Dr. Tilápia",
                    size="7",  # CORRIGIDO: Escala 1-9 (7 é equivalente a large)
                    color="white"
                ),
                padding="2em",
                width="100%",
                background="rgba(255, 255, 255, 0.05)",
                backdrop_filter="blur(5px)",
            ),

            # Histórico de Mensagens
            rx.scroll_area(
                rx.vstack(
                    rx.foreach(State.chat_history, chat_message),
                    width="100%",
                    padding="2em",
                    spacing="4",
                ),
                height="60vh",
                width="100%",
            ),

            # Input de Mensagem
            rx.hstack(
                rx.input(
                    placeholder="Digite sua dúvida técnica...",
                    value=State.current_message,
                    on_change=State.set_current_message,
                    width="100%",
                    background="rgba(255, 255, 255, 0.1)",
                    border=GLASSMORPHISM_BORDER,
                    color="white",
                ),
                rx.button(
                    "Enviar",
                    on_click=State.handle_chat_message,
                    background=ACCENT,
                    color="white",
                    is_loading=State.is_loading,
                ),
                padding="2em",
                width="100%",
                background="rgba(0, 0, 0, 0.2)",
            ),
            width="100%",
            height="100vh",
            spacing="0",
        ),
        width="100%",
        height="100vh",
        background="url('/hub01.jpeg')",
        background_size="cover",
        background_position="center",
        spacing="0",
    )


def consultoria() -> rx.Component:
    """Página de consultoria com proteção de rota via on_mount no ui.py."""
    return rx.fragment(
        rx.cond(
            State.is_authenticated,
            consultoria_content(),
            rx.center(rx.spinner(size="3"), height="100vh")
        ),
        on_mount=State.check_login  # Proteção correta (Evento, não Componente)
    )