import reflex as rx
from ..state import State
from ..styles import PRIMARY, ACCENT, SECONDARY, GLASSMORPHISM_BG, GLASSMORPHISM_BORDER


def page_protegida(component: rx.Component) -> rx.Component:
    """Wrapper para proteção de rotas."""
    return rx.cond(
        State.is_authenticated,
        component,
        rx.redirect("/login")
    )


def admin_rag_content() -> rx.Component:
    """Conteúdo principal do painel admin RAG."""
    return rx.box(
        rx.vstack(
            # Header
            rx.hstack(
                rx.heading("Admin RAG - Gerenciar Documentos", size="9", color="white"),
                rx.spacer(),
                rx.button(
                    "Voltar",
                    on_click=rx.redirect("/hub"),
                    background=SECONDARY,
                    color="white",
                    _hover={"opacity": "0.8"}
                ),
                width="100%",
                padding="1em",
                background=PRIMARY
            ),

            # Conteúdo
            rx.vstack(
                rx.heading("Gerenciamento de Documentos", size="5", color="white"),

                rx.box(
                    rx.vstack(
                        rx.text("Funcionalidades disponíveis:", color="white", font_weight="bold"),
                        rx.unordered_list(
                            rx.list_item("Upload de novos documentos PDF"),
                            rx.list_item("Visualizar documentos indexados"),
                            rx.list_item("Reindexar base de conhecimento"),
                            rx.list_item("Gerenciar permissões de acesso"),
                            color="white"
                        ),
                        spacing="1em"
                    ),
                    background="rgba(0,0,0,0.3)",
                    padding="1.5em",
                    border_radius="0.5em",
                    width="100%"
                ),

                # Botões de ação
                rx.hstack(
                    rx.button(
                        "📤 Upload de Documento",
                        background=ACCENT,
                        color="white",
                        padding="0.8em 1.5em",
                        _hover={"opacity": "0.8"}
                    ),
                    rx.button(
                        "🔄 Reindexar",
                        background=SECONDARY,
                        color="white",
                        padding="0.8em 1.5em",
                        _hover={"opacity": "0.8"}
                    ),
                    rx.button(
                        "📋 Listar Documentos",
                        background=PRIMARY,
                        color="white",
                        padding="0.8em 1.5em",
                        _hover={"opacity": "0.8"}
                    ),
                    spacing="1em",
                    width="100%",
                    justify_content="center"
                ),

                spacing="1.5em",
                padding="2em",
                width="100%"
            ),

            spacing="1em",
            width="100%"
        ),
        width="100%",
        height="100vh",
        background="linear-gradient(135deg, #004e92 0%, #00ced1 100%)",
        padding="0"
    )


def admin_rag() -> rx.Component:
    """Página admin RAG com proteção de rotas (exportada como 'admin_rag' para ui.py)."""
    return page_protegida(admin_rag_content())