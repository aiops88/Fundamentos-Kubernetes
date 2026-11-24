# 🚨 RETO 3 DOCKER: El contenedor que corre como root (Falla en Kubernetes Seguro) 🚨
#
# Síntoma:
# 1. Al correr 'docker run --rm reto-root whoami', verás que responde 'root' (UID 0).
# 2. Al aplicar este Pod en Kubernetes con políticas de seguridad estrictas (pod-seguro.yaml),
#    el Pod falla con error:
#    'CreateContainerConfigError: container has runAsNonRoot and image will run as root'
#
# Pista:
# Para cumplir con las mejores prácticas de seguridad de contenedores (Least Privilege),
# debes:
# 1. Crear un grupo y un usuario no privilegiado (ej. 'appuser' con UID 10001).
# 2. Asignar los archivos al usuario usando '--chown' en la instrucción COPY.
# 3. Declarar la instrucción 'USER' antes de ejecutar el comando CMD.

FROM python:3.12-alpine

WORKDIR /app

RUN addgroup -g 10001 -S appgroup && \
    adduser -u 10001 -S appuser -G appgroup

COPY --chown=appuser:appgroup app.py .

# # Airy: Traje el patrón del reto 2 porque ese Dockerfile ya corría como usuario no privilegiado. En este reto el foco es la seguridad de no correr como root.
# Lo que te llevás: en un Dockerfile, primero hacés todo lo que necesita root (instalar, crear usuarios, permisos) y al final bajamos de privilegio con USER.

EXPOSE 8080

USER appuser

CMD ["python", "app.py"]
