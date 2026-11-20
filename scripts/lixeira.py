"""Modulo de retencao segura e gestao de lixeira (Skill lixeira).

Proibicao absoluta de hard delete. Todos os arquivos removidos ou
versoes anteriores substituidas sao movidos para lixeira/.
"""

import os
import shutil
import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
LIXEIRA_DIR = BASE_DIR / "lixeira"

def mover_para_lixeira(caminho_arquivo: str | Path, pasta_lixeira: str | Path | None = None) -> Path | None:
    """Move um arquivo de forma segura para a pasta lixeira/."""
    origem = Path(caminho_arquivo)
    if not origem.exists():
        return None

    if pasta_lixeira:
        target_lixeira = Path(pasta_lixeira)
    elif origem.parent.name in ["gravacoes", "transcricoes"]:
        # Se for subpasta de gravacoes/transcricoes, mantem a lixeira na raiz dessa pasta
        target_lixeira = origem.parent.parent / "lixeira"
    else:
        target_lixeira = LIXEIRA_DIR

    target_lixeira.mkdir(parents=True, exist_ok=True)
    nome_original = origem.name
    destino = target_lixeira / nome_original

    # Se ja existir arquivo com o mesmo nome na lixeira, adiciona timestamp
    if destino.exists():
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        destino = target_lixeira / f"{origem.stem}_{timestamp}{origem.suffix}"

    try:
        shutil.move(str(origem), str(destino))
        print(f"[LIXEIRA] Movido com sucesso: {origem.name} -> {target_lixeira.name}/{destino.name}")
        return destino
    except PermissionError:
        # Contingencia caso arquivo esteja em uso
        shutil.copy2(str(origem), str(destino))
        print(f"[LIXEIRA] Arquivo em uso. Copiado para lixeira: {destino.name}")
        return destino
    except Exception as exc:
        print(f"[LIXEIRA] Erro ao mover {origem}: {exc}")
        return None
