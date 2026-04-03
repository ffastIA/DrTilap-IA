import reflex as rx

config = rx.Config(
    app_name="ui",
    # 🌐 Porta onde o motor interno do Reflex vai rodar (Websocket/State)
    backend_port=8005,
    # 🔗 URL que o Frontend usará para falar com o motor do Reflex
    backend_url="http://localhost:8002",
)