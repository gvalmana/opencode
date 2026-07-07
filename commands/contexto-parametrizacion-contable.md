---
description: Analiza el contexto global o local de un proyecto de parametrización contable Ledger.
agent: ledger-accounting-parametrization-architect
---

Analiza el contexto actual de parametrización contable Ledger.

Usa, si existen:

- `PROJECT.md` del workspace actual.
- `opencode.json` y sus `references`.
- Agentes locales del workspace.
- Documentación relacionada en WikiAlegra.
- Issues, proyectos o iniciativas de Linear mencionados o relevantes.

Entrega un análisis estructurado con:

1. **Resumen del contexto**
2. **Recurso parametrizado identificado**: items, banks, contacts, taxes, retentions u otro.
3. **Repositorios involucrados**
4. **Repositorios que parecen faltar o que no deberían participar**
5. **Componentes relevantes por repositorio**
6. **Relación entre microservicio, monolito e infraestructura**
7. **Riesgos técnicos y de compatibilidad**
8. **Documentación WikiAlegra relevante**
9. **Issues/proyectos Linear relevantes si aplica**
10. **Plan recomendado de trabajo**

No modifiques archivos. Este comando es solo para análisis y contextualización.

Si el usuario proporciona argumentos adicionales, úsalos para enfocar el análisis:

`$ARGUMENTS`
