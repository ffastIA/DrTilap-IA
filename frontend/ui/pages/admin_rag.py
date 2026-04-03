import reflex as rx
from ui.state import State
from ui.styles import GLASS_CONTAINER_STYLE, ACCENT, WHITE, BACKGROUND_GRADIENT, BUTTON_ACCENT

def admin_rag() -> rx.Component:
    return rx.center(
        rx.vstack(
            rx.heading("Gestão de Conhecimento", color=WHITE, size="8"),
            rx.upload(
                rx.vstack(
                    rx.button("Selecionar PDFs", color=ACCENT, variant="outline"),
                    rx.text("Ou arraste os manuais aqui", font_size="0.8em", color="rgba(255,255,255,0.5)"),
                    spacing="2", align="center",
                ),
                id="upload_manual",
                multiple=True,
                accept={"application/pdf": [".pdf"]},
                border=f"2px dashed {ACCENT}", padding="4em", width="100%",
                bg="rgba(255, 255, 255, 0.03)",
            ),
            # Feedback visual do Drag and Drop
            rx.vstack(
                rx.foreach(rx.selected_files("upload_manual"), lambda f: rx.text(f"📎 {f}", color=WHITE, font_size="0.8em")),
                width="100%", align="start"
            ),
            rx.button("Enviar Arquivos", on_click=State.handle_upload(rx.upload_files(upload_id="upload_manual")), is_loading=State.is_loading, width="100%", **BUTTON_ACCENT),
            rx.link("Voltar ao Hub", href="/hub", color=WHITE, opacity="0.6"),
            width="550px", padding="3em", spacing="5", **GLASS_CONTAINER_STYLE
        ),
        height="100vh", width="100%", background=BACKGROUND_GRADIENT
    )