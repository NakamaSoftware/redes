#!/bin/bash
# Prepara las herramientas de edición de reels en las sesiones en la nube:
# Whisper (whisper.cpp + modelo small), las skills de Hyperframes y Playwright para las skills del repo.
# Es idempotente: si algo ya está, lo saltea.
set -euo pipefail

if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

H=${HERRAMIENTAS:-/root/herramientas}
W=$H/whisper.cpp
MODELO=$H/modelos/ggml-small.bin
SHA1_MODELO=55356645c2b361a969dfd0ef2c5a50d530afd8d5
mkdir -p "$H/modelos"

# 1 · whisper.cpp (whisper-cli)
if [ ! -x "$W/build/bin/whisper-cli" ]; then
  [ -d "$W/.git" ] || git clone -q --depth 1 https://github.com/ggml-org/whisper.cpp "$W"
  cmake -S "$W" -B "$W/build" -DCMAKE_BUILD_TYPE=Release -DWHISPER_BUILD_TESTS=OFF > /dev/null
  cmake --build "$W/build" -j "$(nproc)" --target whisper-cli > /dev/null
fi

# 2 · modelo small de Whisper, verificado
if [ ! -f "$MODELO" ] || [ "$(sha1sum "$MODELO" | cut -d' ' -f1)" != "$SHA1_MODELO" ]; then
  curl -sSfL -o "$MODELO.tmp" https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-small.bin
  [ "$(sha1sum "$MODELO.tmp" | cut -d' ' -f1)" = "$SHA1_MODELO" ] || { echo "el modelo de Whisper no coincide con el oficial" >&2; rm -f "$MODELO.tmp"; exit 1; }
  mv "$MODELO.tmp" "$MODELO"
fi

# whisper-cli en el PATH de la sesión
mkdir -p /root/.local/bin
ln -sfn "$W/build/bin/whisper-cli" /root/.local/bin/whisper-cli
if [ -n "${CLAUDE_ENV_FILE:-}" ]; then
  echo 'export PATH="/root/.local/bin:$PATH"' >> "$CLAUDE_ENV_FILE"
  echo "export WHISPER_MODELO=\"$MODELO\"" >> "$CLAUDE_ENV_FILE"
fi

# 3 · skills de Hyperframes (traen los sonidos de efectos-reels)
if [ ! -d /root/.claude/skills/media-use ]; then
  (cd /tmp && npx --yes skills add heygen-com/hyperframes -g -a claude-code -s '*' -y > /dev/null)
fi

# 4 · Playwright ya instalado, enlazado en las skills del repo que renderizan con Chrome
PW=/opt/node-tools/node_modules
for k in editar-reels-claude motion-graphics-viegas; do
  d="$CLAUDE_PROJECT_DIR/.claude/skills/$k"
  [ -d "$d" ] || continue
  mkdir -p "$d/node_modules"
  ln -sfn "$PW/playwright" "$d/node_modules/playwright"
  ln -sfn "$PW/playwright-core" "$d/node_modules/playwright-core"
done
