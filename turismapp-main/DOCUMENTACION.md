# Documentación Técnica — Turismapp

Desarrollado por: **Manuel Reyes**, **Gabriel Molina** e **Issmael Santana**  
Documentación elaborada por: **Issmael Santana**  
Proyecto Final — Desarrollo Web

---

## Índice
1. [Descripción General](#descripción-general)
2. [Arquitectura del Proyecto](#arquitectura-del-proyecto)
3. [Base de Datos](#base-de-datos)
4. [API REST — main.py](#api-rest--mainpy)
5. [Frontend — turismapp.py](#frontend--turismapppy)
6. [Configuración — rxconfig.py](#configuración--rxconfigpy)

---

## 1. Descripción General

Turismapp es una plataforma web de reservas turísticas desarrollada con:
- **Reflex** — framework Python para el frontend
- **FastAPI** — framework Python para la API REST
- **MySQL** — base de datos relacional

El usuario puede explorar destinos, ver descripciones, registrar reservas y dejar sugerencias. El panel de administración permite gestionar reservas, sugerencias y ofertas.

---

## 2. Arquitectura del Proyecto

```
turismapp/
├── api/
│   ├── main.py              ← API REST (FastAPI)
│   ├── schema.sql           ← Estructura de la base de datos
│   └── requirements.txt     ← Dependencias de la API
├── assets/                  ← Imágenes del sitio
├── turismapp/
│   └── turismapp.py         ← Frontend completo (Reflex)
├── rxconfig.py              ← Configuración de Reflex
└── requirements.txt         ← Dependencias globales
```

**Flujo de datos:**
```
Navegador → Reflex (puerto 3000) → FastAPI (puerto 8001) → MySQL
```

---

## 3. Base de Datos

**Archivo:** `api/schema.sql`

### Tabla `ofertas`
Almacena los paquetes turísticos disponibles.

| Columna | Tipo | Descripción |
|---------|------|-------------|
| `id` | INT AUTO_INCREMENT | Identificador único |
| `nombre` | VARCHAR(200) | Nombre del paquete |
| `descripcion` | TEXT | Descripción del destino |
| `precio` | DECIMAL(10,2) | Precio en pesos dominicanos |
| `duracion` | VARCHAR(100) | Duración del viaje |
| `destino` | VARCHAR(200) | Ciudad o región del destino |
| `imagen_url` | VARCHAR(500) | Ruta de la imagen |
| `activo` | TINYINT(1) | 1 = visible, 0 = oculto |
| `creado_en` | TIMESTAMP | Fecha de creación automática |

### Tabla `reservas`
Almacena las reservas registradas por los usuarios.

| Columna | Tipo | Descripción |
|---------|------|-------------|
| `id` | INT AUTO_INCREMENT | Identificador único |
| `nombre` | VARCHAR(200) | Nombre completo del cliente |
| `email` | VARCHAR(200) | Correo electrónico |
| `telefono` | VARCHAR(30) | Número de teléfono |
| `oferta_id` | INT | Llave foránea → tabla `ofertas` |
| `fecha_reserva` | DATE | Fecha del viaje |
| `cantidad_personas` | INT | Número de personas |
| `comentarios` | TEXT | Notas adicionales |
| `estado` | VARCHAR(20) | pendiente / confirmada / cancelada |
| `fecha_creacion` | TIMESTAMP | Fecha de registro automática |

### Tabla `sugerencias`
Almacena los comentarios enviados por los usuarios desde la página de Reservas.

| Columna | Tipo | Descripción |
|---------|------|-------------|
| `id` | INT AUTO_INCREMENT | Identificador único |
| `nombre` | VARCHAR(200) | Nombre del usuario |
| `email` | VARCHAR(200) | Correo electrónico (opcional) |
| `mensaje` | TEXT | Contenido de la sugerencia |
| `fecha_creacion` | TIMESTAMP | Fecha de registro automática |

---

## 4. API REST — `api/main.py`

**Framework:** FastAPI  
**Puerto:** 8001 (local), 10000 (Render)

### Configuración inicial

```python
app = FastAPI(title="API Turismo", version="1.0.0")
```
Crea la instancia de la aplicación FastAPI.

```python
app.add_middleware(CORSMiddleware, allow_origins=["*"], ...)
```
Permite que el frontend Reflex se comunique con la API desde cualquier origen.

### Conexión a la base de datos

```python
def get_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", "1234"),
        database=os.getenv("DB_NAME", "turismo_db"),
    )
```
Usa variables de entorno para las credenciales. Si no están definidas, usa los valores por defecto. Esto permite que funcione tanto en local como en Render.

### Modelos de datos

```python
class ReservaIn(BaseModel): ...
class OfertaIn(BaseModel): ...
class SugerenciaIn(BaseModel): ...
```
Pydantic valida automáticamente que los datos enviados tengan el formato correcto antes de procesarlos.

### Endpoints de Ofertas

#### `GET /ofertas`
Devuelve todas las ofertas activas (`activo = 1`) ordenadas por ID descendente. Formatea el precio con comas (`RD$45,000.00`).

#### `GET /ofertas/{oferta_id}`
Devuelve una oferta específica por ID. Retorna 404 si no existe.

#### `POST /ofertas`
Crea una nueva oferta turística. Recibe nombre, descripción, precio, duración, destino e imagen. Retorna el ID de la oferta creada.

#### `DELETE /ofertas/{oferta_id}`
Desactiva una oferta (`activo = 0`) en vez de eliminarla físicamente, para preservar el historial de reservas.

### Endpoints de Reservas

#### `POST /reservas`
Recibe los datos del formulario de reservas, los inserta en MySQL y devuelve el ID de la nueva reserva. Retorna código 201.

#### `GET /reservas`
Devuelve todas las reservas con el nombre de la oferta asociada (JOIN con tabla ofertas). Convierte fechas a string para JSON.

#### `GET /reservas/{reserva_id}`
Devuelve una reserva específica por ID.

#### `PUT /reservas/{reserva_id}/estado`
Actualiza el estado de una reserva. Los estados válidos son: `pendiente`, `confirmada`, `cancelada`. Usado desde el panel de admin.

#### `DELETE /reservas/{reserva_id}`
Elimina una reserva permanentemente de la base de datos.

### Endpoints de Sugerencias

#### `POST /sugerencias`
Registra una sugerencia enviada desde la página de Reservas. Requiere nombre y mensaje. El email es opcional.

#### `GET /sugerencias`
Devuelve todas las sugerencias ordenadas por fecha descendente.

#### `DELETE /sugerencias/{sugerencia_id}`
Elimina una sugerencia permanentemente.

---

## 5. Frontend — `turismapp/turismapp.py`

**Framework:** Reflex  
**Puerto:** 3000

### Estado global — `State`

```python
class State(rx.State):
    nombre, correo, telefono       # Formulario de reserva
    sug_nombre, sug_email, sug_mensaje  # Formulario de sugerencias
    busqueda                       # Buscador de destinos
    enviado, error, error_msg      # Control de mensajes
```
Centraliza todos los datos de los formularios. Reflex sincroniza este estado entre el backend Python y el frontend React automáticamente.

#### `buscar()`
Redirige al usuario a Google con el término buscado más "turismo Republica Dominicana".

#### `enviar_formulario()`
Función asíncrona que:
1. Valida nombre completo (mínimo dos palabras)
2. Valida formato de correo con expresión regular
3. Valida teléfono (mínimo 8 dígitos)
4. Hace POST a `/reservas` con los datos
5. Si responde 201, limpia el formulario y muestra éxito por 3 segundos
6. Si hay error, muestra el mensaje correspondiente

#### `enviar_sugerencia()`
Valida que nombre y mensaje no estén vacíos, luego hace POST a `/sugerencias`. Limpia el formulario al enviar exitosamente.

### Estado del admin — `AdminState`

```python
class AdminState(rx.State):
    reservas, sugerencias, ofertas  # Datos cargados de la API
    tab                             # Pestaña activa del panel
    of_nombre, of_descripcion, ...  # Formulario nueva oferta
```

#### `cargar_datos()`
Llama a los endpoints `GET /reservas`, `GET /sugerencias` y `GET /ofertas` para cargar todos los datos al entrar al panel.

#### `confirmar_reserva(id)` / `cancelar_reserva(id)`
Llaman a `PUT /reservas/{id}/estado` con el estado correspondiente y recargan los datos.

#### `eliminar_reserva(id)` / `eliminar_sugerencia(id)` / `eliminar_oferta(id)`
Llaman al endpoint DELETE correspondiente y recargan los datos.

#### `crear_oferta()`
Valida los campos obligatorios (nombre, descripción, precio) y hace POST a `/ofertas`. Muestra mensaje de éxito o error.

### Función `navbar()`
Barra de navegación con enlaces a Inicio, Descripción y Reservas. El enlace a Admin fue removido intencionalmente — solo es accesible escribiendo `/admin` en el navegador.

### Páginas

#### `inicio()`
- Hero con imagen de fondo, overlay oscuro, título y buscador
- Estadísticas (destinos, viajeros, años, atención)
- Tarjetas de ofertas lado a lado con imagen, precio y botón
- Sección de contacto con dirección, teléfono, correo y horario

#### `descripcion()`
- Hero con imagen y texto encima con gradiente
- 4 tarjetas de características (transporte, alojamiento, alimentación, actividades)
- Texto descriptivo e imagen lado a lado
- Itinerario con círculos numerados en azul (componente `dia_itinerario`)
- Botón "Reservar ahora →"

#### `reservas()`
- Imagen hero
- Dos columnas: detalles/pago/contacto y formulario de reserva
- Formulario de sugerencias al final

#### `admin()`
Panel con 4 pestañas:
- **Reservas** — lista con botones ✔ confirmar, ✖ cancelar, 🗑 eliminar
- **Sugerencias** — lista con botón 🗑 eliminar
- **Ofertas** — lista de ofertas activas con botón 🗑 eliminar
- **Nueva Oferta** — formulario para crear nuevos destinos

### Componentes reutilizables

#### `dia_itinerario(numero, titulo, descripcion)`
Muestra un paso del itinerario con un círculo azul numerado a la izquierda y el texto a la derecha.

#### `fila_reserva(r)` / `fila_sugerencia(s)` / `fila_oferta(o)`
Componentes del panel admin que muestran cada registro con sus botones de acción.

---

## 6. Configuración — `rxconfig.py`

```python
config = rx.Config(
    app_name="turismapp",
    plugins=[
        rx.plugins.SitemapPlugin(),
        rx.plugins.TailwindV4Plugin(),
    ]
)
```
- `app_name` — nombre del módulo principal de Reflex
- `SitemapPlugin` — genera sitemap.xml automáticamente para SEO
- `TailwindV4Plugin` — habilita Tailwind CSS v4 para estilos

---

## Cómo ejecutar localmente

```bash
# Terminal 1 — API
cd api
py -3.11 -m uvicorn main:app --reload --port 8001

# Terminal 2 — Frontend
cd turismapp  # carpeta raíz
py -3.11 -m reflex run
```

## Despliegue en Render

La API está desplegada en Render:
- **Root Directory:** `api`
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `uvicorn main:app --host 0.0.0.0 --port 10000`
