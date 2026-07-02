---
name: linear-estimation-update
description: |-
  Actualiza estimaciones (story points) de issues en Linear para alinearlas con la
  nueva convención del equipo: se elimina el 0 como estimación (mínimo 1 punto) y se
  usa la escala 1-2-3-5-8-13. Úsalo cuando el usuario pida "actualizar estimaciones en
  Linear", "migrar a la nueva escala de puntos", "quitar los ceros de Linear" o
  similar. SIEMPRE pregunta primero por team, state y usuario/asignado antes de
  modificar cualquier issue — nunca asumas ninguno de estos tres filtros.
  Examples:
  - user: "actualiza mis issues de Linear a la nueva convención de puntos" → preguntar
    team, estado(s) y usuario/asignado a procesar, luego ejecutar
  - user: "solo backlog de mi usuario en el team Ledger" → filtrar por team Ledger,
    state Backlog y ese usuario específico
---

# Actualización de estimaciones en Linear (nueva convención)

## Contexto de la convención (referencia fija, no modificar)

| Story point | Esfuerzo | Tiempo | Complejidad | Riesgo/Incertidumbre |
|---|---|---|---|---|
| 1 | Mínimo | Minutos | Baja | Ninguna |
| 2 | Mínimo | Horas | Baja | Ninguna |
| 3 | Leve | ~1 día | Baja | Baja |
| 5 | Moderado | Algunos días | Media | Moderada |
| 8 | Alto | ~1 semana | Media | Moderada |
| 13 | Máximo | ~1 mes | Alta | Alta |

Reglas clave:

- **Se elimina el 0**: ninguna tarea planificada debe quedar con estimate = 0 (ni null si ya
  estaba planificada).
- No hay límite de 8 puntos por sprint. No reduzcas ni "recortes" estimaciones para
  encajar en un límite de capacidad; el límite ya no existe.
- Este cambio aplica desde el refinamiento del día indicado por el equipo — no toques
  issues ya cerrados/históricos salvo que el usuario lo pida explícitamente.

## Tabla de equivalencia Old → New (para issues YA estimados con la escala anterior)

Cuando el issue ya tiene un `estimate` asignado con la escala vieja (0,1,2,3,5,8,13),
usa esta conversión fija para migrarlo a la escala nueva — NO es lo mismo que estimar
un issue nuevo desde cero (para eso usa la tabla de esfuerzo/tiempo/complejidad de la
sección anterior).

| Escala anterior | Tiempo estimado antiguo | Nueva equivalencia |
|---|---|---|
| 0 | ~1 hora | 1 |
| 1 | ~1 día | 2 o 3 |
| 2 | 1.5–2 días | 5 |
| 3 | ~3 días | 5 |
| 5 | 4–5 días | 8 |
| 8 | ~1 sprint parcial | 13 |
| 13 | épico | 13 |

Regla de aplicación:

- Para todos los valores con equivalencia única (0→1, 2→5, 3→5, 5→8, 8→13, 13→13),
  aplica la conversión automáticamente sin preguntar issue por issue — es una migración
  determinística de escala.
- El caso **1 → 2 o 3** es ambiguo y no se resuelve solo. Cuando encuentres un issue con
  estimate antiguo = 1, sepáralo en una lista aparte y pregúntale al usuario (una sola
  vez, con la lista completa de esos issues) si quiere:
  a) revisar uno por uno cuál va a 2 y cuál a 3, o
  b) aplicar un criterio por defecto (ej. "todos a 2" o "todos a 3"), o
  c) usar un heurístico simple (título/descripción sugieren más carga → 3, tarea acotada
     → 2) y que se lo confirmes antes de escribir.
  No asignes 2 o 3 por tu cuenta sin que el usuario elija una de estas opciones.

## Flujo obligatorio

### 1. Usa el MCP de Linear, no GraphQL directo

Este proyecto ya tiene el MCP de Linear conectado en OpenCode — úsalo como método
principal para leer y escribir issues (búsqueda/filtrado por team y state, y
actualización de `estimate`). No hagas `fetch` manual a `api.linear.app/graphql` ni
pidas un `LINEAR_API_KEY`: la autenticación y los permisos ya los resuelve el MCP.

Antes de empezar, confirma que las tools de Linear del MCP estén disponibles (listar
teams o states es un buen check rápido de que la conexión funciona). Si el MCP no
está disponible o falla, recién ahí considera el fallback de GraphQL directo descrito
al final de este documento — y avisa al usuario que estás usando el fallback.

### 2. Pregunta SIEMPRE el alcance antes de tocar nada

Antes de ejecutar cualquier query o mutation, pregunta explícitamente al usuario los
tres filtros de alcance — ninguno es opcional, no asumas ninguno por defecto:

- **Team**: ¿qué equipo(s) de Linear? Si hay más de uno conectado, no proceses todos
  por defecto; pedí que especifique cuál(es).
- **State**: ¿qué estado(s) / workflow state(s)? (ej: "Backlog", "Todo",
  "In Progress"). Si el usuario dice "solo backlog", filtra únicamente por ese state.
  Nunca proceses todos los estados si el usuario mencionó uno específico.
- **Usuario/asignado**: ¿a qué usuario(s) (assignee) le pertenecen los issues a
  actualizar? No proceses issues de asignados que el usuario no mencionó. Si el
  usuario quiere abarcar a todo el equipo, que lo diga explícitamente ("todos los
  asignados del team X") — no lo asumas por omisión.
- ¿Solo issues con estimate = 0 / sin estimar, o revisar todas las del estado elegido?
- ¿Esto es una **migración de escala vieja a nueva** (issues que ya tienen puntos con
  la escala 0-1-2-3-5-8-13) o una **estimación nueva** (issues sin estimar todavía)?
  Puede ser ambas a la vez, pero acláraselo al usuario para elegir la tabla correcta
  (ver secciones siguientes).

No avances a la ejecución hasta tener confirmados los tres filtros (team, state,
usuario/asignado). El caso ambiguo "1 → 2 o 3" de la tabla de migración se resuelve en
este mismo paso o en el paso 4, no antes.

### 3. Consulta los issues (vía MCP, solo lectura)

Usa las tools de listar/buscar issues del MCP de Linear filtrando por **team**,
**state** y **assignee (usuario)** confirmados en el paso 2. Trae al menos: `id`,
`identifier`, `title`, `estimate`, `state.name`, `assignee.name`. Si la tool del MCP
no soporta alguno de estos filtros directamente, trae los issues del team y filtra vos
mismo en memoria por `state.name` y `assignee` antes de seguir — no proceses issues de
estados o asignados que el usuario no pidió.

### 4. Presenta la lista antes de modificar

Muéstrale al usuario la lista de issues encontrados (identifier, título, estimate
actual) con su estimate nuevo propuesto, calculado así:

- Si el issue tiene un `estimate` antiguo dentro de {0,1,2,3,5,8,13} → aplica la tabla
  de equivalencia Old → New de arriba. Marca aparte los casos "1 → 2 o 3" para
  resolverlos según lo que el usuario haya elegido en el paso 2.
- Si el issue no tiene estimate (null) o tiene un valor fuera de esa escala → no lo
  conviertas con la tabla; trátalo como estimación nueva y usa la tabla de
  esfuerzo/tiempo/complejidad, preguntando o sugiriendo con criterio explícito (no
  asignes 1 por defecto sin mostrar el porqué).

Pide confirmación final del listado completo (incluyendo los casos ambiguos ya
resueltos) antes de escribir cambios.

### 5. Aplica los cambios (vía MCP)

Solo tras confirmación explícita, actualiza cada issue con la tool de actualización de
issues del MCP de Linear (equivalente a `issueUpdate`, seteando el campo `estimate`).
Ejecutá las actualizaciones una por una (o en lotes pequeños) y registrá el resultado
de cada una. Si alguna falla, repórtala sin detener el resto.

### 6. Resume al final

Cierra con un resumen: cuántos issues se revisaron, cuántos se actualizaron, cuántos
quedaron igual, y cuántos fallaron (con motivo). No reportes datos de estados que el
usuario no pidió procesar.

## Fallback: GraphQL directo (solo si el MCP no está disponible)

Si el MCP de Linear no está conectado o falla, y el usuario confirma que quiere seguir
igual, podés usar la API GraphQL de Linear directamente. Requiere `LINEAR_API_KEY`
(pedísela al usuario si no está seteada como variable de entorno) y el header
`Authorization: <LINEAR_API_KEY>`.

Query de lectura:

```graphql
query IssuesByStateAndAssignee($teamId: ID!, $stateName: String!, $assigneeId: ID!) {
  issues(
    filter: {
      team: { id: { eq: $teamId } }
      state: { name: { eq: $stateName } }
      assignee: { id: { eq: $assigneeId } }
    }
  ) {
    nodes { id identifier title estimate state { name } assignee { name } }
  }
}
```

Mutation de escritura:

```graphql
mutation UpdateEstimate($issueId: String!, $estimate: Int!) {
  issueUpdate(id: $issueId, input: { estimate: $estimate }) {
    success
    issue { identifier estimate }
  }
}
```

Aplica las mismas reglas de confirmación y de las tablas de equivalencia que en el
flujo principal — el fallback cambia el mecanismo de transporte, no las reglas de
negocio.

## Notas

- No inventes IDs de equipo, estado ni usuario: obtenélos primero (vía MCP o, en
  fallback, con `teams { nodes { id name } }` / `workflowStates { nodes { id name } }` /
  `users { nodes { id name } }`) si el usuario no los conoce de memoria. Si hay
  ambigüedad entre varios usuarios con nombre similar, confirmá cuál es antes de
  filtrar.
- No cambies el límite de puntos por sprint en ninguna configuración de Linear (cycles),
  ya que ese límite se gestionaba fuera de Linear (era una convención del equipo, no un
  campo nativo) — solo actualiza `estimate` en los issues.