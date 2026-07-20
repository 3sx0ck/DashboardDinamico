FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN chmod +x entrypoint.sh
# Migra la DB y siembra el admin antes de levantar la API (arranque turnkey).
# Se invoca vía `sh` para no depender del bit +x (el volumen ./backend lo tapa).
CMD ["sh", "entrypoint.sh"]
