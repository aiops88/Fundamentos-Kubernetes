import http.server
import json
import os
import sys

# ❌ La aplicación requiere obligatoriamente una variable de entorno para inicializarse
TOKEN = os.environ.get("APP_SECRET_TOKEN")
PORT = int(os.environ.get("PORT", 8080))

if not TOKEN:
    print("💥 ERROR FATAL: La variable de entorno obligatoria 'APP_SECRET_TOKEN' no fue proporcionada.", file=sys.stderr)
    print("Pista: Puedes definirla en el Dockerfile con 'ENV' o al correr el contenedor con 'docker run -e APP_SECRET_TOKEN=...'", file=sys.stderr)
    sys.exit(1)


class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        #respuesta = {
        #    "estado": "activo",
        #    "mensaje": "🎉 ¡Excelente! La variable de entorno fue configurada correctamente.",
        #    "token_configurado": TOKEN,
        #    "puerto": PORT
        #}
        respuesta = {
             "estado": "activo",
             "mensaje": "Excelente! La variable de entorno fue configurada correctamente.",
             "token_configurado": True,
        }
        self.wfile.write(json.dumps(respuesta, indent=2, ensure_ascii=False).encode("utf-8"))

    def log_message(self, formato, *args):
        sys.stdout.write(f"[{self.log_date_time_string()}] {formato % args}\n")
        sys.stdout.flush()


if __name__ == "__main__":
    # print(f"🚀 Servidor iniciado con éxito con token '{TOKEN}' en puerto {PORT}...")
    print(f"🚀 Servidor iniciado con éxito (token cargado: sí) en puerto {PORT}...")
    #modificación: se eliminó la impresión del token en el log por seguridad, para no exponerlo en los logs del contenedor.
    servidor = http.server.HTTPServer(("0.0.0.0", PORT), Handler)
    servidor.serve_forever()

# Airy: Fail-fast: La aplicación falla inmediatamente si no encuentra la variable de entorno obligatoria. Esto es útil para detectar problemas de configuración temprano y evitar que la aplicación se ejecute en un estado incorrecto.
# file=sys.stderr) el error va a la salida de error estándar, lo que es útil para diferenciar entre mensajes de log normales y errores críticos. Esto es especialmente importante en entornos de contenedores donde los logs se recopilan y analizan automáticamente.
#   BUILD (docker build)            RUN (docker run)
#  ───────────────────             ────────────────
#  ENV en el Dockerfile     →      -e APP_SECRET_TOKEN=...
#  queda HORNEADO en la            se inyecta al ARRANCAR,
#  imagen, para siempre            cada vez distinto si quieres, sin reconstruir la imagen.

