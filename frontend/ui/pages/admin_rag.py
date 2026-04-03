import reflex as rx
from ui.state import State
from ui.styles import (
    GLASS_CONTAINER_STYLE,
    ACCENT,
    WHITE,
    BACKGROUND_GRADIENT,
    BUTTON_ACCENT
)


def admin_rag() -> rx.Component:
    """Painel administrativo para gestão da base de conhecimento RAG."""
    return rx.center(
        rx.vstack(
            # Cabeçalho da Página
            rx.vstack(
                rx.icon(tag="database", size=40, color=ACCENT),
                rx.heading("Gestão de Conhecimento", size="8", color=WHITE),
                rx.text(
                    "Atualize os manuais técnicos do Dr. Tilápia",
                    color="rgba(255,255,255,0.6)",
                    font_size="0.9em"
                ),
                align="center",
                spacing="1",
                margin_bottom="1.5em",
            ),

            # Área de Upload de Documentos
            rx.vstack(
                rx.text("Upload de Manuais (PDF)", font_weight="bold", color=WHITE),
                rx.upload(
                    rx.vstack(
                        rx.button(
                            "Selecionar PDFs",
                            color=ACCENT,
                            variant="outline",
                            border=f"1px solid {ACCENT}"
                        ),
                        rx.text(
                            "Arraste os arquivos aqui ou clique para selecionar",
                            font_size="0.8em",
                            color="rgba(255,255,255,0.5)"
                        ),
                        spacing="2",
                        align="center",
                    ),
                    id="upload_manual",
                    border=f"1px dashed {ACCENT}",
                    padding="3em",
                    border_radius="1em",
                    width="100%",
                    bg="rgba(255, 255, 255, 0.02)",
                ),

                # Botão que dispara o upload para o Backend
                rx.button(
                    "Fazer Upload dos Arquivos",
                    on_click=State.handle_upload(
                        rx.upload_files(upload_id="upload_manual")
                    ),
                    is_loading=State.is_loading,
                    width="100%",
                    height="3.5em",
                    **BUTTON_ACCENT
                ),
                width="100%",
                spacing="4",
            ),

            rx.divider(margin_y="1.5em", border_color="rgba(255,255,255,0.1)"),

            # Ações de Manutenção da IA
            rx.vstack(
                rx.text("Manutenção da Inteligência", font_weight="bold", color=WHITE),
                rx.button(
                    rx.hstack(
                        rx.icon(tag="refresh-cw", size=18),
                        rx.text("Reindexar Base de Dados"),
                        align="center",
                        spacing="2",
                    ),
                    on_click=State.handle_reindex,
                    is_loading=State.is_loading,
                    variant="outline",
                    color=WHITE,
                    width="100%",
                    height="3.5em",
                    _hover={"bg": "rgba(255,255,255,0.1)"},
                ),
                rx.text(
                    "A reindexação processa os novos PDFs e atualiza a memória da IA.",
                    font_size="0.75em",
                    color="rgba(255,255,255,0.4)",
                    text_align="center",
                ),
                width="100%",
                spacing="3",
            ),

            # Navegação de Retorno
            rx.link(
                rx.button(
                    "Voltar ao Hub",
                    variant="ghost",
                    color=WHITE,
                    _hover={"color": ACCENT}
                ),
                href="/hub",
                margin_top="1em",
            ),

            spacing="5",
            padding="3em",
            width="550px",
            **GLASS_CONTAINER_STYLE,
        ),
        height="100vh",
        width="100%",
        background=BACKGROUND_GRADIENT,
    )