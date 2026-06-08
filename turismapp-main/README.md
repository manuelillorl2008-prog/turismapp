# Turismapp 🌴

Plataforma web de reservas y ofertas turísticas enfocada en destinos dentro de la República Dominicana. Permite a los usuarios explorar destinos, ver descripciones detalladas, registrar reservas y dejar sugerencias a través de formularios conectados a una base de datos MySQL.

---

## Descripción del Proyecto

Turismapp es una aplicación web desarrollada con **Reflex** (frontend) y **FastAPI** (backend/API REST), conectada a una base de datos **MySQL**. El proyecto fue desarrollado como proyecto final del curso de Desarrollo Web.

**Páginas:**
- **Inicio** — buscador de destinos y ofertas turísticas con imágenes
- **Descripción** — descripción general, detalles e itinerario del paquete turístico
- **Reservas** — formulario de reserva y formulario de sugerencias
- **Admin** — panel de administración (accesible solo desde `/admin`)

**Funcionalidades:**
- Búsqueda de destinos (redirige a Google)
- Visualización de ofertas turísticas con imágenes
- Registro de reservas en base de datos MySQL
- Validación de formulario (nombre completo, correo válido, teléfono)
- Envío de sugerencias y comentarios
- Panel de administración para gestionar reservas, sugerencias y ofertas
- API REST con endpoints para consultar ofertas y gestionar reservas

---

## Requisitos

- Python 3.11
- MySQL Server
- Git

---

## Cómo Instalar y Ejecutar

### 1. Clonar el repositorio

```bash
git clone https://github.com/manuelillorl2008-prog/turismapp.git
cd turismapp
```

### 2. Instalar dependencias de Python

```bash
py -3.11 -m pip install reflex fastapi uvicorn mysql-connector-python httpx
```

### 3. Configurar la base de datos

Abre MySQL Workbench y ejecuta el archivo `api/schema.sql`. Esto creará la base de datos `turismo_db` con las tablas `ofertas`, `reservas` y `sugerencias`.

### 4. Iniciar la API

Abre una terminal y corre:

```bash
cd api
py -3.11 -m uvicorn main:app --reload --port 8001
```

La API estará disponible en: `http://localhost:8001`  
Documentación Swagger: `http://localhost:8001/docs`

### 5. Iniciar el Frontend

Abre otra terminal y corre:

```bash
cd turismapp  # carpeta raíz del proyecto
py -3.11 -m reflex run
```

La aplicación estará disponible en: `http://localhost:3000`

---

## Endpoints de la API

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/` | Health check |
| GET | `/ofertas` | Listar todas las ofertas turísticas |
| GET | `/ofertas/{id}` | Obtener una oferta por ID |
| POST | `/ofertas` | Crear una nueva oferta |
| DELETE | `/ofertas/{id}` | Desactivar una oferta |
| POST | `/reservas` | Registrar una nueva reserva |
| GET | `/reservas` | Listar todas las reservas |
| GET | `/reservas/{id}` | Obtener una reserva por ID |
| PUT | `/reservas/{id}/estado` | Confirmar o cancelar una reserva |
| DELETE | `/reservas/{id}` | Eliminar una reserva |
| POST | `/sugerencias` | Registrar una sugerencia |
| GET | `/sugerencias` | Listar todas las sugerencias |
| DELETE | `/sugerencias/{id}` | Eliminar una sugerencia |

---

## Estructura de Carpetas

```
turismapp/
├── api/
│   ├── main.py              # API REST con FastAPI
│   ├── schema.sql           # Estructura y datos iniciales de MySQL
│   └── requirements.txt     # Dependencias de la API
├── assets/
│   ├── descarga.jpeg        # Imagen Punta Cana
│   ├── descarga1.jpeg       # Imagen Samaná
│   ├── descarga2.jpeg       # Imagen descripción
│   ├── descarga3.jpeg       # Imagen itinerario
│   ├── descarga4.jpeg       # Imagen reservas
│   └── favicon.ico          # Ícono de la app
├── turismapp/
│   ├── __init__.py
│   └── turismapp.py         # Páginas del frontend (Inicio, Descripción, Reservas, Admin)
├── .gitignore
├── rxconfig.py              # Configuración de Reflex
├── requirements.txt         # Dependencias del proyecto
├── DOCUMENTACION.md         # Documentación técnica del código
└── README.md                # Este archivo
```

---

## Tecnologías Utilizadas

| Tecnología | Uso |
|------------|-----|
| Reflex | Framework de Python para el frontend |
| FastAPI | Framework para la API REST |
| MySQL | Base de datos relacional |
| Uvicorn | Servidor ASGI para FastAPI |
| httpx | Cliente HTTP para conectar frontend con API |
| Git / GitFlow | Control de versiones |

---

## Ramas GitFlow

| Rama | Descripción |
|------|-------------|
| `main` | Código en producción |
| `develop` | Rama de desarrollo principal |
| `feature/paginas-web` | Desarrollo de las páginas web |

---

## Despliegue
## Despliegue

La API está desplegada en Render:
- **URL de la API:** https://turismapp-api.onrender.com
- **Documentación Swagger:** https://turismapp-api.onrender.com/docs

---

## Créditos

Desarrollado por **Manuel Reyes**, **Gabriel Molina** e **Issmael Santana**  
Documentación elaborada por **Issmael Santana**  
Proyecto Final — Desarrollo Web

---

## Enlaces Útiles

- [Reflex Documentation](https://reflex.dev/docs/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [MySQL Documentation](https://dev.mysql.com/doc/)
- [Repositorio en GitHub](https://github.com/manuelillorl2008-prog/turismapp)
