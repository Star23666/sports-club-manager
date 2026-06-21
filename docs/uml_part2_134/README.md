# UML Diagrams — Part 2

PlantUML diagrams for the software engineering report.

| File | Type | Purpose |
|------|------|---------|
| `1_context.puml` | Context Model | System boundary, external actors, external service interactions |
| `3_structural.puml` | Structural Model (Component Diagram) | Static organization of front-end, back-end, and database |
| `4_behavioral.puml` | Behavioral Model (Activity Diagram) | Reset-password workflow with branches and exception paths |

## Rendering

Install the **PlantUML** VS Code extension, open any `.puml` file, and run `PlantUML: Preview Current Diagram`. Export to PNG/SVG from the preview panel.

## Traceability to Code

| Diagram | Source Files |
|---------|-------------|
| Context | `python/app/main.py` |
| Structural | `python/app/api/*.py`, `database/install.sql`, `admin-front-end/src/`, `client-front-end/src/` |
| Behavioral | `python/app/api/find.py`, `python/app/email_service.py`, `client-front-end/src/views/FindAccount.vue`, `client-front-end/src/views/ResetPassword.vue` |
