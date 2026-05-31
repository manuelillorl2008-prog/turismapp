import reflex as rx
import httpx
from frontend.pages.navbar import navbar

class State(rx.State):
    ofertas: list[dict] = []

    def cargar_ofertas(self):
        try:
            r = httpx.get("http://localhost:8001/ofertas")
            self.ofertas = r.json()["data"]
        except:
            self.ofertas = []

def tarjeta_oferta(oferta: dict) -> rx.Component:
    return rx.box(
        rx.image(src=oferta["imagen_url"], width="100%", height="200px", object_fit="cover"),
        rx.box(
            rx.heading(oferta["nombre"], size="5", margin_bottom="0.5em"),
            rx.text(oferta["descripcion"], color="gray", height="80px", overflow="hidden"),
            rx.text(oferta["duracion"], margin_top="0.5em", margin_bottom="0.5em"),
            rx.flex(
                rx.text(oferta["precio"], color="green", weight="bold", size="5"),
                rx.button("Ver más", on_click=rx.redirect("/descripcion")),
                justify="between",
                align="center",
                width="100%",
            ),
            padding="1em",
            height="220px",
            display="flex",
            flex_direction="column",
            justify_content="space-between",
        ),
        border="1px solid #333",
        border_radius="12px",
        width="300px",
        overflow="hidden",
    )

def inicio() -> rx.Component:
    return rx.box(
        navbar(),
        rx.vstack(
            rx.heading("Bienvenido a Turismo RD", size="9"),
            rx.text("Descubre los mejores destinos turisticos"),
            align="center",
            padding="2em",
        ),
        rx.flex(
            rx.foreach(State.ofertas, tarjeta_oferta),
            gap="1.5em",
            flex_wrap="wrap",
            justify="center",
            padding="2em",
            align_items="stretch",
        ),
        on_mount=State.cargar_ofertas,
    )
