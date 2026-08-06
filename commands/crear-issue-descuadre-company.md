---
description: Crea un issue en Linear para analizar descuadres de un idCompany.
---

Crea un issue en Linear para analizar descuadres de un idCompany.

Argumentos recibidos:

`$ARGUMENTS`

Reglas obligatorias:

- Usa siempre el `idCompany` proporcionado por el usuario.
- Si no puedes identificar un `idCompany` en los argumentos, pregúntalo antes de continuar.
- Pregunta siempre la versión del `idCompany` antes de crear el issue.
- Si el usuario no especifica assignee, usa `gustavo.valmana@alegra.com`.
- Si el usuario no especifica TMD/team, usa `tmd-ac-ledger`.
- Si el assignee o team indicado es ambiguo, resuélvelo con Linear y pregunta antes de crear.
- No crees el issue hasta tener confirmados: `idCompany`, `version`, `assignee` y `team`.
- Usa el MCP de Linear mediante `Linear_save_issue`. No uses GraphQL directo.
- No agregues `Definition of Ready` ni `Definition of Done`.
- Crea el issue con estimate `1`.
- Crea el issue con prioridad Medium (`priority: 3`).
- Crea el issue en status `Triage`.
- Crea el issue con SLA de 1 semana: calcula `slaBreachesAt` como la fecha/hora actual + 7 días en formato ISO-8601 y usa `slaType: "all"`.

Verificación previa de duplicados:

- Antes de crear el issue, construye el título final: `Revisar descuadre de idCompany ${idCompany}`.
- Busca en Linear issues existentes con ese mismo título en el team seleccionado.
- Revisa todos los resultados encontrados, incluyendo su status y status type.
- Si existe un issue con el mismo título cuyo status no sea `Done` y cuyo status type no sea `completed`, no crees una tarea nueva.
- Si no creas una tarea por esta regla, responde con el issue existente: identificador, URL, status, team y assignee si están disponibles.
- Si solo existen issues con el mismo título en `Done` o con status type `completed`, sí puedes crear una nueva tarea.
- La comparación del título debe ser exacta después de hacer trim; no bloquees por coincidencias parciales.

Labels de versión:

- Lista los issue labels disponibles en Linear antes de crear el issue.
- Considera únicamente labels cuyo parent sea exactamente `Versión`.
- El usuario no está obligado a escribir exactamente el nombre del label.
- Normaliza la versión indicada por el usuario antes de comparar: trim, case-insensitive, sin tildes, y tolerando espacios, guiones y guiones bajos.
- Primero intenta mapear la versión indicada usando el mapa de aliases de versión definido abajo.
- Si no hay alias compatible, compara la versión normalizada contra el nombre normalizado de cada label bajo `Versión`.
- Si existe un label bajo `Versión` que coincida con la versión indicada, asígnalo al issue.
- Si no existe un label compatible, crea el issue sin label de versión.
- Nunca crees labels nuevos.

Mapa de aliases de versión:

- `COL`: `col`, `colombia`, `colombiana`, `co`
- `MEX`: `mex`, `mexico`, `méxico`, `mx`, `mexicana`
- `ARG`: `arg`, `argentina`, `ar`
- `CHIL`: `chil`, `chile`, `cl`, `chilena`
- `PER`: `per`, `peru`, `perú`, `pe`, `peruana`
- `VEN`: `ven`, `venezuela`, `ve`, `venezolana`
- `CRI`: `cri`, `costa rica`, `costarica`, `cr`
- `DOM`: `dom`, `dominicana`, `republica dominicana`, `república dominicana`, `rd`, `do`
- `PAN`: `pan`, `panama`, `panamá`, `pa`, `panamena`, `panameña`
- `USA`: `usa`, `us`, `estados unidos`, `eeuu`, `ee.uu`, `united states`
- `ESP`: `esp`, `espana`, `españa`, `es`, `spanish`, `spain`
- `4X4`: `4x4`, `4 x 4`
- `ALL`: `all`, `todas`, `todos`, `global`, `general`
- `OTHERS`: `others`, `other`, `otras`, `otros`, `otro`, `otra`

Labels obligatorios:

- Agrega siempre el label `Bug` cuyo parent sea exactamente `Task Type`.
- Agrega siempre el label `Bugs` cuyo parent sea exactamente `Type bug`.
- Antes de crear el issue, lista los issue labels disponibles en Linear para resolver estos labels por nombre y parent.
- Si alguno de estos labels obligatorios no existe, no crees labels nuevos y avisa en la respuesta final cuál no se pudo asignar.

El título debe ser:

`Revisar descuadre de idCompany ${idCompany}`

La descripción debe ser:

```markdown
## Description

Analizar descuadre reportado para el idCompany `${idCompany}`.

Contexto:
Se requiere revisar el origen del descuadre, identificar si corresponde a parametrización, contabilización, datos históricos, migración o comportamiento esperado del sistema.
```

Después de crear el issue, responde con:

- Identificador y URL del issue.
- `idCompany` usado.
- `version` usada.
- Label de versión aplicado, o que no se aplicó ninguno porque no existía.
- Labels obligatorios aplicados, o cuáles no se pudieron aplicar porque no existían.
- Team usado.
- Assignee usado.
- Estimate usado.
- Prioridad usada.
- Status usado.
- SLA usado.
