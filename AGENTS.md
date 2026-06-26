# AGENTS.md

## Propósito del Proyecto
Crear un asistente personal tipo "JARVIS" (nombre: **ATLAS**) controlado por la API de Ollama Cloud, que sea capaz de:

- Escuchar el micrófono
- Ver la pantalla del usuario
- Ver el PC (recursos, archivos, procesos)
- Consultar información por mí
- Ejecutar acciones en mi lugar
- Escalable para futuras funcionalidades

## Idioma Principal
**Español** — Toda la interfaz, mensajes y documentación deben estar en español.

## Interfaz Gráfica
Debe incluir una GUI con apartado de configuraciones que permita:
- Cambiar la API key de Ollama Cloud
- Elegir y cambiar entre modelos disponibles
- Ajustar parámetros del agente

## Stack Tecnológico
(Pendiente de definir contigo)

## Reglas para el Agente (IA)

### ⚠️ REGLA DE ORO: No modificar nada sin confirmación
**NO ESTÁS AUTORIZADO** a modificar, crear, eliminar o renombrar ningún archivo sin mi confirmación explícita. Debes:
1. Leer y entender el código primero.
2. Proponerme los cambios que quieras hacer.
3. Esperar mi autorización antes de ejecutarlos.

### Flujo de trabajo
- Siempre que te pida algo, primero pregúntame si tienes dudas.
- Proponme opciones cuando haya múltiples caminos posibles.
- Explica claramente qué vas a hacer antes de hacerlo.
- No ejecutes comandos destructivos sin preguntar (rm, git reset, etc.).

## Control de Versiones
- Usar Git para control de versiones.
- Subir a GitHub para respaldo.
- Crear `.gitignore` apropiado para el proyecto.

## Tareas Inmediatas Pendientes
1. Definir stack tecnológico (lenguaje, frameworks, librerías).
2. Crear estructura inicial del proyecto.
3. Configurar `.gitignore`.
4. Inicializar Git y repositorio en GitHub.
5. Desarrollar módulo de conexión con Ollama Cloud API.
6. Desarrollar módulo de micrófono.
7. Desarrollar módulo de captura de pantalla.
8. Desarrollar módulo de monitoreo del PC.
9. Desarrollar interfaz gráfica con configuraciones.
10. Integrar todo en el asistente ATLAS.
