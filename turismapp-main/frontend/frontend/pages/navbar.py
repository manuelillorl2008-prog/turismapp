import reflex as rx

def navbar() -> rx.Component:
    return rx.box(
        rx.hstack(
            rx.heading("Turismo RD", size="6", color="white"),
            rx.hstack(
                rx.link("Inicio", href="/", color="white"),
                rx.link("Descripcion", href="/descripcion", color="white"),
                rx.link("Reservas", href="/reservas", color="white"),
                gap="2em",
            ),
            justify="between",
            align="center",
            width="100%",
            padding="1em 2em",
        ),
        background_color="#1a1a2e",
        width="100%",
    )
