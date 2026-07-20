# Dashboard PMK — Diseño

**Fecha:** 2026-07-20
**Proyecto:** Dashboard BI ejecutivo para reporte inmobiliario Parque Mackenna (PMK)
**Audiencia:** Gerencia inmobiliaria
**Repo:** DashboardDinamico · branch `feature/dashboard-pmk`

## 1. Propósito

Convertir el reporte mensual xlsx de Parque Mackenna (formato curado, 13 hojas)
en un dashboard BI premium para gerencia. La gerencia sube el xlsx del mes y ve
KPIs, gráficos y filtros sin recargar la página. Se implementan **3 formatos de
dashboard** en la landing (3 botones); gerencia evalúa y elige uno después.

## 2. Fuente de datos

Archivo: `INFORME PARQUE MACKENNA FINAL.xlsx`. **No es tabla plana**: es un
reporte con múltiples tablas heterogéneas por hoja, celdas combinadas, headers
mezclados y español de dominio inmobiliario.

Hojas relevantes y su rol:

| Hoja | Contenido | Uso |
|------|-----------|-----|
| GESTIÓN JUNIO | Funnel comercial + canal (Capital Inteligente vs Brokers), acumulado 2024-2026 | Funnel, canal, evolución mensual |
| JULIO | Ventas mensuales, leads, visitas sala, distribución banco | Marketing, leads |
| Medios (JUNIO) | Medios de llegada (Google/WhatsApp/Instagram/etc.) | Chart marketing |
| Ofertas x semana (JUNIO) | Grilla piso×depto×estado por torre | Heatmap unidades |
| Stock PMK | Unidades por torre (deptos/estac/bodegas) + strip center | Stock, venta UF |
| ESCRITURACIÓN | Venta total UF, x recibir, pagado, por torre y tipología | KPIs ventas, escrituración |
| AVANCE ESC. | Avance semanal de firmas | Avance semanal |
| ESC. | Detalle escrituración con **nombres de clientes (PII)** | Tabla detalle (interno) |
| Hoja7 / Hoja1 | Reservas / Desistimientos (listas con fecha) | Tablas y velocidad venta |

### ⚠️ PII
La hoja `ESC.` contiene nombres reales de clientes. Herramienta **interna** de
gerencia. **Nunca** publicar como artifact público ni enviar a servicios
externos. Datos se procesan localmente (backend en la misma red / local).

## 3. Arquitectura

```
[Frontend Vite+Tailwind+Chart.js] --login--> [Backend FastAPI]
        |                                        |  auth (users en postgres)
        |  --upload xlsx (multipart)------------>|  1. guarda raw en bucket (archivo)
        |                                        |  2. parser dedicado PMK (pandas)
        |                                        |  3. escribe filas normalizadas en PostgreSQL
        |  <--JSON desde DB (KPIs/charts)---------|
   docker-compose: frontend + backend + postgres + bucket (MinIO)
```

Flujo: login → subir xlsx → backend **archiva el raw en bucket interno** (solo
archivo, no se reutiliza) → **parsea con pandas** → **persiste filas
normalizadas en PostgreSQL** → dashboard consulta la DB (no el archivo).

- **Backend (Python, FastAPI + pandas/openpyxl + SQLAlchemy):**
  - `POST /api/auth/login` — auth simple contra tabla `users`.
  - `POST /api/uploads` — recibe xlsx, archiva raw en bucket, parsea, persiste en DB, devuelve `upload_id` + periodo.
  - `GET /api/dashboard?periodo=&torre=&tipologia=&estado=&canal=` — lee de la DB, aplica filtros, devuelve JSON normalizado para KPIs/charts.
  - pandas maneja de forma confiable celdas combinadas y multi-tabla.
- **Frontend (Vite + Tailwind + Chart.js):** login, cargador visible
  (.xlsx/.xls/.csv), envía al backend, renderiza desde la DB. **Recarga sin
  reload** = subir nuevo archivo → re-fetch → re-render. SheetJS/XLSX queda como
  preview cliente de hojas crudas (rol secundario; el mapeo pesado lo hace Python).
- **Persistencia:** PostgreSQL (datos normalizados) + bucket interno MinIO
  (S3-compatible) para archivar el raw. El raw **no** se reutiliza tras leerlo.
- **Docker:** `docker-compose` levanta frontend + backend + postgres + minio.

### Razonamiento SheetJS vs Python
El requerimiento pedía lectura con SheetJS. Dado que el archivo es muy sucio,
Python/pandas da resultados mucho más confiables para el mapeo dedicado. SheetJS
permanece para lectura/preview cliente. Si se prefiere SheetJS puro (sin
backend), es un cambio de alcance a decidir.

## 3b. Auth y roles

Login por usuario/contraseña contra tabla `users` en PostgreSQL. Contraseñas
**hasheadas** (bcrypt/argon2, nunca texto plano). Sesión vía JWT (cookie
httpOnly) o token. Endpoints protegidos (requieren sesión válida).

**Dos roles:**

| Acción | admin | visitante |
|--------|:-----:|:---------:|
| Ver dashboard + filtros | ✓ | ✓ |
| Subir xlsx (crear periodo) | ✓ | ✗ |
| Crear/listar/eliminar usuarios | ✓ | ✗ |

- **admin:** gestiona usuarios (los crea para que puedan ingresar), sube
  archivos, ve dashboards.
- **visitante:** solo ve dashboards y usa filtros.

Sin registro público: los usuarios los crea un admin. Un admin inicial se crea
por `seed.py`. Endpoints admin protegidos por chequeo de rol en backend (no solo
UI). Frontend oculta acciones no permitidas según rol.

Endpoints de gestión de usuarios (admin):
- `POST /api/users` — crear usuario (email, nombre, password, rol)
- `GET /api/users` — listar
- `DELETE /api/users/{id}` — eliminar (no puede eliminarse a sí mismo / último admin)

## 3c. Persistencia

- **Bucket (MinIO, S3-compatible interno):** cada upload guarda el archivo crudo
  con key `pmk/{upload_id}/{filename}`. Propósito: archivo/auditoría. **No** se
  vuelve a leer para el dashboard.
- **PostgreSQL:** tablas normalizadas (ver §4b). Cada carga crea un registro en
  `uploads` (metadata: id, periodo, filename, bucket_key, usuario, fecha) y filas
  en las tablas de dominio ligadas por `upload_id`. El dashboard consulta estas
  tablas (con filtros), no el archivo.

## 4. Modelo normalizado (salida del parser)

```json
{
  "meta": { "proyecto": "PMK", "periodo": "2026-07", "generado": "..." },
  "ventas": {
    "ventaTotalUF": 0, "xRecibirUF": 0, "pagadoUF": 0,
    "porTorre": [{ "torre": 2, "ventaUF": 0, "xRecibirUF": 0, "escriturados": 0 }]
  },
  "stock": {
    "porTorre": [{ "torre": 3, "tipologia": "2D-2B",
      "disponible": 0, "reservado": 0, "promesado": 0, "escriturado": 0, "bloqueado": 0 }]
  },
  "funnel": { "ofertas": 0, "desistidos": 0, "enCurso": 0, "promesas": 0, "escrituras": 0 },
  "evolucionMensual": [{ "mes": "Enero", "ofertas": 0, "promesas": 0, "escrituras": 0 }],
  "canal": [{ "canal": "Capital Inteligente", "reservas": 0, "promesas": 0, "escrituras": 0, "desistidos": 0 }],
  "marketing": {
    "medios": [{ "medio": "WhatsApp", "cant": 0 }],
    "visitasSala": 0, "leadsEfectivos": 0,
    "banco": [{ "banco": "Consorcio", "pct": 0 }]
  },
  "avanceSemanal": { "semana": "6-10 jul", "porFirmar": 0, "firmadas": 0 },
  "grillaUnidades": [{ "torre": 3, "cara": "ORIENTE", "piso": 23, "depto": "2314", "estado": "ESC" }]
}
```

## 4b. Esquema PostgreSQL

El parser produce el JSON de §4; el backend lo materializa en tablas relacionales.
Todas las tablas de dominio llevan `upload_id` (FK) y `periodo` para filtrar.

- `users` (id, email, password_hash, nombre, rol `admin|visitante`, created_at)
- `uploads` (id, periodo, filename, bucket_key, uploaded_by → users.id, created_at)
- `ventas` (id, upload_id, periodo, torre, venta_uf, x_recibir_uf, pagado_uf, escriturados)
- `stock` (id, upload_id, periodo, torre, tipologia, disponible, reservado, promesado, escriturado, bloqueado)
- `funnel` (id, upload_id, periodo, ofertas, desistidos, en_curso, promesas, escrituras)
- `evolucion_mensual` (id, upload_id, periodo, mes, ofertas, promesas, escrituras)
- `canal` (id, upload_id, periodo, canal, reservas, promesas, escrituras, desistidos)
- `marketing_medios` (id, upload_id, periodo, medio, cant)
- `marketing_banco` (id, upload_id, periodo, banco, pct)
- `marketing_kpis` (id, upload_id, periodo, visitas_sala, leads_efectivos)
- `avance_semanal` (id, upload_id, periodo, semana, por_firmar, firmadas)
- `grilla_unidades` (id, upload_id, periodo, torre, cara, piso, depto, estado)

Migraciones con Alembic. El dashboard filtra por el `periodo` más reciente por
defecto (o el seleccionado).

## 5. KPIs (automáticos)

Venta total UF · % vendido · Unidades escrituradas/promesadas/reservadas/disponibles ·
% avance escrituración · X recibir UF · Conversión funnel (mes) · Velocidad venta (reservas/mes).

## 6. Gráficos (Chart.js)

Funnel comercial · Stock por torre (barra apilada por estado) · Evolución mensual
ofertas/promesas/escrituras (línea) · Mix tipología (donut) · Medios de llegada
(barra/donut) · Capital vs Brokers (barra agrupada) · Heatmap grilla de torres
(piso×depto coloreado por estado) · Distribución por banco (donut).

## 7. Filtros dinámicos

Torre · Tipología · Periodo (mes/trimestre) · Estado · Canal. Los filtros
recalculan KPIs y gráficos sin recargar.

## 8. Los 3 formatos (landing = 3 botones)

Los tres consumen el **mismo** JSON normalizado y el mismo cargador/filtros.
Difieren en layout/experiencia:

1. **Executive Overview** — una pantalla: fila de KPIs arriba + grid de 6 gráficos.
   Dark premium, minimal, cards con sombras suaves. Para lectura rápida de gerencia.
2. **Analítico Multi-tab** — sidebar de navegación por secciones
   (Ventas / Stock / Comercial-Funnel / Marketing / Escrituración). Cada tab con
   gráficos detallados + tablas. Para análisis profundo.
3. **Reporte Narrativo** — scroll tipo storytelling, números gigantes por sección,
   heatmap de torres como protagonista. Para proyectar en reunión / pantalla grande.

## 9. Diseño visual

Premium tipo SaaS/BI. Modo oscuro (default) + claro. Cards, sombras suaves,
bordes redondeados, responsive (desktop gerencia + tablet). Tailwind como sistema.

## 10. Estructura propuesta

```
DashboardDinamico/
  backend/
    main.py            # FastAPI app, routers
    auth.py            # login, hashing, JWT
    pmk_parser.py      # mapeo dedicado por hoja -> JSON normalizado
    storage.py         # cliente MinIO (archiva raw)
    db.py              # SQLAlchemy engine/session
    models.py          # tablas (users, uploads, dominio)
    persist.py         # JSON normalizado -> filas DB
    routers/
      auth.py          # POST /api/auth/login
      users.py         # gestión usuarios (admin: crear/listar/eliminar)
      uploads.py       # POST /api/uploads (admin)
      dashboard.py     # GET /api/dashboard (filtros, ambos roles)
    alembic/           # migraciones
    seed.py            # usuario admin inicial
    requirements.txt
  frontend/
    index.html         # landing 3 botones (post-login)
    src/
      data/api.js      # login, upload -> backend, fetch dashboard, SheetJS preview
      auth/            # pantalla login + estado de sesión/rol
      admin/           # panel gestión usuarios (solo admin)
      components/      # KPIs, charts, filtros, uploader (uploader solo admin)
      formats/         # format1-executive, format2-analitico, format3-narrativo
      charts/          # wrappers Chart.js
    tailwind/vite config
  docker-compose.yml   # frontend + backend + postgres + minio
  docs/superpowers/specs/2026-07-20-dashboard-pmk-design.md
```

## 11. Flujo de trabajo

Opus (planificación/evaluación, incl. subagentes) → Haiku (implementación
mecánica) → mostrar avance corriendo en docker. Branches: `master` → `dev` →
`feature/dashboard-pmk`.

## 12. Fuera de alcance (YAGNI)

- Registro público y permisos más allá de 2 roles (admin/visitante). Usuarios
  creados por admin; admin inicial por seed.
- Reutilizar el archivo raw del bucket tras leerlo (solo archivo/auditoría).
- Fallback genérico para archivos arbitrarios (elegido: mapeo dedicado A).
- Edición de datos desde el dashboard (solo lectura/visualización).
