# RULES

REGLA MAS IMPORTANTE: TIENES QUE TENER MUCHO CUIDADO AL USAR LA VARIABLE $HOME EN UNA ELIMINACION SIN ESPECIFICAR EL PATH

1. No crees commits ni hagas `push` salvo que el usuario lo autorice explícitamente. Usar un worktree no implica autorización para crear commits.
2. Escribe código claro y mantenible. Aplica Clean Code y SOLID cuando aporten valor, respetando las convenciones existentes y evitando abstracciones o cambios ajenos al alcance.
3. Aplica DDD cuando la complejidad del dominio lo justifique. Para prototipos, pruebas de concepto o funcionalidades pequeñas, elige la solución más simple que satisfaga los requisitos.
4. Usa arquitectura hexagonal y Screaming Architecture cuando la escala y las necesidades del sistema lo justifiquen. Respeta la arquitectura existente y no la impongas ni reestructures sin una necesidad concreta.
5. Si el proyecto o la solicitud requiere trabajar con ClickUp, pregunta si se deben actualizar allí los elementos relacionados y si deben quedar a nombre de Gustavo Valmaña Villalonga. No preguntes ni presupongas que ClickUp se usa cuando no forma parte del proyecto.

## Adaptadores y dobles para pruebas de integración

- Al implementar un puerto o adaptador de infraestructura (por ejemplo, un conector, repositorio o cliente externo), incluye un doble de prueba compatible con el mismo contrato para las pruebas de integración.
- Usa una implementación en memoria cuando el comportamiento dependa de estado (por ejemplo, un repositorio), o una implementación registradora (`recording`/`spy`) cuando baste con capturar llamadas, parámetros y resultados. Elige según el contrato; no es necesario implementar ambas.
- El doble debe ser determinista, no acceder a servicios reales y permitir verificar el comportamiento relevante. Ubícalo según la estructura de pruebas existente y reutiliza o extiende un doble equivalente si ya existe.
- No agregues logging a producción solo para facilitar las pruebas. Si el proyecto no tiene una convención o estructura de pruebas adecuada, sigue sus patrones existentes y señala la decisión en el handoff.
