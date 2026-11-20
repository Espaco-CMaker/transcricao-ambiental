"""Script de geracao e empacotamento do executavel portatil para Windows.
Utiliza PyInstaller para criar a distribuicao standalone (.exe) com todas
as dependencias (CustomTkinter, Faster-Whisper, Pygame, SoundDevice, SoundFile)
e o modelo offline incorporado, pronto para rodar em outro PC sem Python instalado.
"""

import os
import sys
import shutil
import zipfile
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DIST_DIR = BASE_DIR / "dist"
BUILD_DIR = BASE_DIR / "build"
SCRIPTS_DIR = BASE_DIR / "scripts"

def main():
    print("=" * 70)
    print("  COMPILADOR DE EXECUTAVEL PORTATIL: TRANSCRICAO AMBIENTAL")
    print("=" * 70)
    print(f"Diretorio base: {BASE_DIR}")

    # 1. Comando do PyInstaller
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name", "TranscricaoAmbiental",
        "--onedir",
        "--windowed",
        "--noconfirm",
        "--clean",
        "--collect-all", "customtkinter",
        "--collect-all", "sounddevice",
        "--collect-all", "soundfile",
        "--collect-all", "faster_whisper",
        "--collect-all", "ctranslate2",
        "--collect-all", "pygame",
        "--exclude-module", "torch",
        "--exclude-module", "torchvision",
        "--exclude-module", "scipy",
        "--exclude-module", "cv2",
        "--exclude-module", "matplotlib",
        "--exclude-module", "numba",
        "--exclude-module", "llvmlite",
        "--paths", str(BASE_DIR),
        "--paths", str(SCRIPTS_DIR),
        str(SCRIPTS_DIR / "gui_app.py")
    ]

    print("\n[1/4] Executando PyInstaller (pode levar alguns minutos)...")
    res = subprocess.run(cmd, cwd=str(BASE_DIR))
    if res.returncode != 0:
        print("[ERRO] Falha na compilacao com PyInstaller.")
        sys.exit(res.returncode)

    app_dist_dir = DIST_DIR / "TranscricaoAmbiental"
    if not app_dist_dir.exists():
        print(f"[ERRO] Pasta de distribuicao nao encontrada: {app_dist_dir}")
        sys.exit(1)

    # 2. Copia pasta de modelos offline
    print("\n[2/4] Copiando modelos de transcricao offline para a distribuicao...")
    models_src = BASE_DIR / "models"
    models_dst = app_dist_dir / "models"
    if models_src.exists():
        if models_dst.exists():
            shutil.rmtree(str(models_dst))
        shutil.copytree(str(models_src), str(models_dst))
        print("  Modelos offline copiados com sucesso.")

    # 3. Cria estrutura de pastas necessarias na distribuicao
    print("\n[3/4] Criando diretorios de dados na pasta de distribuicao...")
    for folder in ["gravacoes", "transcricoes", "data", "lixeira"]:
        (app_dist_dir / folder).mkdir(parents=True, exist_ok=True)

    # Cria script atalho .bat de inicializacao dentro da distribuicao
    launcher_bat = app_dist_dir / "Iniciar_Transcricao.bat"
    with open(launcher_bat, "w", encoding="utf-8") as f:
        f.write("@echo off\n")
        f.write("chcp 65001 > nul\n")
        f.write("start \"\" \"%~dp0TranscricaoAmbiental.exe\"\n")

    print("  Atalho Iniciar_Transcricao.bat criado.")

    # 4. Gera arquivo compactado ZIP para facilitar transferencia para outro PC
    print("\n[4/4] Gerando pacote compactado .zip para transferencia...")
    zip_output_name = DIST_DIR / "TranscricaoAmbiental_Portatil"
    zip_file = shutil.make_archive(str(zip_output_name), "zip", root_dir=str(DIST_DIR), base_dir="TranscricaoAmbiental")
    zip_size_mb = Path(zip_file).stat().st_size / (1024 * 1024)

    print("\n" + "=" * 70)
    print("  EXECUTAVEL GERADO COM SUCESSO!")
    print("=" * 70)
    print(f"Pasta do Executavel: {app_dist_dir}")
    print(f"Executavel Principal: {app_dist_dir / 'TranscricaoAmbiental.exe'}")
    print(f"Pacote ZIP Portatil: {zip_file} ({zip_size_mb:.1f} MB)")
    print("Basta copiar a pasta ou o arquivo ZIP para o outro PC e rodar.")

if __name__ == "__main__":
    main()

