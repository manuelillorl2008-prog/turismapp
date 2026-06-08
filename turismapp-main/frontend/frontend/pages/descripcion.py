import reflex as rx
import httpx
from frontend.pages.navbar import navbar

class DescripcionState(rx.State):
    oferta: dict = {}

    def cargar_oferta(self):
        try:
            r = httpx.get("http://localhost:8001/ofertas/1")
            self.oferta = r.json()["data"]
        except:
            self.oferta = {}

def descripcion() -> rx.Component:
    return rx.box(
        navbar(),
        rx.vstack(
            rx.image(
                src=DescripcionState.oferta["imagen_url"],
                width="100%",
                height="400px",
                object_fit="cover",
            ),
            rx.box(
                rx.heading(DescripcionState.oferta["nombre"], size="9"),
                rx.text(DescripcionState.oferta["descripcion"], color="gray", size="4"),
                rx.divider(),
                rx.hstack(
                    rx.box(
                        rx.heading("Detalles", size="6"),
                        rx.text(f"Destino: {DescripcionState.oferta['destino']}"),
                        rx.text(f"Duracion: {DescripcionState.oferta['duracion']}"),
                        rx.text(DescripcionState.oferta["precio"], color="green", weight="bold", size="6"),
                    ),
                    rx.box(
                        rx.heading("Itinerario", size="6"),
                        rx.text("Dia 1: Llegada y bienvenida"),
                        rx.text("Dia 2: Tour por los principales atractivos"),
                        rx.text("Dia 3: Actividades recreativas"),
                        rx.text("Dia 4: Dia libre"),
                        rx.text("Dia 5: Regreso"),
                    ),
                    gap="4em",
                    align="start",
                    width="100%",
                ),
                rx.divider(),
                rx.button(
                    "Hacer una reserva",
                    on_click=rx.redirect("/reservas"),
                    size="3",
                    color_scheme="blue",
                ),
                padding="2em",
                max_width="900px",
                margin="0 auto",
                width="100%",
            ),
            align="center",
            width="100%",
        ),
        on_mount=DescripcionState.cargar_oferta,
    )
