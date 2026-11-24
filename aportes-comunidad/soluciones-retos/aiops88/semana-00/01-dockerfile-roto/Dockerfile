# 🚨 RETO 1 DOCKER (Nivel Fácil): El contenedor que se apaga solo al instante 🚨
# Síntoma: Haces 'docker build -t reto-docker-01 .' y la imagen compila bien.
#          Sin embargo, al hacer 'docker run -d -p 8080:80 reto-docker-01' y luego 'docker ps',
#          ¡el contenedor NO aparece corriendo!
# Pista: Ejecuta 'docker ps -a' para ver su código de salida.
#        ¿Por qué el proceso de Nginx en CMD se envía a segundo plano y mata al contenedor?
#        Recuerda: en Docker, el proceso principal (PID 1) debe correr en PRIMER PLANO (foreground).

FROM nginx:alpine

COPY index.html /usr/share/nginx/html/index.html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
#Cambio Airy: El contenedor cuando iniciaba Nginx se demonizaba y se cerraba, por eso se agregó -g "daemon off;" al CMD para que el proceso principal corra en primer plano.
#Se mantiene en la forma exec para que el proceso principal PID 1 sea Nginx directamente, porque si lo toma en forma shell entonces ese PID lo toma el shell mismo.
#Para separación de responsabilidades y en este caso por ser contenedor se hace en el Dockerfile: no demonizarse es un requisito del contenedor, no de Nginx. En el nginx.conf no aplicaría porque sería más universal y afectaría a Nginx en cualquier lugar donde corra, no solo en este contenedor.
#Por otra parte, el -g en la línea de comando sí es una directiva de configuración, pero solo aplica a esta ejecución, y esa línea de comando es justamente la que va en el CMD del Dockerfile.
#Los logs del contenedor no mostraban error porque nada falló, pero sí tenían pistas el proceso iniciaba con el PID 1 (1#1) y luego saltaba al 30 (30#30), que lanzaba los workers 31 y 32. Ese salto es el fork del demonio.
