import reflex as rx

# Paleta de Cores
PRIMARY = "#004e92"
ACCENT = "#ff7f50"
SECONDARY = "#00ced1"
WHITE = "#ffffff"

# Gradiente de Fundo
BACKGROUND_GRADIENT = f"radial-gradient(circle at center, {PRIMARY} 0%, #000814 100%)"

# Estilo Glassmorphism
GLASS_CONTAINER_STYLE = {
    "backdrop_filter": "blur(12px)",
    "background_color": "rgba(255, 255, 255, 0.05)",
    "border": "1px solid rgba(255, 255, 255, 0.1)",
    "border_radius": "1.5em",
    "box_shadow": "0 8px 32px 0 rgba(0, 0, 0, 0.37)",
}

BUTTON_ACCENT = {
    "bg": ACCENT,
    "color": WHITE,
    "_hover": {"bg": "#ff6347", "transform": "scale(1.02)"},
    "transition": "all 0.2s ease-in-out",
}