"""Modulo de Renomeacao Atomica e Segura de Arquivos de Transcricao e Ata (.md).
Aplica o formato padronizado apenas aos arquivos Markdown (.md): AAAA-MM-DD_HH-MM-SS_Titulo-Contextual.ext
Arquivos de audio (.wav) NUNCA sao renomeados, permanecendo com seus nomes originais intactos.
Garante que em caso de colisao ou falha, os arquivos originais permanecem intactos.
"""

import os
import re
import shutil
from pathlib import Path
from typing import Optional, Tuple
from datetime import datetime

try:
    from scripts.logger_audit import get_logger
except ImportError:
    from logger_audit import get_logger


def extrair_data_hora_prefixo(nome_arquivo: str) -> str:
    """Extrai o prefixo YYYY-MM-DD_HH-MM-SS de nomes de arquivos."""
    m = re.search(r'(\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2})', nome_arquivo)
    if m:
        return m.group(1)
    agora = datetime.now()
    return agora.strftime("%Y-%m-%d_%H-%M-%S")


def sanitizar_slug(slug: str) -> str:
    """Garante apenas caracteres seguros para o sistema de arquivos."""
    slug_limpo = re.sub(r'[^a-zA-Z0-9_\-]', '', slug)
    return slug_limpo.strip("-_") or "Sessao"


def renomear_trio_arquivos(
    audio_path: Optional[Path],
    transcricao_path: Optional[Path],
    ata_path: Optional[Path],
    titulo_slug: str
) -> Tuple[Optional[Path], Optional[Path], Optional[Path]]:
    """Renomeia exclusivamente os arquivos Markdown (.md) de transcricao e ata.
    Arquivos de audio (.wav) NUNCA sao renomeados, preservando o nome original de gravacao.
    """
    logger = get_logger()
    slug_safe = sanitizar_slug(titulo_slug)

    # Identifica o prefixo temporal a partir do primeiro arquivo valido
    prefixo_tempo = None
    for p in [audio_path, transcricao_path, ata_path]:
        if p and p.name:
            pref = extrair_data_hora_prefixo(p.name)
            if pref:
                prefixo_tempo = pref
                break

    if not prefixo_tempo:
        prefixo_tempo = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    base_nome = f"{prefixo_tempo}_{slug_safe}"

    # 1. Audio (.wav): NUNCA renomear arquivos de audio. Preserva nome original.
    novo_audio = audio_path

    novo_trans = None
    novo_ata = None

    # 2. Renomeia apenas a Transcricao (.md) se existir
    if transcricao_path and transcricao_path.exists():
        novo_nome_trans = f"{base_nome}_transcricao.md"
        dest_trans = transcricao_path.parent / novo_nome_trans
        if dest_trans != transcricao_path:
            contador = 1
            while dest_trans.exists() and dest_trans != transcricao_path:
                dest_trans = transcricao_path.parent / f"{base_nome}_{contador}_transcricao.md"
                contador += 1
            try:
                transcricao_path.rename(dest_trans)
                novo_trans = dest_trans
                logger.info("RENOMEADOR", "TRANSCRICAO", f"Transcricao (.md) renomeada para: {dest_trans.name}")
            except Exception as e:
                logger.warn("RENOMEADOR", "TRANSCRICAO", f"Nao foi possivel renomear transcricao ({e}).")
                novo_trans = transcricao_path
        else:
            novo_trans = transcricao_path

    # 3. Renomeia apenas a Ata (.md) se existir: comeca obrigatoriamente com o prefixo ATA_
    if ata_path and ata_path.exists():
        novo_nome_ata = f"ATA_{prefixo_tempo}_{slug_safe}.md"
        dest_ata = ata_path.parent / novo_nome_ata
        if dest_ata != ata_path:
            contador = 1
            while dest_ata.exists() and dest_ata != ata_path:
                dest_ata = ata_path.parent / f"ATA_{prefixo_tempo}_{slug_safe}_{contador}.md"
                contador += 1
            try:
                ata_path.rename(dest_ata)
                novo_ata = dest_ata
                logger.info("RENOMEADOR", "ATA", f"Ata (.md) renomeada para: {dest_ata.name}")
            except Exception as e:
                logger.warn("RENOMEADOR", "ATA", f"Nao foi possivel renomear ata ({e}).")
                novo_ata = ata_path
        else:
            novo_ata = ata_path

    return novo_audio, novo_trans, novo_ata

