import reflex as rx

def inicio() -> rx.Component:
    return rx.box(
        rx.heading("Bienvenido a Turismo RD", size="9"),
        rx.text("Descubre los mejores destinos turisticos"),
    )