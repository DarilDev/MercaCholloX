#!/usr/bin/env bash
# Cargar con: source scripts/env.sh
# Necesario porque ~/.bashrc no se aplica en shells no interactivas (ej. herramientas
# automatizadas) — este script sirve como fuente explícita del toolchain.
export JAVA_HOME="$HOME/dev-tools/jdk-17.0.20+8"
export ANDROID_HOME="$HOME/Android/Sdk"
export PATH="$JAVA_HOME/bin:$ANDROID_HOME/platform-tools:$ANDROID_HOME/cmdline-tools/latest/bin:$HOME/dev-tools/flutter/bin:$HOME/dev-tools/ngrok-bin:$HOME/dev-tools/chrome-for-testing/chrome-linux64:$HOME/dev-tools/chrome-for-testing/chromedriver-linux64:$PATH"
export NGROK_CONFIG="$HOME/.ngrok2/ngrok.yml"
# Chrome for Testing necesita libasound2, no instalado por apt en esta máquina
# (sin sudo) — extraída a mano del .deb de Ubuntu, ver docs/DECISIONS.md.
export LD_LIBRARY_PATH="$HOME/dev-tools/extra-libs/extracted/usr/lib/x86_64-linux-gnu:$LD_LIBRARY_PATH"
export CHROME_BIN="$HOME/dev-tools/chrome-for-testing/chrome-linux64/chrome"
