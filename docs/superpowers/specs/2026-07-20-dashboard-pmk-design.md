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
[Frontend Vite + Tailwind + Chart.js]  --upload xlsx-->  [Backend FastAPI + pandas]
        |  render KPIs/charts/filtros        <--JSON normalizado--   parser dedicado PMK
        |  SheetJS = preview crudo (secundario)
   docker-compose levanta ambos
```

- **Backend (Python, FastAPI + pandas/openpyxl):** endpoint `POST /api/parse`
  recibe el xlsx (multipart), aplica el mapeo dedicado PMK y devuelve un JSON
  normalizado. pandas maneja de forma confiable celdas combinadas y multi-tabla.
- **Frontend (Vite + Tailwind + Chart.js):** cargador visible (.xlsx/.xls/.csv),
  envía al backend, renderiza. **Recarga sin reload** = re-POST + re-render.
  SheetJS/XLSX se incluye como preview cliente de hojas crudas (rol secundario;
  el mapeo pesado lo hace Python).
- **Docker:** `docker-compose` levanta frontend + backend con un comando.

### Razonamiento SheetJS vs Python
El requerimiento pedía lectura con SheetJS. Dado que el archivo es muy sucio,
Python/pandas da resultados mucho más confiables para el mapeo dedicado. SheetJS
permanece para lectura/preview cliente. Si se prefiere SheetJS puro (sin
backend), es un cambio de alcance a decidir.

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
    main.py            # FastAPI app + /api/parse
    pmk_parser.py      # mapeo dedicado por hoja
    requirements.txt
  frontend/
    index.html         # landing 3 botones
    src/
      data/api.js      # upload -> backend, SheetJS preview
      components/       # KPIs, charts, filtros, uploader
      formats/          # format1-executive, format2-analitico, format3-narrativo
      charts/           # wrappers Chart.js
    tailwind/vite config
  docker-compose.yml
  docs/superpowers/specs/2026-07-20-dashboard-pmk-design.md
```

## 11. Flujo de trabajo

Opus (planificación/evaluación, incl. subagentes) → Haiku (implementación
mecánica) → mostrar avance corriendo en docker. Branches: `master` → `dev` →
`feature/dashboard-pmk`.

## 12. Fuera de alcance (YAGNI)

- Auth/login (herramienta interna, fuera de alcance inicial).
- Persistencia en DB (se trabaja sobre el archivo subido).
- Fallback genérico para archivos arbitrarios (elegido: mapeo dedicado A).
- Edición de datos desde el dashboard (solo lectura/visualización).
