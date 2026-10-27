---
name: revisar-en-invideo
description: >
  Monta en invideo Editor los MP4 que Claude Code ya ha editado (reels, versiones, variantes) para revisarlos cómodamente:
  cada versión en su pista o una tras otra, con su nombre, para reproducir, ir hacia adelante y hacia atrás y comparar. Luego
  recoge las correcciones de la persona (con tiempo y versión), las aplica en Claude Code volviendo a renderizar con la skill
  que hizo el vídeo (editar-reels-claude, motion-graphics-viegas…) y reemplaza solo el clip corregido en invideo Editor.
  invideo Editor es la sala de revisión: no se edita ni se procesa nada allí. Úsala cuando pida «súbelo a invideo», «quiero
  ver las versiones en invideo», «compara las versiones», «monta los reels en invideo para revisarlos» o «aplica estas
  correcciones y actualízalo en invideo». Requiere el conector MCP de invideo (invideo.io/remote-agents).
---

# Revisar en invideo Editor (método Viegas Estudio)

**Reparto del trabajo:** todo el procesado (cortes, recorte, subtítulos, motion graphics, sonido, render) se hace en **Claude Code** con las skills del kit. **invideo Editor solo se usa para ver y comparar** los MP4 terminados y apuntar correcciones. Así la persona revisa en un editor de verdad (gratis) sin depender de abrir archivos uno a uno.

Habla claro y sin jerga; no le pidas que escriba comandos.

## 0. Antes de empezar
1. Comprueba que las herramientas del conector de invideo están disponibles (busca herramientas cuyo nombre contenga `invideo`). Si no lo están, explícale cómo conectarlo:
   - En **invideo.io/remote-agents** elige Claude Code, copia el prompt de configuración y pégalo aquí; inicia sesión cuando lo pida.
   - Conectar invideo Editor es **gratis**; solo gastan créditos los agentes de invideo cuando generan cosas (aquí no los usamos).
2. Localiza los MP4 a revisar (normalmente `resultados/` del proyecto). Lista nombre, duración y tamaño, y confirma con la persona cuáles subir.

## 1. Montar para revisar
1. Crea un proyecto en invideo Editor con un nombre claro (`<proyecto> · revisión v1`) y el formato de los vídeos (1080×1920 para reels, 1920×1080 para YouTube).
2. Sube cada MP4 y colócalo según lo que quiera comparar:
   - **Comparar versiones** (por defecto): una tras otra en la misma pista, en orden, con un hueco de 1 s y el nombre de cada versión como marcador o título breve al principio.
   - **Comparar en paralelo**: cada versión en su pista, alineadas en 0 s, para alternar entre pistas (si el editor permite ver o silenciar pistas).
   - **Antes / después**: el original y el editado seguidos.
3. Mantén **el audio** de cada clip; no añadas música ni efectos.
4. Dale el enlace o dile dónde abrir el proyecto, y una tabla: versión · en qué segundo empieza · qué cambia respecto a las demás.

## 2. Recoger correcciones
Pide las notas así (y apúntalas tal cual):
| Versión | Tiempo | Corrección |
|---|---|---|
| v2 | 0:08 | el subtítulo tapa la boca |

Si dice algo vago («no me gusta el gancho»), pregunta qué cambiar en concreto. Si ve algo en invideo Editor y no sabe el tiempo, pídele que pare el cursor ahí y te lo diga.

## 3. Aplicar en Claude Code
1. Cada corrección se aplica **en el proyecto de Claude Code**, con la skill que generó ese vídeo (p. ej. `editar-reels-claude` para el reel, `motion-graphics-viegas` para un gráfico o una variante). Nunca se arregla dentro de invideo Editor.
2. Renderiza **solo** las versiones afectadas (previa rápida si la persona quiere ver primero).
3. Comprueba el resultado (fotogramas del momento corregido) antes de subirlo.

## 4. Actualizar invideo Editor
1. Sube el MP4 nuevo con sufijo de versión (`v2-r1.mp4`) y **reemplaza solo ese clip** en su sitio (mismo inicio, misma pista). Las demás versiones no se tocan.
2. Añade un marcador «corregido: <qué>» en el clip nuevo.
3. Dile qué ha cambiado y en qué segundo mirar.
4. Repite 2–4 hasta que apruebe. Al final, guarda el MP4 aprobado en la carpeta de entrega del proyecto.

## Reglas
- Nunca borres clips ni proyectos de invideo Editor sin preguntar; reemplazar es añadir el nuevo y quitar el viejo de la línea de tiempo.
- No uses los agentes de generación de invideo salvo que la persona lo pida (gastan créditos).
- Escribe siempre **invideo** en minúscula y en una palabra.
