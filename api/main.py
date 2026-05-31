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
        host="localhost",
        user="root",
        password="1234",
        database="turismo_db",
    )
 
class ReservaIn(BaseModel):
    nombre: str
    email: str
    telefono: Optional[str] = None
    oferta_id: int
    fecha_reserva: date
    cantidad_personas: int = 1
    comentarios: Optional[str] = None
 
@app.get("/")
def health_check():
    return {"ok": True, "mensaje": "API de Turismo funcionando"}
 
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
            reserva.nombre,
            reserva.email,
            reserva.telefono,
            reserva.oferta_id,
            reserva.fecha_reserva,
            reserva.cantidad_personas,
            reserva.comentarios,
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
 










