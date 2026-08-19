#!/usr/bin/env bash
# Cargar con: source scripts/env.sh
# Necesario porque ~/.bashrc no se aplica en shells no interactivas (ej. herramientas
# automatizadas) — este script sirve como fuente explícita del toolchain.
export JAVA_HOME="$HOME/dev-tools/jdk-17.0.20+8"
export ANDROID_HOME="$HOME/Android/Sdk"
export PATH="$JAVA_HOME/bin:$ANDROID_HOME/platform-tools:$ANDROID_HOME/cmdline-tools/latest/bin:$HOME/dev-tools/flutter/bin:$HOME/dev-tools/ngrok-bin:$PATH"
export NGROK_CONFIG="$HOME/.ngrok2/ngrok.yml"
