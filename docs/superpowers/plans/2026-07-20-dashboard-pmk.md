# Dashboard PMK Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Dashboard BI ejecutivo full-stack para el reporte mensual xlsx de Parque Mackenna (PMK), con auth por roles, parser dedicado en Python, persistencia en PostgreSQL y 3 formatos de dashboard en React para que gerencia elija uno.

**Architecture:** Backend FastAPI parsea el xlsx (formato fijo) con pandas/openpyxl → persiste filas normalizadas en PostgreSQL (raw archivado en bucket MinIO) → API con filtros. Frontend React (Vite) consume la API y renderiza KPIs/gráficos (Chart.js) en 3 formatos. Todo orquestado con docker-compose (postgres + minio + backend + frontend).

**Tech Stack:** Python 3.11, FastAPI, SQLAlchemy 2, Alembic, pandas, openpyxl, boto3 (MinIO), passlib+bcrypt, python-jose (JWT), pytest. React 18, Vite, React Router, Tailwind, Chart.js + react-chartjs-2, axios, SheetJS (xlsx), Vitest. Docker Compose.

**Referencia de datos:** ver spec `docs/superpowers/specs/2026-07-20-dashboard-pmk-design.md`. El xlsx es formato fijo; mapeo por coordenada conocida.

---

## Fases

- **F0 — Scaffolding + docker-compose** (esqueleto corriendo)
- **F1 — Modelos DB + migraciones**
- **F2 — Parser dedicado PMK + tests**
- **F3 — Auth + roles + gestión de usuarios**
- **F4 — Uploads (bucket+parse+persist) + API dashboard con filtros**
- **F5 — Frontend React: auth, landing, Formato 1 (Executive) end-to-end**
- **F6 — Formatos 2 (Analítico) y 3 (Narrativo)**

Cada fase deja software funcional y testeable. Commits frecuentes.

---

# F0 — Scaffolding + docker-compose

### Task 0.1: Estructura base del repo

**Files:**
- Create: `backend/requirements.txt`, `backend/main.py`, `backend/app/__init__.py`
- Create: `frontend/package.json` (vía scaffold), `.gitignore`, `README.md` (update)
- Create: `docker-compose.yml`, `.env.example`

- [ ] **Step 1: Crear `.gitignore`**

```gitignore
# python
__pycache__/
*.pyc
.venv/
backend/.venv/
# node
node_modules/
frontend/dist/
# env / data
.env
pgdata/
miniodata/
# os
.DS_Store
```

- [ ] **Step 2: Crear `backend/requirements.txt`**

```
fastapi==0.115.0
uvicorn[standard]==0.30.6
sqlalchemy==2.0.35
alembic==1.13.2
psycopg2-binary==2.9.9
pandas==2.2.2
openpyxl==3.1.5
python-multipart==0.0.9
passlib[bcrypt]==1.7.4
python-jose[cryptography]==3.3.0
boto3==1.35.0
pydantic-settings==2.5.2
pytest==8.3.2
httpx==0.27.2
```

- [ ] **Step 3: Crear `backend/main.py` (health check mínimo)**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Dashboard PMK API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
def health():
    return {"status": "ok"}
```

- [ ] **Step 4: Crear `backend/app/__init__.py`** (vacío)

- [ ] **Step 5: Crear `.env.example`**

```
DATABASE_URL=postgresql+psycopg2://pmk:pmk@postgres:5432/pmk
JWT_SECRET=change-me-in-prod
JWT_EXPIRE_MINUTES=480
MINIO_ENDPOINT=http://minio:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET=pmk-raw
ADMIN_EMAIL=admin@pmk.local
ADMIN_PASSWORD=admin1234
```

- [ ] **Step 6: Commit**

```bash
git add .gitignore backend/requirements.txt backend/main.py backend/app/__init__.py .env.example
git commit -m "chore: scaffold backend base y env"
```

### Task 0.2: Scaffold frontend React (Vite)

**Files:**
- Create: `frontend/` (Vite React + Tailwind)

- [ ] **Step 1: Crear proyecto Vite React**

```bash
cd frontend 2>/dev/null || (npm create vite@latest frontend -- --template react && cd frontend)
npm install
npm install react-router-dom axios chart.js react-chartjs-2 xlsx
npm install -D tailwindcss postcss autoprefixer vitest @testing-library/react @testing-library/jest-dom jsdom
npx tailwindcss init -p
```

- [ ] **Step 2: Configurar Tailwind** — `frontend/tailwind.config.js`

```js
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  darkMode: "class",
  theme: { extend: {} },
  plugins: [],
};
```

- [ ] **Step 3: `frontend/src/index.css`**

```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

- [ ] **Step 4: Verificar dev server**

Run: `cd frontend && npm run dev`
Expected: sirve en http://localhost:5173 sin errores.

- [ ] **Step 5: Commit**

```bash
git add frontend
git commit -m "chore: scaffold frontend React + Vite + Tailwind"
```

### Task 0.3: docker-compose (postgres + minio + backend + frontend)

**Files:**
- Create: `docker-compose.yml`, `backend/Dockerfile`, `frontend/Dockerfile`

- [ ] **Step 1: `backend/Dockerfile`**

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

- [ ] **Step 2: `frontend/Dockerfile`** (dev)

```dockerfile
FROM node:20-slim
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
EXPOSE 5173
CMD ["npm", "run", "dev", "--", "--host"]
```

- [ ] **Step 3: `docker-compose.yml`**

```yaml
services:
  postgres:
    image: postgres:16
    environment:
      POSTGRES_USER: pmk
      POSTGRES_PASSWORD: pmk
      POSTGRES_DB: pmk
    ports: ["5432:5432"]
    volumes: ["./pgdata:/var/lib/postgresql/data"]
  minio:
    image: minio/minio
    command: server /data --console-address ":9001"
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: minioadmin
    ports: ["9000:9000", "9001:9001"]
    volumes: ["./miniodata:/data"]
  backend:
    build: ./backend
    env_file: .env
    ports: ["8000:8000"]
    depends_on: [postgres, minio]
    volumes: ["./backend:/app"]
  frontend:
    build: ./frontend
    ports: ["5173:5173"]
    depends_on: [backend]
    volumes: ["./frontend:/app", "/app/node_modules"]
```

- [ ] **Step 4: Verificar stack levanta**

Run: `cp .env.example .env && docker compose up -d --build && sleep 15 && curl -s http://localhost:8000/api/health`
Expected: `{"status":"ok"}`

- [ ] **Step 5: Commit**

```bash
git add docker-compose.yml backend/Dockerfile frontend/Dockerfile
git commit -m "chore: docker-compose con postgres, minio, backend, frontend"
```

---

# F1 — Modelos DB + migraciones

### Task 1.1: Config + engine SQLAlchemy

**Files:**
- Create: `backend/app/config.py`, `backend/app/db.py`

- [ ] **Step 1: `backend/app/config.py`**

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    jwt_secret: str
    jwt_expire_minutes: int = 480
    minio_endpoint: str
    minio_access_key: str
    minio_secret_key: str
    minio_bucket: str = "pmk-raw"
    admin_email: str
    admin_password: str
    class Config:
        env_file = ".env"

settings = Settings()
```

- [ ] **Step 2: `backend/app/db.py`**

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.config import settings

engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

- [ ] **Step 3: Commit**

```bash
git add backend/app/config.py backend/app/db.py
git commit -m "feat: config settings y engine SQLAlchemy"
```

### Task 1.2: Modelos ORM

**Files:**
- Create: `backend/app/models.py`

- [ ] **Step 1: Escribir modelos** (`backend/app/models.py`)

```python
from datetime import datetime
from sqlalchemy import String, Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db import Base

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    nombre: Mapped[str] = mapped_column(String)
    password_hash: Mapped[str] = mapped_column(String)
    rol: Mapped[str] = mapped_column(String, default="visitante")  # admin|visitante
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
    canal: Mapped[str] = mapped_column(String)  # "Capital Inteligente" | "Brokers"
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
    estado: Mapped[str] = mapped_column(String)  # ESC|PROM|RES|DISP|INVM|BLOQ
```

- [ ] **Step 2: Commit**

```bash
git add backend/app/models.py
git commit -m "feat: modelos ORM (users, uploads, dominio PMK)"
```

### Task 1.3: Alembic + migración inicial

**Files:**
- Create: `backend/alembic.ini`, `backend/alembic/env.py`, migración

- [ ] **Step 1: Inicializar Alembic**

```bash
cd backend && alembic init alembic
```

- [ ] **Step 2: Editar `backend/alembic/env.py`** — apuntar a metadata y URL

Reemplazar la sección de config con:

```python
from app.db import Base
from app.config import settings
from app import models  # noqa: F401  (registra tablas)
target_metadata = Base.metadata
config.set_main_option("sqlalchemy.url", settings.database_url)
```

- [ ] **Step 3: Generar y aplicar migración**

```bash
cd backend && alembic revision --autogenerate -m "init schema" && alembic upgrade head
```
Expected: crea todas las tablas en postgres sin error.

- [ ] **Step 4: Verificar tablas**

Run: `docker compose exec postgres psql -U pmk -d pmk -c "\dt"`
Expected: lista users, uploads, ventas, stock, funnel, etc.

- [ ] **Step 5: Commit**

```bash
git add backend/alembic.ini backend/alembic
git commit -m "feat: alembic + migracion inicial de esquema"
```

---

# F2 — Parser dedicado PMK + tests

> El xlsx es formato fijo. El parser lee por coordenada conocida. Mapeo calibrado
> contra `INFORME PARQUE MACKENNA FINAL.xlsx`. Copiar ese archivo a
> `backend/tests/fixtures/pmk_sample.xlsx` para tests.

**Mapeo de referencia (hoja → celdas):**
- `GESTIÓN JUNIO`: Capital Inteligente mes acumulado funnel en `C12:G12` (2025), filas 12+ por mes col B; Brokers en `M12:Q...`. Reservas/Promesas/Escrituras/Desistidos semana/mes en filas 5-8 (Capital cols C/D, Brokers cols M/N). Tipología (donut) en `I11:J...` y `S11:T...`.
- `Stock PMK`: torres en `A2:E7` (Torre, Deptos, Estac, Bodegas, Total).
- `ESCRITURACIÓN`: bloques por torre — Torre 2 en cols A-B (ESC. Pagado, Esc x pagar, Promesados, Reservados, Disponibles, Escriturados, TOTAL, PIE TOTAL, TOTAL VENTA, X RECIBIR); Torre 5 cols D-E; Torre 3 cols G-H. Tipología por torre (NO/O/NP/P/SP/SO/%/Stock) en bloques a la derecha.
- `Medios (JUNIO)`: `A2:B8` medio→cant, `B10` total.
- `Ofertas x semana (JUNIO)`: grilla por torre; filas = pisos (col A número piso), celdas alternan `depto`/`estado`.
- `AVANCE ESC.`: texto semana en `A1`, por firmar en filas etiquetadas.
- `JULIO`: visitas sala, leads efectivos, distribución banco.

### Task 2.1: Fixture + esqueleto del parser

**Files:**
- Create: `backend/tests/__init__.py`, `backend/tests/fixtures/pmk_sample.xlsx`
- Create: `backend/app/parser/__init__.py`, `backend/app/parser/pmk_parser.py`

- [ ] **Step 1: Copiar fixture**

```bash
mkdir -p backend/tests/fixtures
cp "/Users/gabo/Downloads/20260714 - INFORME PARQUE MACKENNA FINAL.xlsx" backend/tests/fixtures/pmk_sample.xlsx
```

- [ ] **Step 2: Esqueleto `backend/app/parser/pmk_parser.py`**

```python
from __future__ import annotations
import openpyxl
from typing import Any

def parse_pmk(path: str) -> dict[str, Any]:
    wb = openpyxl.load_workbook(path, data_only=True)
    return {
        "meta": _parse_meta(wb),
        "ventas": _parse_ventas(wb),
        "stock": _parse_stock(wb),
        "funnel": _parse_funnel(wb),
        "evolucionMensual": _parse_evolucion(wb),
        "canal": _parse_canal(wb),
        "marketing": _parse_marketing(wb),
        "avanceSemanal": _parse_avance(wb),
        "grillaUnidades": _parse_grilla(wb),
    }
```

- [ ] **Step 3: Commit**

```bash
git add backend/tests backend/app/parser
git commit -m "feat: fixture y esqueleto parser PMK"
```

### Task 2.2: Parser funnel + canal (TDD)

**Files:**
- Test: `backend/tests/test_parser_funnel.py`
- Modify: `backend/app/parser/pmk_parser.py`

- [ ] **Step 1: Test que falla** (`backend/tests/test_parser_funnel.py`)

```python
from app.parser.pmk_parser import parse_pmk

FIX = "tests/fixtures/pmk_sample.xlsx"

def test_funnel_capital_totales():
    data = parse_pmk(FIX)
    f = data["funnel"]
    # Capital Inteligente 2025 acumulado: C12:G12 = 155,51,20,47,25
    assert f["ofertas"] >= 155
    assert set(["ofertas","desistidos","enCurso","promesas","escrituras"]) <= f.keys()

def test_canal_dos_entradas():
    data = parse_pmk(FIX)
    canales = {c["canal"] for c in data["canal"]}
    assert "Capital Inteligente" in canales
    assert "Brokers" in canales
```

- [ ] **Step 2: Correr — debe fallar**

Run: `cd backend && python -m pytest tests/test_parser_funnel.py -v`
Expected: FAIL (`_parse_funnel` no definido / KeyError).

- [ ] **Step 3: Implementar `_parse_funnel` y `_parse_canal`** en `pmk_parser.py`

```python
def _cell(ws, coord):
    v = ws[coord].value
    return v

def _num(v, default=0):
    try:
        return float(v)
    except (TypeError, ValueError):
        return default

def _parse_funnel(wb):
    ws = wb["GESTIÓN JUNIO"]
    # Capital Inteligente acumulado total 2025 (fila 12): Ofertas..Escrituras C..G
    return {
        "ofertas": int(_num(_cell(ws, "C12"))),
        "desistidos": int(_num(_cell(ws, "D12"))),
        "enCurso": int(_num(_cell(ws, "E12"))),
        "promesas": int(_num(_cell(ws, "F12"))),
        "escrituras": int(_num(_cell(ws, "G12"))),
    }

def _parse_canal(wb):
    ws = wb["GESTIÓN JUNIO"]
    # Capital: reservas/promesas/escrituras/desistidos mes = col D filas 5-8
    # Brokers: col N filas 5-8
    def col(c):
        return {
            "reservas": int(_num(_cell(ws, f"{c}5"))),
            "promesas": int(_num(_cell(ws, f"{c}6"))),
            "escrituras": int(_num(_cell(ws, f"{c}7"))),
            "desistidos": int(_num(_cell(ws, f"{c}8"))),
        }
    return [
        {"canal": "Capital Inteligente", **col("D")},
        {"canal": "Brokers", **col("N")},
    ]
```

- [ ] **Step 4: Correr — debe pasar**

Run: `cd backend && python -m pytest tests/test_parser_funnel.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add backend/app/parser/pmk_parser.py backend/tests/test_parser_funnel.py
git commit -m "feat: parser funnel y canal con tests"
```

### Task 2.3: Parser evolución mensual (TDD)

**Files:**
- Test: `backend/tests/test_parser_evolucion.py`
- Modify: `backend/app/parser/pmk_parser.py`

- [ ] **Step 1: Test** (`backend/tests/test_parser_evolucion.py`)

```python
from app.parser.pmk_parser import parse_pmk
FIX = "tests/fixtures/pmk_sample.xlsx"

def test_evolucion_meses():
    data = parse_pmk(FIX)
    ev = data["evolucionMensual"]
    meses = {r["mes"] for r in ev}
    assert {"Enero","Febrero","Marzo"} <= meses
    for r in ev:
        assert {"mes","ofertas","promesas","escrituras"} <= r.keys()
```

- [ ] **Step 2: Correr — falla**

Run: `cd backend && python -m pytest tests/test_parser_evolucion.py -v`
Expected: FAIL

- [ ] **Step 3: Implementar `_parse_evolucion`**

```python
MESES = ["Enero","Febrero","Marzo","Abril","Mayo","Junio","Julio","Agosto",
         "Septiembre","Octubre","Noviembre","Diciembre"]

def _parse_evolucion(wb):
    ws = wb["GESTIÓN JUNIO"]
    out = []
    # Capital Inteligente: filas por mes col B, cols C(ofertas) F(promesas) G(escrituras)
    for row in range(13, 25):
        mes = _cell(ws, f"B{row}")
        if mes in MESES:
            out.append({
                "mes": mes,
                "ofertas": int(_num(_cell(ws, f"C{row}"))),
                "promesas": int(_num(_cell(ws, f"F{row}"))),
                "escrituras": int(_num(_cell(ws, f"G{row}"))),
            })
    return out
```

- [ ] **Step 4: Correr — pasa**

Run: `cd backend && python -m pytest tests/test_parser_evolucion.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add backend/app/parser/pmk_parser.py backend/tests/test_parser_evolucion.py
git commit -m "feat: parser evolucion mensual con tests"
```

### Task 2.4: Parser ventas + stock (TDD)

**Files:**
- Test: `backend/tests/test_parser_ventas_stock.py`
- Modify: `backend/app/parser/pmk_parser.py`

- [ ] **Step 1: Test**

```python
from app.parser.pmk_parser import parse_pmk
FIX = "tests/fixtures/pmk_sample.xlsx"

def test_ventas_por_torre():
    data = parse_pmk(FIX)
    v = data["ventas"]
    assert v["ventaTotalUF"] > 0
    torres = {r["torre"] for r in v["porTorre"]}
    assert {2, 3} <= torres

def test_stock_estructura():
    data = parse_pmk(FIX)
    s = data["stock"]["porTorre"]
    assert len(s) > 0
    for r in s:
        assert {"torre","tipologia","disponible","reservado","promesado","escriturado"} <= r.keys()
```

- [ ] **Step 2: Correr — falla**

Run: `cd backend && python -m pytest tests/test_parser_ventas_stock.py -v`
Expected: FAIL

- [ ] **Step 3: Implementar `_parse_ventas` y `_parse_stock`**

```python
def _parse_ventas(wb):
    ws = wb["ESCRITURACIÓN"]
    # Bloques por torre: T2 cols A-B, T5 cols D-E, T3 cols G-H
    def bloque(col_lbl, col_val, torre):
        # busca filas por etiqueta dentro del bloque
        venta = _num(_cell(ws, f"{col_val}9"))   # TOTAL VENTA aprox; calibrar
        xrec = _num(_cell(ws, f"{col_val}10"))
        return {"torre": torre, "ventaUF": venta, "xRecibirUF": xrec, "escriturados": 0}
    por_torre = [bloque("A","B",2), bloque("D","E",5), bloque("G","H",3)]
    total = sum(t["ventaUF"] for t in por_torre)
    return {
        "ventaTotalUF": total,
        "xRecibirUF": sum(t["xRecibirUF"] for t in por_torre),
        "pagadoUF": 0,
        "porTorre": por_torre,
    }

def _parse_stock(wb):
    # Tipología por torre desde bloques de ESCRITURACIÓN (NO/O/NP/P/SP/SO por 2D-2B,1D-1B,Estudios)
    ws = wb["ESCRITURACIÓN"]
    out = []
    # calibrar coordenadas de cada bloque de tipología por torre
    # placeholder de estructura; el implementador ajusta filas exactas contra el fixture
    return {"porTorre": out}
```

> **Nota de calibración:** las etiquetas de `ESCRITURACIÓN` no están alineadas 1:1
> por fila fija (hay bloques desplazados). El implementador DEBE abrir el fixture,
> localizar por etiqueta (`ESC. Pagado`, `TOTAL VENTA`, `X RECIBIR`, `Promesados`,
> `Reservados`, `Disponibles`) recorriendo la columna del bloque, y ajustar las
> coordenadas. Usar búsqueda por texto de etiqueta en la columna, no fila fija:

```python
def _find_in_col(ws, col, label, max_row=48):
    for r in range(1, max_row+1):
        if str(_cell(ws, f"{col}{r}")).strip().upper() == label.upper():
            return r
    return None
```

Reimplementar `_parse_ventas` usando `_find_in_col` para robustez:

```python
def _parse_ventas(wb):
    ws = wb["ESCRITURACIÓN"]
    def bloque(col_lbl, col_val, torre):
        r_venta = _find_in_col(ws, col_lbl, "TOTAL VENTA")
        r_xrec = _find_in_col(ws, col_lbl, "X RECIBIR")
        venta = _num(_cell(ws, f"{col_val}{r_venta}")) if r_venta else 0
        xrec = _num(_cell(ws, f"{col_val}{r_xrec}")) if r_xrec else 0
        return {"torre": torre, "ventaUF": venta, "xRecibirUF": xrec, "escriturados": 0}
    por_torre = [bloque("A","B",2), bloque("D","E",5), bloque("G","H",3)]
    return {
        "ventaTotalUF": sum(t["ventaUF"] for t in por_torre),
        "xRecibirUF": sum(t["xRecibirUF"] for t in por_torre),
        "pagadoUF": 0,
        "porTorre": por_torre,
    }
```

- [ ] **Step 4: Correr — pasa**

Run: `cd backend && python -m pytest tests/test_parser_ventas_stock.py -v`
Expected: PASS (ajustar coordenadas hasta pasar contra fixture).

- [ ] **Step 5: Commit**

```bash
git add backend/app/parser/pmk_parser.py backend/tests/test_parser_ventas_stock.py
git commit -m "feat: parser ventas y stock (busqueda por etiqueta)"
```

### Task 2.5: Parser marketing + avance + grilla + meta (TDD)

**Files:**
- Test: `backend/tests/test_parser_resto.py`
- Modify: `backend/app/parser/pmk_parser.py`

- [ ] **Step 1: Test**

```python
from app.parser.pmk_parser import parse_pmk
FIX = "tests/fixtures/pmk_sample.xlsx"

def test_marketing_medios():
    m = parse_pmk(FIX)["marketing"]
    medios = {x["medio"] for x in m["medios"]}
    assert {"GOOGLE","WHATSAPP","INSTAGRAM"} & {s.upper() for s in medios}
    assert m["visitasSala"] >= 0

def test_grilla_unidades():
    g = parse_pmk(FIX)["grillaUnidades"]
    assert len(g) > 0
    for u in g[:5]:
        assert {"torre","piso","depto","estado"} <= u.keys()

def test_meta_periodo():
    meta = parse_pmk(FIX)["meta"]
    assert "periodo" in meta
```

- [ ] **Step 2: Correr — falla**

Run: `cd backend && python -m pytest tests/test_parser_resto.py -v`
Expected: FAIL

- [ ] **Step 3: Implementar `_parse_marketing`, `_parse_avance`, `_parse_grilla`, `_parse_meta`**

```python
def _parse_meta(wb):
    return {"proyecto": "PMK", "periodo": "2026-07"}

def _parse_marketing(wb):
    wm = wb["Medios (JUNIO)"]
    medios = []
    for r in range(2, 9):
        nombre = _cell(wm, f"A{r}")
        if nombre:
            medios.append({"medio": str(nombre), "cant": int(_num(_cell(wm, f"B{r}")))})
    wj = wb["JULIO"]
    visitas = int(_num(_find_value_by_label(wj, "VISITAS SALA DE VENTAS")))
    leads = int(_num(_find_value_by_label(wj, "LEADS EFECTIVOS")))
    return {"medios": medios, "visitasSala": visitas, "leadsEfectivos": leads, "banco": []}

def _find_value_by_label(ws, label, span=6):
    for row in ws.iter_rows():
        for i, c in enumerate(row):
            if str(c.value).strip().upper() == label.upper():
                for j in range(i+1, min(i+1+span, len(row))):
                    if isinstance(row[j].value, (int, float)):
                        return row[j].value
    return 0

def _parse_avance(wb):
    ws = wb["AVANCE ESC."]
    semana = str(_cell(ws, "A1") or "")
    por_firmar = int(_num(_find_value_by_label(ws, "Por firmar")))
    return {"semana": semana, "porFirmar": por_firmar, "firmadas": 0}

ESTADO_MAP = {"disponible":"DISP","prom":"PROM","res":"RES","esc":"ESC","invm":"INVM"}

def _parse_grilla(wb):
    ws = wb["Ofertas x semana (JUNIO)"]
    out = []
    for row in ws.iter_rows(min_row=3):
        piso = row[0].value
        if not isinstance(piso, (int, float)):
            continue
        cells = [c.value for c in row[1:] if c.value is not None]
        # pares depto/estado
        for k in range(0, len(cells)-1, 2):
            depto, estado = cells[k], cells[k+1]
            if depto is None or estado is None:
                continue
            est = ESTADO_MAP.get(str(estado).strip().lower(), str(estado).strip().upper()[:4])
            out.append({"torre": 3, "cara": "", "piso": int(piso), "depto": str(depto), "estado": est})
    return out
```

- [ ] **Step 4: Correr — pasa**

Run: `cd backend && python -m pytest tests/test_parser_resto.py -v`
Expected: PASS (ajustar hasta pasar).

- [ ] **Step 5: Commit**

```bash
git add backend/app/parser/pmk_parser.py backend/tests/test_parser_resto.py
git commit -m "feat: parser marketing, avance, grilla, meta"
```

---

# F3 — Auth + roles + gestión de usuarios

### Task 3.1: Hashing + JWT + seed admin

**Files:**
- Create: `backend/app/auth/security.py`, `backend/app/auth/deps.py`, `backend/seed.py`
- Test: `backend/tests/test_security.py`

- [ ] **Step 1: Test** (`backend/tests/test_security.py`)

```python
from app.auth.security import hash_password, verify_password, create_token, decode_token

def test_hash_roundtrip():
    h = hash_password("secret")
    assert h != "secret"
    assert verify_password("secret", h)
    assert not verify_password("bad", h)

def test_token_roundtrip():
    t = create_token({"sub": "1", "rol": "admin"})
    data = decode_token(t)
    assert data["sub"] == "1"
    assert data["rol"] == "admin"
```

- [ ] **Step 2: Correr — falla**

Run: `cd backend && python -m pytest tests/test_security.py -v`
Expected: FAIL

- [ ] **Step 3: Implementar `backend/app/auth/security.py`**

```python
from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import jwt
from app.config import settings

pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(p: str) -> str:
    return pwd.hash(p)

def verify_password(p: str, h: str) -> bool:
    return pwd.verify(p, h)

def create_token(claims: dict) -> str:
    to_encode = claims.copy()
    to_encode["exp"] = datetime.utcnow() + timedelta(minutes=settings.jwt_expire_minutes)
    return jwt.encode(to_encode, settings.jwt_secret, algorithm="HS256")

def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
```

- [ ] **Step 4: Correr — pasa**

Run: `cd backend && python -m pytest tests/test_security.py -v`
Expected: PASS

- [ ] **Step 5: Dependencias de auth `backend/app/auth/deps.py`**

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.db import get_db
from app.auth.security import decode_token
from app import models

oauth2 = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

def current_user(token: str = Depends(oauth2), db: Session = Depends(get_db)) -> models.User:
    try:
        data = decode_token(token)
        user = db.get(models.User, int(data["sub"]))
    except Exception:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "token inválido")
    if not user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "usuario no existe")
    return user

def require_admin(user: models.User = Depends(current_user)) -> models.User:
    if user.rol != "admin":
        raise HTTPException(status.HTTP_403_FORBIDDEN, "requiere admin")
    return user
```

- [ ] **Step 6: Seed admin `backend/seed.py`**

```python
from app.db import SessionLocal
from app import models
from app.auth.security import hash_password
from app.config import settings

def run():
    db = SessionLocal()
    if not db.query(models.User).filter_by(email=settings.admin_email).first():
        db.add(models.User(email=settings.admin_email, nombre="Admin",
                            password_hash=hash_password(settings.admin_password), rol="admin"))
        db.commit()
        print("admin creado")
    else:
        print("admin ya existe")
    db.close()

if __name__ == "__main__":
    run()
```

- [ ] **Step 7: Commit**

```bash
git add backend/app/auth backend/seed.py backend/tests/test_security.py
git commit -m "feat: security (hash/jwt), deps de rol, seed admin"
```

### Task 3.2: Router auth + users

**Files:**
- Create: `backend/app/routers/auth.py`, `backend/app/routers/users.py`, `backend/app/schemas.py`
- Modify: `backend/main.py`
- Test: `backend/tests/test_auth_api.py`

- [ ] **Step 1: Schemas `backend/app/schemas.py`**

```python
from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    email: EmailStr
    nombre: str
    password: str
    rol: str = "visitante"

class UserOut(BaseModel):
    id: int
    email: EmailStr
    nombre: str
    rol: str
    class Config:
        from_attributes = True

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    rol: str
    nombre: str
```

- [ ] **Step 2: Router auth `backend/app/routers/auth.py`**

```python
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.db import get_db
from app import models
from app.auth.security import verify_password, create_token
from app.schemas import TokenOut

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/login", response_model=TokenOut)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter_by(email=form.username).first()
    if not user or not verify_password(form.password, user.password_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "credenciales inválidas")
    token = create_token({"sub": str(user.id), "rol": user.rol})
    return TokenOut(access_token=token, rol=user.rol, nombre=user.nombre)
```

- [ ] **Step 3: Router users `backend/app/routers/users.py`**

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db import get_db
from app import models
from app.auth.deps import require_admin, current_user
from app.auth.security import hash_password
from app.schemas import UserCreate, UserOut

router = APIRouter(prefix="/api/users", tags=["users"])

@router.get("", response_model=list[UserOut])
def list_users(db: Session = Depends(get_db), _: models.User = Depends(require_admin)):
    return db.query(models.User).all()

@router.post("", response_model=UserOut, status_code=201)
def create_user(body: UserCreate, db: Session = Depends(get_db), _: models.User = Depends(require_admin)):
    if body.rol not in ("admin", "visitante"):
        raise HTTPException(400, "rol inválido")
    if db.query(models.User).filter_by(email=body.email).first():
        raise HTTPException(409, "email ya existe")
    u = models.User(email=body.email, nombre=body.nombre,
                    password_hash=hash_password(body.password), rol=body.rol)
    db.add(u); db.commit(); db.refresh(u)
    return u

@router.delete("/{user_id}", status_code=204)
def delete_user(user_id: int, db: Session = Depends(get_db), me: models.User = Depends(require_admin)):
    if user_id == me.id:
        raise HTTPException(400, "no puede eliminarse a sí mismo")
    u = db.get(models.User, user_id)
    if not u:
        raise HTTPException(404, "no existe")
    admins = db.query(models.User).filter_by(rol="admin").count()
    if u.rol == "admin" and admins <= 1:
        raise HTTPException(400, "no puede eliminar el último admin")
    db.delete(u); db.commit()
```

- [ ] **Step 4: Registrar routers en `backend/main.py`**

```python
from app.routers import auth, users
app.include_router(auth.router)
app.include_router(users.router)
```

- [ ] **Step 5: Test API `backend/tests/test_auth_api.py`**

```python
import pytest
from fastapi.testclient import TestClient
from main import app
from app.db import SessionLocal
from app import models
from app.auth.security import hash_password

client = TestClient(app)

@pytest.fixture(autouse=True)
def seed_admin():
    db = SessionLocal()
    db.query(models.User).delete(); db.commit()
    db.add(models.User(email="admin@pmk.local", nombre="A",
                       password_hash=hash_password("admin1234"), rol="admin"))
    db.commit(); db.close()

def _login(email="admin@pmk.local", pw="admin1234"):
    r = client.post("/api/auth/login", data={"username": email, "password": pw})
    return r.json()["access_token"]

def test_login_ok():
    r = client.post("/api/auth/login", data={"username": "admin@pmk.local", "password": "admin1234"})
    assert r.status_code == 200
    assert r.json()["rol"] == "admin"

def test_admin_crea_visitante():
    tok = _login()
    r = client.post("/api/users", json={"email":"v@pmk.local","nombre":"V","password":"x","rol":"visitante"},
                    headers={"Authorization": f"Bearer {tok}"})
    assert r.status_code == 201

def test_visitante_no_crea_usuarios():
    tok = _login()
    client.post("/api/users", json={"email":"v2@pmk.local","nombre":"V","password":"x","rol":"visitante"},
                headers={"Authorization": f"Bearer {tok}"})
    vtok = _login("v2@pmk.local", "x")
    r = client.post("/api/users", json={"email":"z@pmk.local","nombre":"Z","password":"x","rol":"visitante"},
                    headers={"Authorization": f"Bearer {vtok}"})
    assert r.status_code == 403
```

- [ ] **Step 6: Correr tests**

Run: `cd backend && python -m pytest tests/test_auth_api.py -v`
Expected: PASS (requiere DB de test; usar postgres del compose o sqlite de test).

- [ ] **Step 7: Commit**

```bash
git add backend/app/routers backend/app/schemas.py backend/main.py backend/tests/test_auth_api.py
git commit -m "feat: auth login y gestion de usuarios con roles"
```

---

# F4 — Uploads + API dashboard

### Task 4.1: Cliente storage MinIO

**Files:**
- Create: `backend/app/storage.py`
- Test: `backend/tests/test_storage.py`

- [ ] **Step 1: `backend/app/storage.py`**

```python
import boto3
from botocore.client import Config
from app.config import settings

def _client():
    return boto3.client(
        "s3",
        endpoint_url=settings.minio_endpoint,
        aws_access_key_id=settings.minio_access_key,
        aws_secret_access_key=settings.minio_secret_key,
        config=Config(signature_version="s3v4"),
    )

def ensure_bucket():
    c = _client()
    existing = [b["Name"] for b in c.list_buckets().get("Buckets", [])]
    if settings.minio_bucket not in existing:
        c.create_bucket(Bucket=settings.minio_bucket)

def put_raw(key: str, data: bytes):
    ensure_bucket()
    _client().put_object(Bucket=settings.minio_bucket, Key=key, Body=data)
    return key
```

- [ ] **Step 2: Test (integración, requiere minio del compose)**

```python
from app.storage import put_raw, ensure_bucket

def test_put_raw():
    ensure_bucket()
    key = put_raw("test/x.bin", b"hola")
    assert key == "test/x.bin"
```

- [ ] **Step 3: Correr**

Run: `cd backend && python -m pytest tests/test_storage.py -v`
Expected: PASS (con minio arriba).

- [ ] **Step 4: Commit**

```bash
git add backend/app/storage.py backend/tests/test_storage.py
git commit -m "feat: cliente storage MinIO (archiva raw)"
```

### Task 4.2: Persistencia JSON → DB

**Files:**
- Create: `backend/app/persist.py`
- Test: `backend/tests/test_persist.py`

- [ ] **Step 1: `backend/app/persist.py`**

```python
from sqlalchemy.orm import Session
from app import models

def persist_parsed(db: Session, upload: models.Upload, data: dict):
    p = upload.periodo
    uid = upload.id
    f = data["funnel"]
    db.add(models.Funnel(upload_id=uid, periodo=p, ofertas=f["ofertas"], desistidos=f["desistidos"],
                         en_curso=f["enCurso"], promesas=f["promesas"], escrituras=f["escrituras"]))
    for c in data["canal"]:
        db.add(models.Canal(upload_id=uid, periodo=p, canal=c["canal"], reservas=c["reservas"],
                            promesas=c["promesas"], escrituras=c["escrituras"], desistidos=c["desistidos"]))
    for e in data["evolucionMensual"]:
        db.add(models.EvolucionMensual(upload_id=uid, periodo=p, mes=e["mes"], ofertas=e["ofertas"],
                                       promesas=e["promesas"], escrituras=e["escrituras"]))
    for t in data["ventas"]["porTorre"]:
        db.add(models.Venta(upload_id=uid, periodo=p, torre=t["torre"], venta_uf=t["ventaUF"],
                            x_recibir_uf=t["xRecibirUF"], escriturados=t.get("escriturados", 0)))
    for s in data["stock"]["porTorre"]:
        db.add(models.Stock(upload_id=uid, periodo=p, torre=s["torre"], tipologia=s["tipologia"],
                            disponible=s.get("disponible",0), reservado=s.get("reservado",0),
                            promesado=s.get("promesado",0), escriturado=s.get("escriturado",0),
                            bloqueado=s.get("bloqueado",0)))
    m = data["marketing"]
    for md in m["medios"]:
        db.add(models.MarketingMedio(upload_id=uid, periodo=p, medio=md["medio"], cant=md["cant"]))
    for b in m.get("banco", []):
        db.add(models.MarketingBanco(upload_id=uid, periodo=p, banco=b["banco"], pct=b["pct"]))
    db.add(models.MarketingKpis(upload_id=uid, periodo=p, visitas_sala=m["visitasSala"],
                                leads_efectivos=m["leadsEfectivos"]))
    a = data["avanceSemanal"]
    db.add(models.AvanceSemanal(upload_id=uid, periodo=p, semana=a["semana"],
                                por_firmar=a["porFirmar"], firmadas=a.get("firmadas",0)))
    for g in data["grillaUnidades"]:
        db.add(models.GrillaUnidad(upload_id=uid, periodo=p, torre=g["torre"], cara=g.get("cara",""),
                                   piso=g["piso"], depto=g["depto"], estado=g["estado"]))
    db.commit()
```

- [ ] **Step 2: Test** — parsea fixture, persiste, cuenta filas

```python
from app.parser.pmk_parser import parse_pmk
from app.persist import persist_parsed
from app.db import SessionLocal
from app import models

def test_persist_cuenta():
    db = SessionLocal()
    for M in [models.Funnel, models.Canal, models.Venta, models.GrillaUnidad]:
        db.query(M).delete()
    db.query(models.Upload).delete(); db.commit()
    up = models.Upload(periodo="2026-07", filename="f.xlsx", bucket_key="k", uploaded_by=1)
    db.add(up); db.commit(); db.refresh(up)
    data = parse_pmk("tests/fixtures/pmk_sample.xlsx")
    persist_parsed(db, up, data)
    assert db.query(models.Canal).count() == 2
    assert db.query(models.GrillaUnidad).count() > 0
    db.close()
```

- [ ] **Step 3: Correr**

Run: `cd backend && python -m pytest tests/test_persist.py -v`
Expected: PASS

- [ ] **Step 4: Commit**

```bash
git add backend/app/persist.py backend/tests/test_persist.py
git commit -m "feat: persistencia JSON normalizado -> PostgreSQL"
```

### Task 4.3: Router uploads (admin) + dashboard (ambos roles)

**Files:**
- Create: `backend/app/routers/uploads.py`, `backend/app/routers/dashboard.py`
- Modify: `backend/main.py`
- Test: `backend/tests/test_dashboard_api.py`

- [ ] **Step 1: Router uploads `backend/app/routers/uploads.py`**

```python
import uuid, tempfile, os
from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session
from app.db import get_db
from app import models
from app.auth.deps import require_admin
from app.storage import put_raw
from app.parser.pmk_parser import parse_pmk
from app.persist import persist_parsed

router = APIRouter(prefix="/api/uploads", tags=["uploads"])

@router.post("", status_code=201)
async def upload(file: UploadFile = File(...), db: Session = Depends(get_db),
                 admin: models.User = Depends(require_admin)):
    raw = await file.read()
    uid = uuid.uuid4().hex
    key = f"pmk/{uid}/{file.filename}"
    put_raw(key, raw)
    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
        tmp.write(raw); tmp_path = tmp.name
    try:
        data = parse_pmk(tmp_path)
    finally:
        os.unlink(tmp_path)
    periodo = data["meta"]["periodo"]
    up = models.Upload(periodo=periodo, filename=file.filename, bucket_key=key, uploaded_by=admin.id)
    db.add(up); db.commit(); db.refresh(up)
    persist_parsed(db, up, data)
    return {"upload_id": up.id, "periodo": periodo}
```

- [ ] **Step 2: Router dashboard `backend/app/routers/dashboard.py`**

```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db import get_db
from app import models
from app.auth.deps import current_user

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

def _latest_periodo(db):
    row = db.query(models.Upload).order_by(models.Upload.created_at.desc()).first()
    return row.periodo if row else None

@router.get("")
def dashboard(periodo: str | None = None, torre: int | None = None,
              db: Session = Depends(get_db), _: models.User = Depends(current_user)):
    p = periodo or _latest_periodo(db)
    if not p:
        return {"periodo": None, "empty": True}
    def q(M):
        query = db.query(M).filter(M.periodo == p)
        if torre and hasattr(M, "torre"):
            query = query.filter(M.torre == torre)
        return query.all()
    funnel = db.query(models.Funnel).filter_by(periodo=p).first()
    ventas = q(models.Venta)
    stock = q(models.Stock)
    return {
        "periodo": p,
        "kpis": {
            "ventaTotalUF": sum(v.venta_uf for v in ventas),
            "xRecibirUF": sum(v.x_recibir_uf for v in ventas),
            "escriturados": sum(v.escriturados for v in ventas),
        },
        "funnel": None if not funnel else {
            "ofertas": funnel.ofertas, "desistidos": funnel.desistidos,
            "enCurso": funnel.en_curso, "promesas": funnel.promesas, "escrituras": funnel.escrituras},
        "ventas": [{"torre": v.torre, "ventaUF": v.venta_uf, "xRecibirUF": v.x_recibir_uf} for v in ventas],
        "stock": [{"torre": s.torre, "tipologia": s.tipologia, "disponible": s.disponible,
                   "reservado": s.reservado, "promesado": s.promesado, "escriturado": s.escriturado} for s in stock],
        "evolucionMensual": [{"mes": e.mes, "ofertas": e.ofertas, "promesas": e.promesas, "escrituras": e.escrituras}
                              for e in db.query(models.EvolucionMensual).filter_by(periodo=p).all()],
        "canal": [{"canal": c.canal, "reservas": c.reservas, "promesas": c.promesas,
                   "escrituras": c.escrituras, "desistidos": c.desistidos}
                  for c in db.query(models.Canal).filter_by(periodo=p).all()],
        "marketing": {
            "medios": [{"medio": m.medio, "cant": m.cant}
                       for m in db.query(models.MarketingMedio).filter_by(periodo=p).all()],
        },
        "grillaUnidades": [{"torre": g.torre, "piso": g.piso, "depto": g.depto, "estado": g.estado}
                           for g in db.query(models.GrillaUnidad).filter_by(periodo=p).all()],
    }
```

- [ ] **Step 3: Registrar en `backend/main.py`**

```python
from app.routers import uploads, dashboard
app.include_router(uploads.router)
app.include_router(dashboard.router)
```

- [ ] **Step 4: Test `backend/tests/test_dashboard_api.py`**

```python
from fastapi.testclient import TestClient
from main import app
client = TestClient(app)
# reutiliza login helper del test de auth; sube fixture y consulta dashboard

def test_upload_y_dashboard(admin_token):
    with open("tests/fixtures/pmk_sample.xlsx", "rb") as f:
        r = client.post("/api/uploads", files={"file": ("pmk.xlsx", f)},
                        headers={"Authorization": f"Bearer {admin_token}"})
    assert r.status_code == 201
    d = client.get("/api/dashboard", headers={"Authorization": f"Bearer {admin_token}"})
    assert d.status_code == 200
    assert d.json()["kpis"]["ventaTotalUF"] > 0
```

> Añadir fixture `admin_token` en `conftest.py` que siembra admin y hace login.

- [ ] **Step 5: Correr**

Run: `cd backend && python -m pytest tests/test_dashboard_api.py -v`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add backend/app/routers/uploads.py backend/app/routers/dashboard.py backend/main.py backend/tests/test_dashboard_api.py
git commit -m "feat: endpoints upload (admin) y dashboard con filtros"
```

---

# F5 — Frontend React: auth, landing, Formato 1

### Task 5.1: Cliente API + AuthContext

**Files:**
- Create: `frontend/src/api/client.js`, `frontend/src/auth/AuthContext.jsx`

- [ ] **Step 1: `frontend/src/api/client.js`**

```js
import axios from "axios";

const api = axios.create({ baseURL: "http://localhost:8000" });

api.interceptors.request.use((cfg) => {
  const t = localStorage.getItem("token");
  if (t) cfg.headers.Authorization = `Bearer ${t}`;
  return cfg;
});

export async function login(email, password) {
  const body = new URLSearchParams({ username: email, password });
  const { data } = await api.post("/api/auth/login", body);
  return data; // {access_token, rol, nombre}
}
export const getDashboard = (params) => api.get("/api/dashboard", { params }).then((r) => r.data);
export const uploadFile = (file) => {
  const fd = new FormData(); fd.append("file", file);
  return api.post("/api/uploads", fd).then((r) => r.data);
};
export const listUsers = () => api.get("/api/users").then((r) => r.data);
export const createUser = (u) => api.post("/api/users", u).then((r) => r.data);
export default api;
```

- [ ] **Step 2: `frontend/src/auth/AuthContext.jsx`**

```jsx
import { createContext, useContext, useState } from "react";
import { login as apiLogin } from "../api/client";

const AuthCtx = createContext(null);

export function AuthProvider({ children }) {
  const [auth, setAuth] = useState(() => {
    const t = localStorage.getItem("token");
    return t ? { token: t, rol: localStorage.getItem("rol"), nombre: localStorage.getItem("nombre") } : null;
  });
  async function login(email, password) {
    const d = await apiLogin(email, password);
    localStorage.setItem("token", d.access_token);
    localStorage.setItem("rol", d.rol);
    localStorage.setItem("nombre", d.nombre);
    setAuth({ token: d.access_token, rol: d.rol, nombre: d.nombre });
  }
  function logout() { localStorage.clear(); setAuth(null); }
  return <AuthCtx.Provider value={{ auth, login, logout }}>{children}</AuthCtx.Provider>;
}
export const useAuth = () => useContext(AuthCtx);
```

- [ ] **Step 3: Commit**

```bash
git add frontend/src/api frontend/src/auth
git commit -m "feat: cliente API y AuthContext"
```

### Task 5.2: Login + guards + router

**Files:**
- Create: `frontend/src/auth/Login.jsx`, `frontend/src/auth/guards.jsx`
- Modify: `frontend/src/App.jsx`, `frontend/src/main.jsx`

- [ ] **Step 1: `frontend/src/auth/Login.jsx`**

```jsx
import { useState } from "react";
import { useAuth } from "./AuthContext";
import { useNavigate } from "react-router-dom";

export default function Login() {
  const { login } = useAuth();
  const nav = useNavigate();
  const [email, setEmail] = useState(""); const [pw, setPw] = useState(""); const [err, setErr] = useState("");
  async function submit(e) {
    e.preventDefault();
    try { await login(email, pw); nav("/"); }
    catch { setErr("Credenciales inválidas"); }
  }
  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-900">
      <form onSubmit={submit} className="bg-slate-800 p-8 rounded-2xl shadow-xl w-80 space-y-4">
        <h1 className="text-white text-xl font-semibold">Dashboard PMK</h1>
        <input className="w-full p-2 rounded bg-slate-700 text-white" placeholder="Email"
               value={email} onChange={(e) => setEmail(e.target.value)} />
        <input type="password" className="w-full p-2 rounded bg-slate-700 text-white" placeholder="Contraseña"
               value={pw} onChange={(e) => setPw(e.target.value)} />
        {err && <p className="text-red-400 text-sm">{err}</p>}
        <button className="w-full bg-indigo-600 hover:bg-indigo-500 text-white p-2 rounded">Ingresar</button>
      </form>
    </div>
  );
}
```

- [ ] **Step 2: Guards `frontend/src/auth/guards.jsx`**

```jsx
import { Navigate } from "react-router-dom";
import { useAuth } from "./AuthContext";

export function RequireAuth({ children }) {
  const { auth } = useAuth();
  return auth ? children : <Navigate to="/login" replace />;
}
export function RequireAdmin({ children }) {
  const { auth } = useAuth();
  if (!auth) return <Navigate to="/login" replace />;
  return auth.rol === "admin" ? children : <Navigate to="/" replace />;
}
```

- [ ] **Step 3: `frontend/src/App.jsx` con rutas**

```jsx
import { Routes, Route } from "react-router-dom";
import Login from "./auth/Login";
import { RequireAuth, RequireAdmin } from "./auth/guards";
import Landing from "./pages/Landing";
import Executive from "./formats/Executive";
import Users from "./admin/Users";

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/" element={<RequireAuth><Landing /></RequireAuth>} />
      <Route path="/executive" element={<RequireAuth><Executive /></RequireAuth>} />
      <Route path="/admin/users" element={<RequireAdmin><Users /></RequireAdmin>} />
    </Routes>
  );
}
```

- [ ] **Step 4: `frontend/src/main.jsx`**

```jsx
import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import { AuthProvider } from "./auth/AuthContext";
import App from "./App";
import "./index.css";

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <BrowserRouter>
      <AuthProvider><App /></AuthProvider>
    </BrowserRouter>
  </React.StrictMode>
);
```

- [ ] **Step 5: Verificar login en browser**

Run: levantar backend+frontend, ir a http://localhost:5173/login, ingresar admin@pmk.local / admin1234.
Expected: redirige a `/` sin error; token en localStorage.

- [ ] **Step 6: Commit**

```bash
git add frontend/src/auth frontend/src/App.jsx frontend/src/main.jsx
git commit -m "feat: login, guards por rol y router"
```

### Task 5.3: Hook de datos + Uploader + FilterBar

**Files:**
- Create: `frontend/src/hooks/useDashboard.js`, `frontend/src/components/Uploader.jsx`, `frontend/src/components/FilterBar.jsx`, `frontend/src/components/KpiCard.jsx`

- [ ] **Step 1: `frontend/src/hooks/useDashboard.js`**

```js
import { useState, useEffect, useCallback } from "react";
import { getDashboard } from "../api/client";

export function useDashboard() {
  const [filters, setFilters] = useState({});
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const reload = useCallback(() => {
    setLoading(true);
    getDashboard(filters).then(setData).finally(() => setLoading(false));
  }, [filters]);
  useEffect(() => { reload(); }, [reload]);
  return { data, loading, filters, setFilters, reload };
}
```

- [ ] **Step 2: `frontend/src/components/KpiCard.jsx`**

```jsx
export default function KpiCard({ label, value, suffix = "" }) {
  return (
    <div className="bg-white dark:bg-slate-800 rounded-2xl shadow-md p-5">
      <p className="text-slate-500 dark:text-slate-400 text-sm">{label}</p>
      <p className="text-2xl font-bold text-slate-900 dark:text-white mt-1">
        {value}{suffix}
      </p>
    </div>
  );
}
```

- [ ] **Step 3: `frontend/src/components/Uploader.jsx`** (solo admin lo renderiza el padre)

```jsx
import { useState } from "react";
import { uploadFile } from "../api/client";

export default function Uploader({ onDone }) {
  const [busy, setBusy] = useState(false);
  async function onChange(e) {
    const f = e.target.files[0];
    if (!f) return;
    setBusy(true);
    try { await uploadFile(f); onDone?.(); } finally { setBusy(false); e.target.value = ""; }
  }
  return (
    <label className="inline-flex items-center gap-2 bg-indigo-600 hover:bg-indigo-500 text-white px-4 py-2 rounded-xl cursor-pointer">
      {busy ? "Procesando..." : "Subir archivo (.xlsx)"}
      <input type="file" accept=".xlsx,.xls,.csv" className="hidden" onChange={onChange} disabled={busy} />
    </label>
  );
}
```

- [ ] **Step 4: `frontend/src/components/FilterBar.jsx`**

```jsx
export default function FilterBar({ filters, setFilters, torres = [] }) {
  return (
    <div className="flex gap-3 flex-wrap">
      <select className="p-2 rounded-lg bg-slate-100 dark:bg-slate-700 dark:text-white"
              value={filters.torre || ""} onChange={(e) => setFilters({ ...filters, torre: e.target.value || undefined })}>
        <option value="">Todas las torres</option>
        {torres.map((t) => <option key={t} value={t}>Torre {t}</option>)}
      </select>
    </div>
  );
}
```

- [ ] **Step 5: Commit**

```bash
git add frontend/src/hooks frontend/src/components
git commit -m "feat: useDashboard, KpiCard, Uploader, FilterBar"
```

### Task 5.4: Charts (react-chartjs-2) + Formato Executive + Landing

**Files:**
- Create: `frontend/src/charts/FunnelChart.jsx`, `StockTorreChart.jsx`, `EvolucionChart.jsx`, `MediosChart.jsx`, `CanalChart.jsx`
- Create: `frontend/src/formats/Executive.jsx`, `frontend/src/pages/Landing.jsx`

- [ ] **Step 1: Registrar Chart.js una vez** — `frontend/src/charts/setup.js`

```js
import { Chart, CategoryScale, LinearScale, BarElement, LineElement, PointElement, ArcElement, Tooltip, Legend } from "chart.js";
Chart.register(CategoryScale, LinearScale, BarElement, LineElement, PointElement, ArcElement, Tooltip, Legend);
```

- [ ] **Step 2: Charts** — ejemplo `frontend/src/charts/FunnelChart.jsx`

```jsx
import "./setup";
import { Bar } from "react-chartjs-2";

export default function FunnelChart({ funnel }) {
  if (!funnel) return null;
  const data = {
    labels: ["Ofertas", "Desistidos", "En curso", "Promesas", "Escrituras"],
    datasets: [{ label: "Funnel", data: [funnel.ofertas, funnel.desistidos, funnel.enCurso, funnel.promesas, funnel.escrituras],
      backgroundColor: ["#6366f1","#ef4444","#f59e0b","#3b82f6","#10b981"] }],
  };
  return <Bar data={data} options={{ responsive: true, plugins: { legend: { display: false } } }} />;
}
```

`StockTorreChart.jsx` (barra apilada por estado), `EvolucionChart.jsx` (Line con 3 series), `MediosChart.jsx` (Doughnut), `CanalChart.jsx` (Bar agrupada Capital vs Brokers). Cada uno importa `./setup`, recibe su slice de `data` por props y usa colores de la paleta: `#6366f1 #3b82f6 #10b981 #f59e0b #ef4444 #8b5cf6`.

```jsx
// StockTorreChart.jsx
import "./setup";
import { Bar } from "react-chartjs-2";
export default function StockTorreChart({ stock }) {
  const torres = [...new Set(stock.map((s) => s.torre))];
  const estados = ["disponible","reservado","promesado","escriturado"];
  const colores = { disponible:"#10b981", reservado:"#f59e0b", promesado:"#3b82f6", escriturado:"#6366f1" };
  const datasets = estados.map((es) => ({
    label: es, backgroundColor: colores[es],
    data: torres.map((t) => stock.filter((s) => s.torre === t).reduce((a, s) => a + (s[es] || 0), 0)),
  }));
  return <Bar data={{ labels: torres.map((t)=>`Torre ${t}`), datasets }}
              options={{ responsive:true, scales:{ x:{ stacked:true }, y:{ stacked:true } } }} />;
}
```

```jsx
// EvolucionChart.jsx
import "./setup";
import { Line } from "react-chartjs-2";
export default function EvolucionChart({ evolucion }) {
  const labels = evolucion.map((e) => e.mes);
  const mk = (k, c) => ({ label: k, data: evolucion.map((e) => e[k]), borderColor: c, tension: 0.3 });
  return <Line data={{ labels, datasets: [mk("ofertas","#6366f1"), mk("promesas","#3b82f6"), mk("escrituras","#10b981")] }}
               options={{ responsive: true }} />;
}
```

```jsx
// MediosChart.jsx
import "./setup";
import { Doughnut } from "react-chartjs-2";
export default function MediosChart({ medios }) {
  return <Doughnut data={{ labels: medios.map((m)=>m.medio),
    datasets: [{ data: medios.map((m)=>m.cant),
      backgroundColor:["#6366f1","#3b82f6","#10b981","#f59e0b","#ef4444","#8b5cf6"] }] }} />;
}
```

```jsx
// CanalChart.jsx
import "./setup";
import { Bar } from "react-chartjs-2";
export default function CanalChart({ canal }) {
  const labels = canal.map((c)=>c.canal);
  const mk = (k,c)=>({ label:k, backgroundColor:c, data: canal.map((x)=>x[k]) });
  return <Bar data={{ labels, datasets:[mk("reservas","#3b82f6"),mk("promesas","#f59e0b"),mk("escrituras","#10b981")] }}
              options={{ responsive:true }} />;
}
```

- [ ] **Step 3: `frontend/src/formats/Executive.jsx`**

```jsx
import { useAuth } from "../auth/AuthContext";
import { useDashboard } from "../hooks/useDashboard";
import KpiCard from "../components/KpiCard";
import Uploader from "../components/Uploader";
import FilterBar from "../components/FilterBar";
import FunnelChart from "../charts/FunnelChart";
import StockTorreChart from "../charts/StockTorreChart";
import EvolucionChart from "../charts/EvolucionChart";
import MediosChart from "../charts/MediosChart";
import CanalChart from "../charts/CanalChart";

export default function Executive() {
  const { auth } = useAuth();
  const { data, loading, filters, setFilters, reload } = useDashboard();
  if (loading || !data) return <div className="p-8 text-slate-400">Cargando...</div>;
  if (data.empty) return <div className="p-8 text-slate-400">Sin datos. Suba un archivo.</div>;
  const torres = [...new Set((data.ventas || []).map((v) => v.torre))];
  const fmt = (n) => new Intl.NumberFormat("es-CL").format(Math.round(n || 0));
  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-900 p-6 space-y-6">
      <header className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Parque Mackenna · {data.periodo}</h1>
        <div className="flex gap-3">
          <FilterBar filters={filters} setFilters={setFilters} torres={torres} />
          {auth.rol === "admin" && <Uploader onDone={reload} />}
        </div>
      </header>
      <section className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <KpiCard label="Venta total" value={fmt(data.kpis.ventaTotalUF)} suffix=" UF" />
        <KpiCard label="Por recibir" value={fmt(data.kpis.xRecibirUF)} suffix=" UF" />
        <KpiCard label="Escriturados" value={fmt(data.kpis.escriturados)} />
        <KpiCard label="Promesas" value={fmt(data.funnel?.promesas)} />
      </section>
      <section className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card title="Funnel comercial"><FunnelChart funnel={data.funnel} /></Card>
        <Card title="Stock por torre"><StockTorreChart stock={data.stock} /></Card>
        <Card title="Evolución mensual"><EvolucionChart evolucion={data.evolucionMensual} /></Card>
        <Card title="Capital vs Brokers"><CanalChart canal={data.canal} /></Card>
        <Card title="Medios de llegada"><MediosChart medios={data.marketing.medios} /></Card>
      </section>
    </div>
  );
}
function Card({ title, children }) {
  return (
    <div className="bg-white dark:bg-slate-800 rounded-2xl shadow-md p-5">
      <h3 className="text-slate-700 dark:text-slate-200 font-semibold mb-3">{title}</h3>
      {children}
    </div>
  );
}
```

- [ ] **Step 4: `frontend/src/pages/Landing.jsx`** (3 botones)

```jsx
import { Link } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";

const formatos = [
  { to: "/executive", titulo: "Executive Overview", desc: "Una pantalla, KPIs + 6 gráficos" },
  { to: "/analitico", titulo: "Analítico Multi-tab", desc: "Secciones detalladas con tablas" },
  { to: "/narrativo", titulo: "Reporte Narrativo", desc: "Storytelling para reunión" },
];

export default function Landing() {
  const { auth, logout } = useAuth();
  return (
    <div className="min-h-screen bg-slate-900 p-10">
      <div className="flex justify-between items-center mb-10">
        <h1 className="text-3xl font-bold text-white">Dashboard PMK</h1>
        <div className="flex gap-3 items-center">
          {auth.rol === "admin" && <Link to="/admin/users" className="text-indigo-300">Usuarios</Link>}
          <span className="text-slate-400">{auth.nombre} ({auth.rol})</span>
          <button onClick={logout} className="text-slate-300">Salir</button>
        </div>
      </div>
      <div className="grid md:grid-cols-3 gap-6">
        {formatos.map((f) => (
          <Link key={f.to} to={f.to}
                className="bg-slate-800 hover:bg-slate-700 rounded-2xl p-8 shadow-xl transition">
            <h2 className="text-xl font-semibold text-white">{f.titulo}</h2>
            <p className="text-slate-400 mt-2">{f.desc}</p>
          </Link>
        ))}
      </div>
    </div>
  );
}
```

- [ ] **Step 5: Verificar Formato 1 end-to-end**

Run: backend+frontend arriba; login admin; subir `pmk_sample.xlsx`; entrar a Executive.
Expected: KPIs con venta total UF > 0, gráficos renderizan, filtro por torre funciona, recarga tras subir sin reload de página.

- [ ] **Step 6: Commit**

```bash
git add frontend/src/charts frontend/src/formats frontend/src/pages
git commit -m "feat: charts, formato Executive y landing 3 botones"
```

### Task 5.5: Panel admin de usuarios

**Files:**
- Create: `frontend/src/admin/Users.jsx`

- [ ] **Step 1: `frontend/src/admin/Users.jsx`**

```jsx
import { useState, useEffect } from "react";
import { listUsers, createUser } from "../api/client";

export default function Users() {
  const [users, setUsers] = useState([]);
  const [form, setForm] = useState({ email: "", nombre: "", password: "", rol: "visitante" });
  const load = () => listUsers().then(setUsers);
  useEffect(() => { load(); }, []);
  async function submit(e) {
    e.preventDefault();
    await createUser(form);
    setForm({ email: "", nombre: "", password: "", rol: "visitante" });
    load();
  }
  return (
    <div className="min-h-screen bg-slate-900 p-8 text-white">
      <h1 className="text-2xl font-bold mb-6">Usuarios</h1>
      <form onSubmit={submit} className="flex flex-wrap gap-3 mb-8 bg-slate-800 p-4 rounded-xl">
        <input className="p-2 rounded bg-slate-700" placeholder="Email" value={form.email}
               onChange={(e)=>setForm({...form,email:e.target.value})} />
        <input className="p-2 rounded bg-slate-700" placeholder="Nombre" value={form.nombre}
               onChange={(e)=>setForm({...form,nombre:e.target.value})} />
        <input type="password" className="p-2 rounded bg-slate-700" placeholder="Contraseña" value={form.password}
               onChange={(e)=>setForm({...form,password:e.target.value})} />
        <select className="p-2 rounded bg-slate-700" value={form.rol}
                onChange={(e)=>setForm({...form,rol:e.target.value})}>
          <option value="visitante">visitante</option>
          <option value="admin">admin</option>
        </select>
        <button className="bg-indigo-600 px-4 rounded">Crear</button>
      </form>
      <table className="w-full text-left">
        <thead><tr className="text-slate-400"><th>Email</th><th>Nombre</th><th>Rol</th></tr></thead>
        <tbody>{users.map((u)=>(
          <tr key={u.id} className="border-t border-slate-700"><td>{u.email}</td><td>{u.nombre}</td><td>{u.rol}</td></tr>
        ))}</tbody>
      </table>
    </div>
  );
}
```

- [ ] **Step 2: Verificar**

Run: como admin, ir a `/admin/users`, crear un visitante, cerrar sesión, entrar con el visitante.
Expected: visitante ve dashboards pero no ve botón subir ni link Usuarios.

- [ ] **Step 3: Commit**

```bash
git add frontend/src/admin/Users.jsx
git commit -m "feat: panel admin de usuarios"
```

---

# F6 — Formatos 2 (Analítico) y 3 (Narrativo)

### Task 6.1: Formato Analítico (multi-tab)

**Files:**
- Create: `frontend/src/formats/Analitico.jsx`
- Modify: `frontend/src/App.jsx` (ruta `/analitico`)

- [ ] **Step 1: `frontend/src/formats/Analitico.jsx`** — layout con sidebar de secciones (Ventas / Stock / Comercial / Marketing / Escrituración). Cada sección reusa los charts de `../charts` + tablas. Estado local `tab`:

```jsx
import { useState } from "react";
import { useDashboard } from "../hooks/useDashboard";
import StockTorreChart from "../charts/StockTorreChart";
import FunnelChart from "../charts/FunnelChart";
import EvolucionChart from "../charts/EvolucionChart";
import MediosChart from "../charts/MediosChart";
import CanalChart from "../charts/CanalChart";

const TABS = ["Ventas","Stock","Comercial","Marketing"];

export default function Analitico() {
  const { data, loading } = useDashboard();
  const [tab, setTab] = useState("Ventas");
  if (loading || !data || data.empty) return <div className="p-8 text-slate-400">Sin datos.</div>;
  return (
    <div className="min-h-screen flex bg-slate-50 dark:bg-slate-900">
      <aside className="w-56 bg-slate-800 text-white p-4 space-y-2">
        {TABS.map((t)=>(
          <button key={t} onClick={()=>setTab(t)}
                  className={`block w-full text-left px-3 py-2 rounded ${tab===t?"bg-indigo-600":"hover:bg-slate-700"}`}>{t}</button>
        ))}
      </aside>
      <main className="flex-1 p-6">
        {tab==="Ventas" && <Panel title="Evolución mensual"><EvolucionChart evolucion={data.evolucionMensual}/></Panel>}
        {tab==="Stock" && <Panel title="Stock por torre"><StockTorreChart stock={data.stock}/></Panel>}
        {tab==="Comercial" && (<>
          <Panel title="Funnel"><FunnelChart funnel={data.funnel}/></Panel>
          <Panel title="Capital vs Brokers"><CanalChart canal={data.canal}/></Panel></>)}
        {tab==="Marketing" && <Panel title="Medios"><MediosChart medios={data.marketing.medios}/></Panel>}
      </main>
    </div>
  );
}
function Panel({ title, children }) {
  return <div className="bg-white dark:bg-slate-800 rounded-2xl shadow p-5 mb-6">
    <h3 className="font-semibold mb-3 dark:text-white">{title}</h3>{children}</div>;
}
```

- [ ] **Step 2: Añadir ruta** en `App.jsx`: `<Route path="/analitico" element={<RequireAuth><Analitico/></RequireAuth>} />`

- [ ] **Step 3: Verificar** — navegar tabs, charts renderizan.

- [ ] **Step 4: Commit**

```bash
git add frontend/src/formats/Analitico.jsx frontend/src/App.jsx
git commit -m "feat: formato Analitico multi-tab"
```

### Task 6.2: Formato Narrativo + Heatmap torres

**Files:**
- Create: `frontend/src/formats/Narrativo.jsx`, `frontend/src/charts/HeatmapTorre.jsx`
- Modify: `frontend/src/App.jsx` (ruta `/narrativo`)

- [ ] **Step 1: `frontend/src/charts/HeatmapTorre.jsx`** — grilla piso×depto coloreada por estado (CSS grid, no Chart.js)

```jsx
const COLOR = { ESC:"#10b981", PROM:"#3b82f6", RES:"#f59e0b", DISP:"#64748b", INVM:"#8b5cf6", BLOQ:"#ef4444" };
export default function HeatmapTorre({ grilla }) {
  const pisos = [...new Set(grilla.map((u)=>u.piso))].sort((a,b)=>b-a);
  return (
    <div className="space-y-1">
      {pisos.map((p)=>(
        <div key={p} className="flex gap-1 items-center">
          <span className="w-8 text-xs text-slate-400">{p}</span>
          {grilla.filter((u)=>u.piso===p).map((u)=>(
            <span key={u.depto} title={`${u.depto} ${u.estado}`}
                  className="w-6 h-6 rounded" style={{ background: COLOR[u.estado] || "#334155" }} />
          ))}
        </div>
      ))}
    </div>
  );
}
```

- [ ] **Step 2: `frontend/src/formats/Narrativo.jsx`** — scroll con números gigantes + heatmap protagonista

```jsx
import { useDashboard } from "../hooks/useDashboard";
import HeatmapTorre from "../charts/HeatmapTorre";
import EvolucionChart from "../charts/EvolucionChart";

export default function Narrativo() {
  const { data, loading } = useDashboard();
  if (loading || !data || data.empty) return <div className="p-8 text-slate-400">Sin datos.</div>;
  const fmt = (n)=>new Intl.NumberFormat("es-CL").format(Math.round(n||0));
  return (
    <div className="bg-slate-900 text-white">
      <section className="min-h-[60vh] flex flex-col justify-center items-center">
        <p className="text-slate-400 uppercase tracking-widest">Parque Mackenna · {data.periodo}</p>
        <h1 className="text-7xl font-black mt-4">{fmt(data.kpis.ventaTotalUF)} UF</h1>
        <p className="text-slate-400 mt-2">Venta total</p>
      </section>
      <section className="min-h-screen p-10">
        <h2 className="text-3xl font-bold mb-6">Estado de unidades</h2>
        <HeatmapTorre grilla={data.grillaUnidades} />
      </section>
      <section className="min-h-screen p-10">
        <h2 className="text-3xl font-bold mb-6">Evolución comercial</h2>
        <div className="max-w-3xl"><EvolucionChart evolucion={data.evolucionMensual} /></div>
      </section>
    </div>
  );
}
```

- [ ] **Step 3: Añadir ruta** `/narrativo` en `App.jsx`.

- [ ] **Step 4: Verificar** los 3 botones de landing navegan a los 3 formatos con datos reales.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/formats/Narrativo.jsx frontend/src/charts/HeatmapTorre.jsx frontend/src/App.jsx
git commit -m "feat: formato Narrativo + heatmap torres"
```

---

## Cierre

- [ ] Verificar `docker compose up` levanta todo y flujo completo funciona (login → subir → 3 formatos).
- [ ] Merge `feature/dashboard-pmk` → `dev` (usar skill finishing-a-development-branch).
- [ ] Mostrar avance a Gabo; decidir formato final.

## Notas de riesgo

- **Parser (F2):** mayor riesgo. Las coordenadas de `ESCRITURACIÓN` y `Ofertas x
  semana` requieren calibración fina contra el fixture (búsqueda por etiqueta, no
  fila fija). Iterar test hasta pasar con valores reales.
- **Tests con DB:** los tests de API/persist requieren postgres. Usar el postgres
  del compose o configurar sqlite en `conftest.py` para tests unitarios rápidos.
- **PII:** el fixture tiene nombres reales. NO subir el fixture a repos públicos;
  añadir a `.gitignore` si el repo es público, o usar datos anonimizados.
