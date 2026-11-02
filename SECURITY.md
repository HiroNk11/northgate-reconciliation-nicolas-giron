# Seguridad
No publicar passwords, tokens, claves privadas, cadenas de conexion con secretos,
datos personales ni respaldos en fuentes, issues o pull requests.

Usar el reporte privado de vulnerabilidades de GitHub si esta habilitado. De lo
contrario solicitar al propietario un canal privado sin incluir detalles sensibles
en el mensaje publico. No se garantizan plazos de respuesta ni se declara una
certificacion de seguridad.

Si se confirma una credencial expuesta, revocarla o rotarla primero en su
proveedor. Borrarla del archivo no elimina el historial ni invalida copias previas.
No reescribir historial sin coordinar con el propietario.

La deteccion automatica no reconoce todos los secretos. Las variables de entorno
y los secretos de Actions nunca deben imprimirse en logs ni incluirse en assets
del frontend. Las variables VITE_* y EXPO_PUBLIC_* llegan al cliente: no guardar
secretos en ellas.
