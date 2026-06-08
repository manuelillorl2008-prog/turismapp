import reflex as rx

def descripcion() -> rx.Component:
    return rx.box(
        rx.heading("Descripción del destino", size="9"),
    )