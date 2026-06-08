import mysql.connector
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from datetime import date
import os

app = FastAPI(title="API Turismo", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", "1234"),
        database=os.getenv("DB_NAME", "turismo_db"),
    )

class ReservaIn(BaseModel):
    nombre: str
    email: str
    telefono: Optional[str] = None
    oferta_id: int
    fecha_reserva: date
    cantidad_personas: int = 1
    comentarios: Optional[str] = None

class OfertaIn(BaseModel):
    nombre: str
    descripcion: str
    precio: float
    duracion: str
    destino: str
    imagen_url: Optional[str] = "/descarga.jpeg"

class SugerenciaIn(BaseModel):
    nombre: str
    email: Optional[str] = None
    mensaje: str

@app.get("/")
def health_check():
    return {"ok": True, "mensaje": "API de Turismo funcionando"}

# ── OFERTAS ──────────────────────────────────────────────────────────────────

@app.get("/ofertas")
def get_ofertas():
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM ofertas WHERE activo = 1 ORDER BY id DESC")
        ofertas = cursor.fetchall()
        for o in ofertas:
            o["precio"] = f"RD${o['precio']:,.2f}"
        cursor.close()
        conn.close()
        return {"ok": True, "data": ofertas}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/ofertas/{oferta_id}")
def get_oferta(oferta_id: int):
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM ofertas WHERE id = %s", (oferta_id,))
        oferta = cursor.fetchone()
        cursor.close()
        conn.close()
        if not oferta:
            raise HTTPException(status_code=404, detail="Oferta no encontrada")
        return {"ok": True, "data": oferta}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ofertas", status_code=201)
def crear_oferta(oferta: OfertaIn):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        sql = """
            INSERT INTO ofertas (nombre, descripcion, precio, duracion, destino, imagen_url)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(sql, (oferta.nombre, oferta.descripcion, oferta.precio, oferta.duracion, oferta.destino, oferta.imagen_url))
        conn.commit()
        nuevo_id = cursor.lastrowid
        cursor.close()
        conn.close()
        return {"ok": True, "mensaje": "Oferta creada", "id": nuevo_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/ofertas/{oferta_id}")
def eliminar_oferta(oferta_id: int):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE ofertas SET activo = 0 WHERE id = %s", (oferta_id,))
        conn.commit()
        cursor.close()
        conn.close()
        return {"ok": True, "mensaje": "Oferta eliminada"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ── RESERVAS ─────────────────────────────────────────────────────────────────

@app.post("/reservas", status_code=201)
def crear_reserva(reserva: ReservaIn):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        sql = """
            INSERT INTO reservas
              (nombre, email, telefono, oferta_id, fecha_reserva, cantidad_personas, comentarios)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        valores = (
            reserva.nombre, reserva.email, reserva.telefono,
            reserva.oferta_id, reserva.fecha_reserva,
            reserva.cantidad_personas, reserva.comentarios,
        )
        cursor.execute(sql, valores)
        conn.commit()
        nuevo_id = cursor.lastrowid
        cursor.close()
        conn.close()
        return {"ok": True, "mensaje": "Reserva registrada", "id": nuevo_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/reservas")
def get_reservas():
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT r.*, o.nombre AS oferta_nombre
            FROM reservas r
            LEFT JOIN ofertas o ON r.oferta_id = o.id
            ORDER BY r.fecha_creacion DESC
        """)
        reservas = cursor.fetchall()
        for r in reservas:
            for k, v in r.items():
                if hasattr(v, "isoformat"):
                    r[k] = v.isoformat()
        cursor.close()
        conn.close()
        return {"ok": True, "data": reservas}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/reservas/{reserva_id}")
def get_reserva(reserva_id: int):
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM reservas WHERE id = %s", (reserva_id,))
        reserva = cursor.fetchone()
        cursor.close()
        conn.close()
        if not reserva:
            raise HTTPException(status_code=404, detail="Reserva no encontrada")
        for k, v in reserva.items():
            if hasattr(v, "isoformat"):
                reserva[k] = v.isoformat()
        return {"ok": True, "data": reserva}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/reservas/{reserva_id}/estado")
def actualizar_estado(reserva_id: int, estado: str):
    if estado not in ["pendiente", "confirmada", "cancelada"]:
        raise HTTPException(status_code=400, detail="Estado inválido")
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE reservas SET estado = %s WHERE id = %s", (estado, reserva_id))
        conn.commit()
        cursor.close()
        conn.close()
        return {"ok": True, "mensaje": f"Reserva {estado}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/reservas/{reserva_id}")
def eliminar_reserva(reserva_id: int):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM reservas WHERE id = %s", (reserva_id,))
        conn.commit()
        cursor.close()
        conn.close()
        return {"ok": True, "mensaje": "Reserva eliminada"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ── SUGERENCIAS ──────────────────────────────────────────────────────────────

@app.post("/sugerencias", status_code=201)
def crear_sugerencia(sugerencia: SugerenciaIn):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO sugerencias (nombre, email, mensaje) VALUES (%s, %s, %s)",
            (sugerencia.nombre, sugerencia.email, sugerencia.mensaje)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return {"ok": True, "mensaje": "Sugerencia registrada"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/sugerencias")
def get_sugerencias():
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM sugerencias ORDER BY fecha_creacion DESC")
        sugerencias = cursor.fetchall()
        for s in sugerencias:
            for k, v in s.items():
                if hasattr(v, "isoformat"):
                    s[k] = v.isoformat()
        cursor.close()
        conn.close()
        return {"ok": True, "data": sugerencias}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/sugerencias/{sugerencia_id}")
def eliminar_sugerencia(sugerencia_id: int):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM sugerencias WHERE id = %s", (sugerencia_id,))
        conn.commit()
        cursor.close()
        conn.close()
        return {"ok": True, "mensaje": "Sugerencia eliminada"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
