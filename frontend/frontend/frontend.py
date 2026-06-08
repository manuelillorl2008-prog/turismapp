import reflex as rx
from frontend.pages.inicio import inicio
from frontend.pages.descripcion import descripcion
from frontend.pages.reservas import reservas

app = rx.App()
app.add_page(inicio, route="/")
app.add_page(descripcion, route="/descripcion")
app.add_page(reservas, route="/reservas")