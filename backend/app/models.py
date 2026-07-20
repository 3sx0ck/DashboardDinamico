from datetime import datetime
from sqlalchemy import String, Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.db import Base

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    nombre: Mapped[str] = mapped_column(String)
    password_hash: Mapped[str] = mapped_column(String)
    rol: Mapped[str] = mapped_column(String, default="visitante")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class Upload(Base):
    __tablename__ = "uploads"
    id: Mapped[int] = mapped_column(primary_key=True)
    periodo: Mapped[str] = mapped_column(String, index=True)
    filename: Mapped[str] = mapped_column(String)
    bucket_key: Mapped[str] = mapped_column(String)
    uploaded_by: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class Venta(Base):
    __tablename__ = "ventas"
    id: Mapped[int] = mapped_column(primary_key=True)
    upload_id: Mapped[int] = mapped_column(ForeignKey("uploads.id"), index=True)
    periodo: Mapped[str] = mapped_column(String, index=True)
    torre: Mapped[int] = mapped_column(Integer)
    venta_uf: Mapped[float] = mapped_column(Float, default=0)
    x_recibir_uf: Mapped[float] = mapped_column(Float, default=0)
    pagado_uf: Mapped[float] = mapped_column(Float, default=0)
    escriturados: Mapped[int] = mapped_column(Integer, default=0)

class Stock(Base):
    __tablename__ = "stock"
    id: Mapped[int] = mapped_column(primary_key=True)
    upload_id: Mapped[int] = mapped_column(ForeignKey("uploads.id"), index=True)
    periodo: Mapped[str] = mapped_column(String, index=True)
    torre: Mapped[int] = mapped_column(Integer)
    tipologia: Mapped[str] = mapped_column(String)
    disponible: Mapped[int] = mapped_column(Integer, default=0)
    reservado: Mapped[int] = mapped_column(Integer, default=0)
    promesado: Mapped[int] = mapped_column(Integer, default=0)
    escriturado: Mapped[int] = mapped_column(Integer, default=0)
    bloqueado: Mapped[int] = mapped_column(Integer, default=0)

class Funnel(Base):
    __tablename__ = "funnel"
    id: Mapped[int] = mapped_column(primary_key=True)
    upload_id: Mapped[int] = mapped_column(ForeignKey("uploads.id"), index=True)
    periodo: Mapped[str] = mapped_column(String, index=True)
    ofertas: Mapped[int] = mapped_column(Integer, default=0)
    desistidos: Mapped[int] = mapped_column(Integer, default=0)
    en_curso: Mapped[int] = mapped_column(Integer, default=0)
    promesas: Mapped[int] = mapped_column(Integer, default=0)
    escrituras: Mapped[int] = mapped_column(Integer, default=0)

class EvolucionMensual(Base):
    __tablename__ = "evolucion_mensual"
    id: Mapped[int] = mapped_column(primary_key=True)
    upload_id: Mapped[int] = mapped_column(ForeignKey("uploads.id"), index=True)
    periodo: Mapped[str] = mapped_column(String, index=True)
    mes: Mapped[str] = mapped_column(String)
    ofertas: Mapped[int] = mapped_column(Integer, default=0)
    promesas: Mapped[int] = mapped_column(Integer, default=0)
    escrituras: Mapped[int] = mapped_column(Integer, default=0)

class Canal(Base):
    __tablename__ = "canal"
    id: Mapped[int] = mapped_column(primary_key=True)
    upload_id: Mapped[int] = mapped_column(ForeignKey("uploads.id"), index=True)
    periodo: Mapped[str] = mapped_column(String, index=True)
    canal: Mapped[str] = mapped_column(String)
    reservas: Mapped[int] = mapped_column(Integer, default=0)
    promesas: Mapped[int] = mapped_column(Integer, default=0)
    escrituras: Mapped[int] = mapped_column(Integer, default=0)
    desistidos: Mapped[int] = mapped_column(Integer, default=0)

class MarketingMedio(Base):
    __tablename__ = "marketing_medios"
    id: Mapped[int] = mapped_column(primary_key=True)
    upload_id: Mapped[int] = mapped_column(ForeignKey("uploads.id"), index=True)
    periodo: Mapped[str] = mapped_column(String, index=True)
    medio: Mapped[str] = mapped_column(String)
    cant: Mapped[int] = mapped_column(Integer, default=0)

class MarketingBanco(Base):
    __tablename__ = "marketing_banco"
    id: Mapped[int] = mapped_column(primary_key=True)
    upload_id: Mapped[int] = mapped_column(ForeignKey("uploads.id"), index=True)
    periodo: Mapped[str] = mapped_column(String, index=True)
    banco: Mapped[str] = mapped_column(String)
    pct: Mapped[float] = mapped_column(Float, default=0)

class MarketingKpis(Base):
    __tablename__ = "marketing_kpis"
    id: Mapped[int] = mapped_column(primary_key=True)
    upload_id: Mapped[int] = mapped_column(ForeignKey("uploads.id"), index=True)
    periodo: Mapped[str] = mapped_column(String, index=True)
    visitas_sala: Mapped[int] = mapped_column(Integer, default=0)
    leads_efectivos: Mapped[int] = mapped_column(Integer, default=0)

class AvanceSemanal(Base):
    __tablename__ = "avance_semanal"
    id: Mapped[int] = mapped_column(primary_key=True)
    upload_id: Mapped[int] = mapped_column(ForeignKey("uploads.id"), index=True)
    periodo: Mapped[str] = mapped_column(String, index=True)
    semana: Mapped[str] = mapped_column(String)
    por_firmar: Mapped[int] = mapped_column(Integer, default=0)
    firmadas: Mapped[int] = mapped_column(Integer, default=0)

class GrillaUnidad(Base):
    __tablename__ = "grilla_unidades"
    id: Mapped[int] = mapped_column(primary_key=True)
    upload_id: Mapped[int] = mapped_column(ForeignKey("uploads.id"), index=True)
    periodo: Mapped[str] = mapped_column(String, index=True)
    torre: Mapped[int] = mapped_column(Integer)
    cara: Mapped[str] = mapped_column(String)
    piso: Mapped[int] = mapped_column(Integer)
    depto: Mapped[str] = mapped_column(String)
    estado: Mapped[str] = mapped_column(String)
