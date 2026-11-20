"""Script de automacao para publicacao de Releases e upload de binarios executaveis
no GitHub para o repositorio Espaco-CMaker/transcricao-ambiental.
Utiliza a autenticacao ativa do Git Credential Manager sem salvar tokens em disco.
"""

import os
import sys
import json
import subprocess
from pathlib import Path
import requests

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

REPO_OWNER = "Espaco-CMaker"
REPO_NAME = "transcricao-ambiental"
TAG_NAME = "v1.0.42"
RELEASE_TITLE = "Transcrição Ambiental de Sala v1.0.42 (Portátil Standalone)"

RELEASE_BODY = """## 🎙️📝 Transcrição Ambiental de Sala v1.0.42

Aplicação desktop 100% nativa e local em Python (sem servidor, sem portas HTTP e sem navegador web), desenvolvida com CustomTkinter, SoundDevice, SoundFile, Faster-Whisper (CUDA/CPU int8) e Pygame para gravação contínua de áudio de sala e geração automática de transcrições em Markdown (.md).

---

### 📦 Download do Pacote Portátil Standalone (Windows 64-bit):

⬇️ **`TranscricaoAmbiental_Portatil.zip`** *(~341 MB)*
- Pacote completo com todos os binários, dependências Python e modelo offline pré-carregado.
- Não requer instalação prévia de Python ou conexão com a internet.
- Para usar: basta baixar, descompactar em qualquer pasta ou pendrive e executar **`Iniciar_Transcricao.bat`** (ou `TranscricaoAmbiental.exe`).

---

### 🌟 Principais Recursos da Versão v1.0.42:
- **100% Offline e Seguro:** Zero envio de áudio para servidores externos, preservando a privacidade de estudantes e docentes.
- **Transcrição em Lote Contextual:** Botão único `⚡ Transcrever` que transcreve o arquivo ou múltiplos arquivos selecionados na tabela (via Shift, Ctrl ou Ctrl+A).
- **Osciloscópio Acústico de Alta Precisão:** Gráfico de som ao vivo dos últimos 5 segundos com traços verticais de 1px e passo de 3px, oscilação perfeitamente simétrica em torno do horizonte central.
- **Timestamps Reais:** Cálculo cronológico dos horários reais do relógio (`HH:MM:SS`) projetados sobre todas as falas da transcrição.
- **Reprodutor Integrado com Seek Interativo:** Clique em qualquer ponto da forma de onda para saltar instantaneamente a reprodução com playhead sincronizado.
- **Organização por Dia:** Divisores cronológicos na tabela agrupando gravações e transcrições por data.
"""

def get_github_token() -> str:
    """Obtem o token de autenticacao diretamente do Git Credential Manager."""
    gcm_path = "C:/Users/fgbet/MinGit/mingw64/bin/git-credential-manager.exe"
    if not os.path.exists(gcm_path):
        import shutil
        gcm_path = shutil.which("git-credential-manager") or "git-credential-manager"

    p = subprocess.Popen(
        [gcm_path, "get"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    out, _ = p.communicate("protocol=https\nhost=github.com\n")
    for line in out.splitlines():
        if line.startswith("password="):
            return line.split("=", 1)[1].strip()
    return None

def publish():
    project_root = Path(__file__).resolve().parent.parent
    dist_dir = project_root / "dist"
    portable_zip = dist_dir / "TranscricaoAmbiental_Portatil.zip"

    print("=" * 65)
    print(" 🚀 Publicador de Release no GitHub - Transcricao Ambiental")
    print("=" * 65)

    token = get_github_token()
    if not token:
        print("[ERRO] Nao foi possivel obter o token de acesso do GitHub via Git Credential Manager.")
        sys.exit(1)

    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "CMaker-Release-Publisher/1.0"
    }

    # 1. Verifica se a release ja existe
    rel_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/releases/tags/{TAG_NAME}"
    resp = requests.get(rel_url, headers=headers)

    if resp.status_code == 200:
        release_data = resp.json()
        print(f"[*] Release {TAG_NAME} ja existe (ID: {release_data['id']}).")
    elif resp.status_code == 404:
        print(f"[*] Criando nova Release {TAG_NAME} no GitHub...")
        create_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/releases"
        payload = {
            "tag_name": TAG_NAME,
            "target_commitish": "main",
            "name": RELEASE_TITLE,
            "body": RELEASE_BODY,
            "draft": False,
            "prerelease": False
        }
        create_resp = requests.post(create_url, headers=headers, json=payload)
        if create_resp.status_code not in (200, 201):
            print(f"[ERRO] Falha ao criar release: {create_resp.status_code} - {create_resp.text}")
            sys.exit(1)
        release_data = create_resp.json()
        print(f"[OK] Release criada com sucesso! (ID: {release_data['id']})")
    else:
        print(f"[ERRO] Erro ao consultar release: {resp.status_code} - {resp.text}")
        sys.exit(1)

    upload_url_template = release_data.get("upload_url", "").split("{")[0]
    existing_assets = {a["name"]: a["id"] for a in release_data.get("assets", [])}

    # 2. Upload do arquivo zip portatil
    if not portable_zip.exists():
        print(f"[ERRO] Arquivo zip portatil nao encontrado em: {portable_zip}")
        sys.exit(1)

    fname = portable_zip.name
    fsize_mb = portable_zip.stat().st_size / (1024 * 1024)

    if fname in existing_assets:
        print(f"\n[*] Arquivo '{fname}' ja existe na release. Substituindo...")
        del_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/releases/assets/{existing_assets[fname]}"
        del_resp = requests.delete(del_url, headers=headers)
        if del_resp.status_code in (200, 204):
            print("    ✔ Asset anterior removido com sucesso.")

    print(f"\n[*] Enviando '{fname}' ({fsize_mb:.1f} MB) para o GitHub Releases...")
    upload_url = f"{upload_url_template}?name={fname}"
    upload_headers = headers.copy()
    upload_headers["Content-Type"] = "application/zip"

    with open(portable_zip, "rb") as f_data:
        upload_resp = requests.post(
            upload_url,
            headers=upload_headers,
            data=f_data,
            timeout=1200
        )

    if upload_resp.status_code in (200, 201):
        asset_info = upload_resp.json()
        download_url = asset_info.get("browser_download_url", "")
        print(f"    ✔ Upload concluido com sucesso!")
        print(f"    Link direto de download: {download_url}")
    else:
        print(f"[ERRO] Falha no upload: {upload_resp.status_code} - {upload_resp.text}")
        sys.exit(1)

    print("\n" + "=" * 65)
    print(" 🎉 RELEASE PUBLICADA COM SUCESSO NO GITHUB!")
    print(f" Link da Release: https://github.com/{REPO_OWNER}/{REPO_NAME}/releases/tag/{TAG_NAME}")
    print("=" * 65)

if __name__ == "__main__":
    publish()
