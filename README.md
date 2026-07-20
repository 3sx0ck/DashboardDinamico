# DashboardDinamico
Dashboard dinamico para el claudio via claude

## Arranque rápido (pocos comandos)

1. Copia `.env.example` → `.env` y pon tu `NGROK_AUTHTOKEN` ([obtenerlo aquí](https://dashboard.ngrok.com/get-started/your-authtoken)).
2. Levanta todo (stack + túnel público):

```bash
docker compose --profile tunnel up -d
```

3. Obtén la URL pública para compartir:

```bash
curl -s http://localhost:4040/api/tunnels | python3 -c "import sys,json;print(json.load(sys.stdin)['tunnels'][0]['public_url'])"
```

Al arrancar, el backend **migra la DB y crea el usuario admin automáticamente**
(no hay pasos manuales). La primera vez que abras la URL de ngrok verás una
advertencia de ngrok: clic en **Visit Site** (aparece una sola vez).

**Credenciales iniciales:** `admin@pmk.local` / `admin1234` (cámbialas creando
un nuevo admin y borrando este, o edita `.env` antes del primer arranque).

- Admin: sube Excel, gestiona usuarios, ve todo.
- Visitante: solo ve los dashboards.

> La URL gratuita de ngrok cambia en cada reinicio. Para una URL fija se necesita
> un dominio reservado (plan ngrok).

## Desarrollo local (sin túnel)

```bash
docker compose up
```

Frontend: http://localhost:5173 — API proxied vía Vite en `/api`.

## Exponer el frontend con ngrok

1. Copia `.env.example` → `.env` y define `NGROK_AUTHTOKEN` ([cuenta ngrok](https://dashboard.ngrok.com/get-started/your-authtoken)).
2. Levanta stack + túnel:

```bash
docker compose --profile tunnel up
```

3. URL pública: panel ngrok en http://localhost:4040 o `curl -s http://localhost:4040/api/tunnels | jq -r '.tunnels[0].public_url'`.

El proxy de Vite reenvía `/api` al backend dentro de Docker, así quien entra por ngrok no necesita `localhost:8000` en su navegador.

### Sin Docker

Con `npm run dev` en `frontend/` (backend en `:8000`):

```bash
ngrok http 5173
```
