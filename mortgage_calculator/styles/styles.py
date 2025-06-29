import reflex as rx

# Design system colors
COLORS = {
    "primary": "#1e3a8a",
    "secondary": "#10b981",
    "accent": "#f59e0b",
    "background": "#f9fafb",
    "text": "#374151",
    "error": "#ef4444",
    "white": "#ffffff",
    "gray_100": "#f3f4f6",
    "gray_200": "#e5e7eb",
    "gray_600": "#6b7280",
    "gray_900": "#111827",
}

# Component styles
button_style = {
    "border_radius": "0.375rem",
    "font_weight": "medium",
    "transition": "all 0.2s",
    "_hover": {
        "transform": "translateY(-1px)",
        "box_shadow": "md",
    },
}

card_style = {
    "padding": "1rem",
    "border_radius": "0.5rem",
    "border": f"1px solid {COLORS['gray_200']}",
    "background_color": COLORS["white"],
    "box_shadow": "sm",
}

input_style = {
    "border_radius": "0.375rem",
    "border": f"1px solid {COLORS['gray_200']}",
    "_focus": {
        "border_color": COLORS["primary"],
        "box_shadow": f"0 0 0 3px {COLORS['primary']}20",
    },
}