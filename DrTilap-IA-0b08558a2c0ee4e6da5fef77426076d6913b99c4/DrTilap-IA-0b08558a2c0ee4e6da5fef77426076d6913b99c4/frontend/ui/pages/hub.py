import reflex as rx
from ..state import State
from ..styles import PRIMARY, ACCENT, GLASSMORPHISM_BG, GLASSMORPHISM_BORDER

def floating_card(title: str, description: str, href: str, icon: str, **kwargs) -> rx.Component:
    return rx.box(
        rx.link(
            rx.vstack(
                rx.text(icon, font_size="3em"),
                rx.text(title, font_size="1.3em", font_weight="bold", color="white"),
                rx.text(description, font_size="0.9em", color="rgba(255,255,255,0.8)"),
                spacing="2",
                align_items="center",
                text_align="center"
            ),
            href=href,
            _hover={"text_decoration": "none"}
        ),
        background=GLASSMORPHISM_BG,
        border=GLASSMORPHISM_BORDER,
        border_radius="1.5em",
        padding="2em",
        width="180px",
        height="180px",
        display="flex",
        align_items="center",
        justify_content="center",
        position="absolute",
        transition="all 0.3s ease-in-out",
        _hover={"transform": "scale(1.1)", "opacity": "0.95"},
        cursor="pointer",
        **kwargs
    )

def hub_content() -> rx.Component:
    return rx.box(
        rx.image(
            src="/hub01.jpeg", width="100%", height="100vh",
            object_fit="cover", position="absolute", z_index="-1", filter="brightness(0.6)"
        ),
        floating_card("Dashboard", "Métricas", "/dashboard", "📊", bottom="20%", right="10%"),
        floating_card("Consultoria", "Chat IA", "/consultoria", "🤖", bottom="40%", left="10%"),
        floating_card("Admin", "RAG", "/admin_rag", "⚙️", top="20%", right="15%"),
        rx.box(
            rx.button("Sair", on_click=State.logout, background=ACCENT, color="white"),
            position="absolute", top="2em", right="2em", z_index="10"
        ),
        width="100%", height="100vh", position="relative", overflow="hidden"
    )

def hub() -> rx.Component:
    """Hub com proteção de rota e feedback visual."""
    return rx.fragment(
        rx.cond(
            State.is_authenticated,
            hub_content(),
            rx.center(
                rx.vstack(
                    rx.spinner(size="3"),
                    rx.text("Verificando autenticação...", color="white"),
                    spacing="2",
                    align_items="center"
                ),
                height="100vh",
                background="linear-gradient(135deg, #004e92 0%, #00ced1 100%)"
            )
        ),
        on_mount=State.check_login
    )