import reflex as rx
import httpx
import asyncio
import re


class State(rx.State):
    nombre: str = ""
    correo: str = ""
    telefono: str = ""
    enviado: bool = False
    error: bool = False
    error_msg: str = ""
    busqueda: str = ""

    def set_nombre(self, value: str):
        self.nombre = value

    def set_correo(self, value: str):
        self.correo = value

    def set_telefono(self, value: str):
        self.telefono = value

    def set_busqueda(self, value: str):
        self.busqueda = value

    def buscar(self):
        return rx.redirect(f"https://www.google.com/search?q={self.busqueda}+turismo+Republica+Dominicana")

    async def enviar_formulario(self):
        # Validaciones
        partes = self.nombre.strip().split()
        if len(partes) < 2:
            self.error = True
            self.error_msg = "Por favor ingresa nombre y apellido completos."
            return

        if not re.match(r"^[^@]+@[^@]+\.[^@]+$", self.correo.strip()):
            self.error = True
            self.error_msg = "El correo electrónico no es válido."
            return

        if not self.telefono.strip().isdigit() or len(self.telefono.strip()) < 8:
            self.error = True
            self.error_msg = "El teléfono debe tener al menos 8 dígitos."
            return

        self.error = False
        self.error_msg = ""

        try:
            r = httpx.post("http://localhost:8001/reservas", json={
                "nombre": self.nombre,
                "email": self.correo,
                "telefono": self.telefono,
                "oferta_id": 1,
                "fecha_reserva": "2026-07-01",
                "cantidad_personas": 1,
            })
            if r.status_code == 201:
                self.nombre = ""
                self.correo = ""
                self.telefono = ""
                self.enviado = True
                yield
                await asyncio.sleep(3)
                self.enviado = False
                yield
            else:
                self.error = True
                self.error_msg = "Error al registrar la reserva. Intenta de nuevo."
        except:
            self.error = True
            self.error_msg = "No se pudo conectar al servidor."


def navbar():
    return rx.box(
        rx.center(
            rx.hstack(
                rx.link("Inicio", href="/"),
                rx.link("Descripción", href="/descripcion"),
                rx.link("Reservas", href="/reservas"),
                spacing="8",
                font_size="1.1em",
            )
        ),
        padding="20px",
        width="100%",
    )


def inicio():
    return rx.container(
        navbar(),
        rx.center(
            rx.vstack(
                rx.heading("Turismapp", size="9", text_align="center"),
                rx.text(
                    "Plataforma turística enfocada en experiencias organizadas dentro de República Dominicana, "
                    "ofreciendo información clara, destinos destacados y excursiones seguras para todo tipo de viajeros.",
                    text_align="center",
                    max_width="900px",
                ),
                rx.heading("Buscar Destino", size="6"),
                rx.hstack(
                    rx.input(
                        placeholder="Buscar destino turístico...",
                        value=State.busqueda,
                        on_change=State.set_busqueda,
                        width="500px",
                    ),
                    rx.button("Buscar", on_click=State.buscar),
                    justify="center",
                    width="100%",
                ),
                rx.divider(width="100%"),
                rx.heading("Ofertas Turísticas", size="7"),
                rx.card(
                    rx.vstack(
                        rx.image(src="/descarga.jpeg", width="700px", border_radius="10px"),
                        rx.heading("Punta Cana", size="5"),
                        rx.text(
                            "Punta Cana es uno de los destinos más visitados de República Dominicana, reconocido internacionalmente por sus playas de arena blanca, aguas cristalinas y resorts de alto nivel. "
                            "Este destino turístico ofrece una amplia variedad de actividades recreativas, deportes acuáticos, excursiones y experiencias todo incluido, convirtiéndolo en una opción ideal para descanso y entretenimiento.",
                            text_align="center",
                        ),
                    ),
                    width="800px",
                ),
                rx.card(
                    rx.vstack(
                        rx.image(src="/descarga1.jpeg", width="700px", border_radius="10px"),
                        rx.heading("Samaná", size="5"),
                        rx.text(
                            "Samaná es una provincia caracterizada por su impresionante belleza natural, donde se combinan montañas, cascadas, playas vírgenes y una biodiversidad única. "
                            "Es considerada uno de los destinos más importantes del ecoturismo en la República Dominicana, ideal para quienes buscan aventura, naturaleza y tranquilidad.",
                            text_align="center",
                        ),
                    ),
                    width="800px",
                ),
                spacing="6",
                align="center",
                width="100%",
                max_width="1000px",
                margin="0 auto",
            ),
        ),
        padding="30px",
    )


def descripcion():
    return rx.container(
        navbar(),
        rx.center(
            rx.vstack(
                rx.heading("Descripción General", size="8", text_align="center"),
                rx.image(src="/descarga2.jpeg", width="800px", border_radius="10px"),
                rx.text(
                    "Este paquete turístico ofrece una experiencia completa que combina cultura, naturaleza y recreación en un solo recorrido organizado. "
                    "Está diseñado para brindar comodidad, seguridad y una experiencia enriquecedora durante toda la estadía en la República Dominicana.",
                    text_align="center",
                    max_width="900px",
                ),
                rx.heading("Detalles", size="6"),
                rx.text(
                    "Incluye transporte ida y vuelta, alojamiento en hoteles seleccionados, alimentación según el plan contratado y acceso a actividades recreativas y culturales guiadas por personal especializado.",
                    text_align="center",
                    max_width="900px",
                ),
                rx.image(src="/descarga3.jpeg", width="800px", border_radius="10px"),
                rx.heading("Itinerario", size="6"),
                rx.text(
                    "Día 1: llegada, recepción de los participantes y traslado al hotel. "
                    "Día 2: excursiones guiadas a destinos turísticos, actividades culturales y recreativas. "
                    "Día 3: desayuno, tiempo libre y retorno al punto de origen.",
                    text_align="center",
                    max_width="900px",
                ),
                spacing="6",
                align="center",
                width="100%",
                max_width="1000px",
                margin="0 auto",
            ),
        ),
        padding="30px",
    )


def reservas():
    return rx.container(
        navbar(),
        rx.center(
            rx.vstack(
                rx.heading("Reservas", size="8", text_align="center"),
                rx.image(src="/descarga4.jpeg", width="800px", border_radius="10px"),
                rx.heading("Datos de Contacto", size="6"),
                rx.text("Centro de Atención al Cliente Turismapp", font_weight="bold"),
                rx.text("(809) 555-1234", size="5"),
                rx.heading("Detalles de la Actividad", size="6"),
                rx.text(
                    "La reserva incluye un paquete completo de servicios turísticos que abarca transporte, alojamiento y actividades organizadas. "
                    "Todo está diseñado para garantizar una experiencia segura, cómoda y totalmente planificada.",
                    text_align="center",
                    max_width="900px",
                ),
                rx.heading("Descripción de Pago", size="6"),
                rx.text(
                    "Los pagos pueden realizarse mediante transferencia bancaria, tarjetas de crédito o débito, así como otros métodos autorizados. "
                    "Cada transacción es procesada de forma segura para garantizar la protección del cliente.",
                    text_align="center",
                    max_width="900px",
                ),
                rx.heading("Formulario de Reserva", size="6"),
                rx.input(
                    placeholder="Nombre completo",
                    value=State.nombre,
                    on_change=State.set_nombre,
                    width="500px",
                ),
                rx.input(
                    placeholder="Correo electrónico",
                    value=State.correo,
                    on_change=State.set_correo,
                    width="500px",
                ),
                rx.input(
                    placeholder="Número de teléfono",
                    value=State.telefono,
                    on_change=State.set_telefono,
                    width="500px",
                ),
                rx.hstack(
                    rx.button("Enviar", on_click=State.enviar_formulario),
                    rx.cond(
                        State.enviado,
                        rx.text("Reserva registrada exitosamente ✔", color="green", font_weight="bold"),
                    ),
                    rx.cond(
                        State.error,
                        rx.text(State.error_msg, color="red", font_weight="bold"),
                    ),
                    align="center",
                    spacing="4",
                ),
                spacing="6",
                align="center",
                width="100%",
                max_width="600px",
                margin="0 auto",
            ),
        ),
        padding="30px",
    )


app = rx.App()

app.add_page(inicio, route="/")
app.add_page(descripcion, route="/descripcion")
app.add_page(reservas, route="/reservas")
