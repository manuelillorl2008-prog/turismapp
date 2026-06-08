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

    sug_nombre: str = ""
    sug_email: str = ""
    sug_mensaje: str = ""
    sug_enviado: bool = False
    sug_error: str = ""

    def set_sug_nombre(self, v: str): self.sug_nombre = v
    def set_sug_email(self, v: str): self.sug_email = v
    def set_sug_mensaje(self, v: str): self.sug_mensaje = v

    def set_busqueda(self, value: str):
        self.busqueda = value

    async def enviar_sugerencia(self):
        if not self.sug_nombre.strip() or not self.sug_mensaje.strip():
            self.sug_error = "Completa nombre y mensaje."
            return
        try:
            r = httpx.post("http://localhost:8001/sugerencias", json={
                "nombre": self.sug_nombre,
                "email": self.sug_email,
                "mensaje": self.sug_mensaje,
            })
            if r.status_code == 201:
                self.sug_nombre = ""
                self.sug_email = ""
                self.sug_mensaje = ""
                self.sug_error = ""
                self.sug_enviado = True
                yield
                import asyncio
                await asyncio.sleep(3)
                self.sug_enviado = False
                yield
            else:
                self.sug_error = "Error al enviar sugerencia."
        except:
            self.sug_error = "No se pudo conectar al servidor."

    def buscar(self):
        return rx.redirect(f"https://www.google.com/search?q={self.busqueda}+turismo+Republica+Dominicana")

    async def enviar_formulario(self):
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


class AdminState(rx.State):
    reservas: list[dict] = []
    sugerencias: list[dict] = []
    ofertas: list[dict] = []
    tab: str = "reservas"
    # Formulario nueva oferta
    of_nombre: str = ""
    of_descripcion: str = ""
    of_precio: str = ""
    of_duracion: str = ""
    of_destino: str = ""
    of_imagen: str = "/descarga.jpeg"
    of_msg: str = ""
    of_error: bool = False

    def set_tab(self, t: str):
        self.tab = t

    def set_of_nombre(self, v: str): self.of_nombre = v
    def set_of_descripcion(self, v: str): self.of_descripcion = v
    def set_of_precio(self, v: str): self.of_precio = v
    def set_of_duracion(self, v: str): self.of_duracion = v
    def set_of_destino(self, v: str): self.of_destino = v
    def set_of_imagen(self, v: str): self.of_imagen = v

    async def cargar_datos(self):
        async with httpx.AsyncClient(timeout=10) as client:
            resultados = await asyncio.gather(
                client.get("http://localhost:8001/reservas"),
                client.get("http://localhost:8001/sugerencias"),
                client.get("http://localhost:8001/ofertas"),
                return_exceptions=True,
            )
        r, s, o = resultados
        self.reservas = r.json()["data"] if not isinstance(r, Exception) else []
        self.sugerencias = s.json()["data"] if not isinstance(s, Exception) else []
        self.ofertas = o.json()["data"] if not isinstance(o, Exception) else []

    async def confirmar_reserva(self, reserva_id: int):
        try:
            async with httpx.AsyncClient() as client:
                await client.put(f"http://localhost:8001/reservas/{reserva_id}/estado?estado=confirmada")
            await self.cargar_datos()
        except:
            pass

    async def cancelar_reserva(self, reserva_id: int):
        try:
            async with httpx.AsyncClient() as client:
                await client.put(f"http://localhost:8001/reservas/{reserva_id}/estado?estado=cancelada")
            await self.cargar_datos()
        except:
            pass

    async def eliminar_reserva(self, reserva_id: int):
        try:
            async with httpx.AsyncClient() as client:
                await client.delete(f"http://localhost:8001/reservas/{reserva_id}")
            await self.cargar_datos()
        except:
            pass

    async def eliminar_sugerencia(self, sug_id: int):
        try:
            async with httpx.AsyncClient() as client:
                await client.delete(f"http://localhost:8001/sugerencias/{sug_id}")
            await self.cargar_datos()
        except:
            pass

    async def eliminar_oferta(self, oferta_id: int):
        try:
            async with httpx.AsyncClient() as client:
                await client.delete(f"http://localhost:8001/ofertas/{oferta_id}")
            await self.cargar_datos()
        except:
            pass

    async def crear_oferta(self):
        if not self.of_nombre or not self.of_descripcion or not self.of_precio:
            self.of_error = True
            self.of_msg = "Completa todos los campos obligatorios."
            return
        try:
            async with httpx.AsyncClient() as client:
                r = await client.post("http://localhost:8001/ofertas", json={
                    "nombre": self.of_nombre,
                    "descripcion": self.of_descripcion,
                    "precio": float(self.of_precio),
                    "duracion": self.of_duracion,
                    "destino": self.of_destino,
                    "imagen_url": self.of_imagen,
                })
            if r.status_code == 201:
                self.of_nombre = ""
                self.of_descripcion = ""
                self.of_precio = ""
                self.of_duracion = ""
                self.of_destino = ""
                self.of_error = False
                self.of_msg = "Oferta creada exitosamente."
                await self.cargar_datos()
            else:
                self.of_error = True
                self.of_msg = "Error al crear la oferta."
        except:
            self.of_error = True
            self.of_msg = "No se pudo conectar al servidor."


def color_estado(estado: str) -> str:
    if estado == "confirmada":
        return "green"
    elif estado == "cancelada":
        return "red"
    return "orange"


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
    return rx.box(
        navbar(),
        rx.box(
            rx.box(
                rx.vstack(
                    rx.heading("Turismapp", size="9", color="white"),
                    rx.text(
                        "Descubre los mejores destinos turísticos de la República Dominicana",
                        color="white", size="5", text_align="center", max_width="700px",
                    ),
                    rx.hstack(
                        rx.input(
                            placeholder="¿A dónde quieres ir?",
                            value=State.busqueda,
                            on_change=State.set_busqueda,
                            width="380px",
                            background_color="white",
                            color="black",
                        ),
                        rx.button("Buscar", on_click=State.buscar, size="3"),
                        spacing="2",
                    ),
                    align="center",
                    spacing="5",
                ),
                position="absolute", top="0", left="0", width="100%", height="100%",
                display="flex", align_items="center", justify_content="center",
                background="rgba(0,0,0,0.5)",
            ),
            background_image="url('/descarga.jpeg')",
            background_size="cover", background_position="center",
            height="500px", position="relative", width="100%",
        ),
        rx.box(
            rx.hstack(
                rx.vstack(rx.heading("50+", size="7", color="white"), rx.text("Destinos disponibles", color="gray"), align="center"),
                rx.vstack(rx.heading("1,000+", size="7", color="white"), rx.text("Viajeros satisfechos", color="gray"), align="center"),
                rx.vstack(rx.heading("10+", size="7", color="white"), rx.text("Años de experiencia", color="gray"), align="center"),
                rx.vstack(rx.heading("24/7", size="7", color="white"), rx.text("Atención al cliente", color="gray"), align="center"),
                justify="center", spacing="9", flex_wrap="wrap",
            ),
            padding="3em", width="100%", text_align="center",
        ),
        rx.divider(),
        rx.center(
            rx.vstack(
                rx.heading("Ofertas Turísticas", size="7", text_align="center"),
                rx.text("Explora nuestros destinos más populares", color="gray", text_align="center"),
                rx.hstack(
                    rx.box(
                        rx.box(
                            rx.image(src="/descarga.jpeg", width="100%", height="260px", object_fit="cover"),
                            rx.box(
                                rx.heading("Punta Cana", size="5", color="white"),
                                rx.text("5 días / 4 noches", color="white", size="2"),
                                position="absolute", bottom="0", left="0", padding="1em",
                                background="linear-gradient(transparent, rgba(0,0,0,0.8))", width="100%",
                            ),
                            position="relative", border_radius="12px 12px 0 0", overflow="hidden",
                        ),
                        rx.box(
                            rx.text("Playas de arena blanca, aguas cristalinas y resorts de alto nivel.", color="gray", size="2"),
                            rx.hstack(
                                rx.text("RD$45,000", color="green", font_weight="bold", size="5"),
                                rx.button("Ver más", on_click=rx.redirect("/descripcion"), size="2"),
                                justify="between", align="center", width="100%",
                            ),
                            padding="1em", display="flex", flex_direction="column", gap="0.8em",
                        ),
                        border="1px solid #333", border_radius="12px", width="380px", overflow="hidden",
                    ),
                    rx.box(
                        rx.box(
                            rx.image(src="/descarga1.jpeg", width="100%", height="260px", object_fit="cover"),
                            rx.box(
                                rx.heading("Samaná", size="5", color="white"),
                                rx.text("3 días / 2 noches", color="white", size="2"),
                                position="absolute", bottom="0", left="0", padding="1em",
                                background="linear-gradient(transparent, rgba(0,0,0,0.8))", width="100%",
                            ),
                            position="relative", border_radius="12px 12px 0 0", overflow="hidden",
                        ),
                        rx.box(
                            rx.text("Naturaleza única, cascadas, ballenas jorobadas y playas vírgenes.", color="gray", size="2"),
                            rx.hstack(
                                rx.text("RD$28,000", color="green", font_weight="bold", size="5"),
                                rx.button("Ver más", on_click=rx.redirect("/descripcion"), size="2"),
                                justify="between", align="center", width="100%",
                            ),
                            padding="1em", display="flex", flex_direction="column", gap="0.8em",
                        ),
                        border="1px solid #333", border_radius="12px", width="380px", overflow="hidden",
                    ),
                    spacing="6", flex_wrap="wrap", justify="center", width="100%",
                ),
                spacing="5", width="100%", max_width="900px", align="center",
            ),
            padding="3em 1em", width="100%",
        ),
        rx.divider(),
        rx.center(
            rx.vstack(
                rx.heading("Contacto e Información", size="7", text_align="center"),
                rx.card(
                    rx.vstack(
                        rx.heading("Turismapp RD", size="5"),
                        rx.text("Tu plataforma de confianza para explorar la República Dominicana.", text_align="center"),
                        rx.divider(width="100%"),
                        rx.hstack(
                            rx.vstack(rx.text("📍 Dirección", font_weight="bold"), rx.text("Av. Winston Churchill, Santo Domingo, RD"), align="center"),
                            rx.vstack(rx.text("📞 Teléfono", font_weight="bold"), rx.text("(809) 555-1234"), align="center"),
                            rx.vstack(rx.text("✉️ Correo", font_weight="bold"), rx.text("info@turismapp.com"), align="center"),
                            rx.vstack(rx.text("🕐 Horario", font_weight="bold"), rx.text("Lun - Vie: 8am - 6pm"), align="center"),
                            spacing="8", justify="center", flex_wrap="wrap",
                        ),
                        spacing="4", align="center", width="100%",
                    ),
                    width="800px",
                ),
                spacing="5", width="100%", max_width="900px", align="center",
            ),
            padding="3em 1em", width="100%",
        ),
        width="100%",
    )


def dia_itinerario(numero: str, titulo: str, desc: str) -> rx.Component:
    return rx.hstack(
        rx.box(
            rx.text(numero, color="white", font_weight="bold", font_size="1.2em"),
            background_color="#3b82f6", border_radius="50%",
            width="45px", height="45px", display="flex",
            align_items="center", justify_content="center", flex_shrink="0",
        ),
        rx.vstack(
            rx.text(titulo, font_weight="bold", font_size="1.05em"),
            rx.text(desc, color="gray"),
            align="start", spacing="1",
        ),
        spacing="4", align="start", width="100%",
    )


def descripcion():
    return rx.container(
        navbar(),
        rx.center(
            rx.vstack(
                rx.box(
                    rx.image(src="/descarga2.jpeg", width="100%", height="420px", object_fit="cover"),
                    rx.box(
                        rx.heading("Paquete Turístico República Dominicana", size="8", color="white"),
                        rx.text("Una experiencia completa de cultura, naturaleza y recreación", color="white", size="4"),
                        position="absolute", bottom="0", left="0", padding="2em",
                        background="linear-gradient(transparent, rgba(0,0,0,0.8))", width="100%",
                    ),
                    position="relative", width="100%", max_width="900px",
                    border_radius="16px", overflow="hidden",
                ),
                rx.hstack(
                    rx.card(rx.vstack(rx.text("✈️", font_size="2em"), rx.text("Transporte", font_weight="bold"), rx.text("Ida y vuelta incluido", text_align="center", color="gray"), align="center", spacing="2"), width="200px", text_align="center"),
                    rx.card(rx.vstack(rx.text("🏨", font_size="2em"), rx.text("Alojamiento", font_weight="bold"), rx.text("Hoteles seleccionados", text_align="center", color="gray"), align="center", spacing="2"), width="200px", text_align="center"),
                    rx.card(rx.vstack(rx.text("🍽️", font_size="2em"), rx.text("Alimentación", font_weight="bold"), rx.text("Incluida según el plan", text_align="center", color="gray"), align="center", spacing="2"), width="200px", text_align="center"),
                    rx.card(rx.vstack(rx.text("🎯", font_size="2em"), rx.text("Actividades", font_weight="bold"), rx.text("Tours guiados y culturales", text_align="center", color="gray"), align="center", spacing="2"), width="200px", text_align="center"),
                    spacing="4", flex_wrap="wrap", justify="center",
                ),
                rx.hstack(
                    rx.vstack(
                        rx.heading("Sobre este paquete", size="6"),
                        rx.text("Este paquete turístico ofrece una experiencia completa que combina cultura, naturaleza y recreación en un solo recorrido organizado.", color="gray"),
                        rx.text("Incluye transporte ida y vuelta, alojamiento en hoteles seleccionados, alimentación según el plan contratado y acceso a actividades recreativas.", color="gray"),
                        align="start", spacing="4", width="420px",
                    ),
                    rx.image(src="/descarga3.jpeg", width="420px", border_radius="12px", object_fit="cover"),
                    spacing="6", align="start", flex_wrap="wrap", justify="center",
                ),
                rx.box(
                    rx.vstack(
                        rx.heading("Itinerario", size="6"),
                        dia_itinerario("1", "Llegada y bienvenida", "Recepción de los participantes y traslado al hotel. Cena de bienvenida."),
                        dia_itinerario("2", "Tour y actividades", "Excursiones guiadas a destinos turísticos, actividades culturales y recreativas."),
                        dia_itinerario("3", "Regreso", "Desayuno, tiempo libre, check-out y retorno al punto de origen."),
                        spacing="5", align="start", width="100%",
                    ),
                    border="1px solid #333", border_radius="12px", padding="2em",
                    width="100%", max_width="860px",
                ),
                rx.button("Reservar ahora →", on_click=rx.redirect("/reservas"), size="3", color_scheme="blue"),
                spacing="6", align="center", width="100%", max_width="1000px", margin="0 auto",
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
                rx.image(src="/descarga4.jpeg", width="100%", max_width="700px", height="350px", object_fit="cover", border_radius="16px"),
                rx.hstack(
                    rx.box(
                        rx.vstack(
                            rx.heading("📋 Detalles de la Actividad", size="5"),
                            rx.text("✈️ Transporte ida y vuelta incluido"),
                            rx.text("🏨 Alojamiento en hoteles seleccionados"),
                            rx.text("🍽️ Alimentación según el plan contratado"),
                            rx.text("🎯 Actividades recreativas y culturales"),
                            rx.divider(),
                            rx.heading("💳 Descripción de Pago", size="5"),
                            rx.text("Aceptamos transferencia bancaria, tarjetas de crédito y débito."),
                            rx.text("Cada transacción es procesada de forma segura."),
                            rx.divider(),
                            rx.heading("📞 Contacto", size="5"),
                            rx.text("Centro de Atención al Cliente Turismapp"),
                            rx.text("☎️ (809) 555-1234", font_weight="bold"),
                            rx.text("✉️ info@turismapp.com"),
                            spacing="3", align="start",
                        ),
                        border="1px solid #333", border_radius="12px", padding="2em", width="380px",
                    ),
                    rx.box(
                        rx.vstack(
                            rx.heading("Formulario de Reserva", size="5"),
                            rx.input(placeholder="Nombre completo", value=State.nombre, on_change=State.set_nombre, width="100%"),
                            rx.input(placeholder="Correo electrónico", value=State.correo, on_change=State.set_correo, width="100%"),
                            rx.input(placeholder="Número de teléfono", value=State.telefono, on_change=State.set_telefono, width="100%"),
                            rx.hstack(
                                rx.button("Enviar reserva", on_click=State.enviar_formulario, width="100%"),
                                rx.cond(State.enviado, rx.text("✔ Reserva registrada", color="green", font_weight="bold")),
                                rx.cond(State.error, rx.text(State.error_msg, color="red", font_weight="bold")),
                                align="center", spacing="3", width="100%",
                            ),
                            spacing="4", align="start", width="100%",
                        ),
                        border="1px solid #333", border_radius="12px", padding="2em", width="380px",
                    ),
                    spacing="6", align="start", flex_wrap="wrap", justify="center",
                ),
                rx.divider(),
                rx.box(
                    rx.vstack(
                        rx.heading("💬 Deja tu Sugerencia", size="5"),
                        rx.text("¿Tienes algún comentario o idea para mejorar nuestro servicio?", color="gray"),
                        rx.input(placeholder="Tu nombre *", value=State.sug_nombre, on_change=State.set_sug_nombre, width="100%"),
                        rx.input(placeholder="Tu correo (opcional)", value=State.sug_email, on_change=State.set_sug_email, width="100%"),
                        rx.text_area(placeholder="Tu sugerencia o comentario *", value=State.sug_mensaje, on_change=State.set_sug_mensaje, width="100%"),
                        rx.hstack(
                            rx.button("Enviar sugerencia", on_click=State.enviar_sugerencia, color_scheme="blue"),
                            rx.cond(State.sug_enviado, rx.text("✔ Sugerencia enviada", color="green", font_weight="bold")),
                            rx.cond(State.sug_error != "", rx.text(State.sug_error, color="red", font_weight="bold")),
                            align="center", spacing="3",
                        ),
                        spacing="4", align="start", width="100%",
                    ),
                    border="1px solid #333", border_radius="12px", padding="2em", width="100%", max_width="760px",
                ),
                spacing="6", align="center", width="100%", max_width="900px", margin="0 auto",
            ),
        ),
        padding="30px",
    )


def fila_reserva(r: dict) -> rx.Component:
    return rx.box(
        rx.hstack(
            rx.vstack(
                rx.text(r["nombre"], font_weight="bold"),
                rx.text(r["email"], color="gray", size="2"),
                rx.text(r["telefono"], color="gray", size="2"),
                align="start", spacing="1", width="200px",
            ),
            rx.vstack(
                rx.text(r["oferta_nombre"], size="2"),
                rx.text(r["fecha_reserva"], size="2", color="gray"),
                align="start", spacing="1", width="160px",
            ),
            rx.badge(r["estado"], color_scheme=rx.cond(r["estado"] == "confirmada", "green", rx.cond(r["estado"] == "cancelada", "red", "orange"))),
            rx.hstack(
                rx.button("✔", on_click=AdminState.confirmar_reserva(r["id"]), size="1", color_scheme="green"),
                rx.button("✖", on_click=AdminState.cancelar_reserva(r["id"]), size="1", color_scheme="orange"),
                rx.button("🗑", on_click=AdminState.eliminar_reserva(r["id"]), size="1", color_scheme="red"),
                spacing="2",
            ),
            justify="between", align="center", width="100%", flex_wrap="wrap",
        ),
        border="1px solid #333", border_radius="8px", padding="1em",
        width="100%",
    )


def fila_sugerencia(s: dict) -> rx.Component:
    return rx.box(
        rx.hstack(
            rx.vstack(
                rx.text(s["nombre"], font_weight="bold"),
                rx.text(s["email"], color="gray", size="2"),
                align="start", spacing="1", width="180px",
            ),
            rx.text(s["mensaje"], width="400px", size="2"),
            rx.button("🗑", on_click=AdminState.eliminar_sugerencia(s["id"]), size="1", color_scheme="red"),
            justify="between", align="center", width="100%", flex_wrap="wrap",
        ),
        border="1px solid #333", border_radius="8px", padding="1em", width="100%",
    )


def fila_oferta(o: dict) -> rx.Component:
    return rx.box(
        rx.hstack(
            rx.image(src=o["imagen_url"], width="80px", height="60px", object_fit="cover", border_radius="6px"),
            rx.vstack(
                rx.text(o["nombre"], font_weight="bold"),
                rx.text(o["destino"], color="gray", size="2"),
                align="start", spacing="1",
            ),
            rx.text(o["precio"], color="green", font_weight="bold"),
            rx.button("🗑", on_click=AdminState.eliminar_oferta(o["id"]), size="1", color_scheme="red"),
            justify="between", align="center", width="100%", flex_wrap="wrap",
        ),
        border="1px solid #333", border_radius="8px", padding="1em", width="100%",
    )


def admin():
    return rx.container(
        navbar(),
        rx.center(
            rx.vstack(
                rx.heading("Panel de Administración", size="8", text_align="center"),

                # Tabs
                rx.hstack(
                    rx.button("Reservas", on_click=AdminState.set_tab("reservas"), color_scheme=rx.cond(AdminState.tab == "reservas", "blue", "gray")),
                    rx.button("Sugerencias", on_click=AdminState.set_tab("sugerencias"), color_scheme=rx.cond(AdminState.tab == "sugerencias", "blue", "gray")),
                    rx.button("Ofertas", on_click=AdminState.set_tab("ofertas"), color_scheme=rx.cond(AdminState.tab == "ofertas", "blue", "gray")),
                    rx.button("Nueva Oferta", on_click=AdminState.set_tab("nueva"), color_scheme=rx.cond(AdminState.tab == "nueva", "blue", "gray")),
                    spacing="3", flex_wrap="wrap",
                ),

                # Reservas
                rx.cond(
                    AdminState.tab == "reservas",
                    rx.vstack(
                        rx.heading("Reservas", size="5"),
                        rx.foreach(AdminState.reservas, fila_reserva),
                        spacing="3", width="100%",
                    ),
                ),

                # Sugerencias
                rx.cond(
                    AdminState.tab == "sugerencias",
                    rx.vstack(
                        rx.heading("Sugerencias", size="5"),
                        rx.foreach(AdminState.sugerencias, fila_sugerencia),
                        spacing="3", width="100%",
                    ),
                ),

                # Ofertas
                rx.cond(
                    AdminState.tab == "ofertas",
                    rx.vstack(
                        rx.heading("Ofertas activas", size="5"),
                        rx.foreach(AdminState.ofertas, fila_oferta),
                        spacing="3", width="100%",
                    ),
                ),

                # Nueva oferta
                rx.cond(
                    AdminState.tab == "nueva",
                    rx.box(
                        rx.vstack(
                            rx.heading("Crear nueva oferta", size="5"),
                            rx.input(placeholder="Nombre del destino *", value=AdminState.of_nombre, on_change=AdminState.set_of_nombre, width="100%"),
                            rx.text_area(placeholder="Descripción *", value=AdminState.of_descripcion, on_change=AdminState.set_of_descripcion, width="100%"),
                            rx.input(placeholder="Precio (ej: 45000) *", value=AdminState.of_precio, on_change=AdminState.set_of_precio, width="100%"),
                            rx.input(placeholder="Duración (ej: 3 días / 2 noches)", value=AdminState.of_duracion, on_change=AdminState.set_of_duracion, width="100%"),
                            rx.input(placeholder="Destino (ej: Punta Cana, RD)", value=AdminState.of_destino, on_change=AdminState.set_of_destino, width="100%"),
                            rx.input(placeholder="URL imagen (ej: /descarga.jpeg)", value=AdminState.of_imagen, on_change=AdminState.set_of_imagen, width="100%"),
                            rx.button("Crear oferta", on_click=AdminState.crear_oferta, width="100%", color_scheme="blue"),
                            rx.cond(AdminState.of_msg != "", rx.text(AdminState.of_msg, color=rx.cond(AdminState.of_error, "red", "green"), font_weight="bold")),
                            spacing="4", width="100%",
                        ),
                        border="1px solid #333", border_radius="12px", padding="2em", width="100%",
                    ),
                ),

                spacing="6", width="100%", max_width="900px",
            ),
        ),
        padding="30px",
        on_mount=AdminState.cargar_datos,
    )


app = rx.App()
app.add_page(inicio, route="/")
app.add_page(descripcion, route="/descripcion")
app.add_page(reservas, route="/reservas")
app.add_page(admin, route="/admin")
