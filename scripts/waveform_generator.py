"""Modulo para extracao e geracao de graficos de som (waveform drafts).
Permite extracao ultra-rapida de envelopes sonoros e renderizacao de miniaturas (sparklines)
e graficos detalhados de som capturado para cada arquivo de audio.
"""

import math
from pathlib import Path
from typing import Optional, Dict, Any, List
import numpy as np
import soundfile as sf
from PIL import Image, ImageTk, ImageDraw

_sparkline_cache: Dict[tuple, ImageTk.PhotoImage] = {}
_raw_waveform_cache: Dict[tuple, Dict[str, Any]] = {}
_text_waveform_cache: Dict[tuple, str] = {}
BARS_UNICODE = " ▂▃▄▅▆▇█"


def extrair_amostras_waveform(caminho_wav: Path, num_pontos: int = 150) -> Dict[str, Any]:
    """Extrai amostras de envelope, picos e RMS de um arquivo WAV com alta performance."""
    p = Path(caminho_wav)
    if not p.exists() or p.stat().st_size <= 44:
        return {
            "pontos": [0.0] * num_pontos,
            "rms_pontos": [0.0] * num_pontos,
            "pico_max": 0.0,
            "pico_db": -60.0,
            "rms_medio_db": -60.0,
            "atividade_pct": 0.0,
            "duracao_seg": 0.0,
            "valido": False
        }

    stat = p.stat()
    cache_key = (str(p.resolve()), stat.st_mtime, stat.st_size, num_pontos)
    if cache_key in _raw_waveform_cache:
        return _raw_waveform_cache[cache_key]

    peaks: List[float] = []
    rms_list: List[float] = []
    duracao_seg = 0.0

    try:
        with sf.SoundFile(str(p)) as f:
            frames = f.frames
            sr = f.samplerate
            duracao_seg = frames / sr if sr > 0 else 0.0

            if frames == 0:
                raise ValueError("Arquivo sem frames")

            block_size = max(1, frames // num_pontos)
            for _ in range(num_pontos):
                data = f.read(block_size, dtype="float32")
                if len(data) == 0:
                    break
                if data.ndim > 1:
                    data = data[:, 0]
                pk = float(np.max(np.abs(data)))
                rms = float(np.sqrt(np.mean(data**2)))
                peaks.append(pk)
                rms_list.append(rms)

    except Exception:
        # Fallback para arquivos vazios ou ilegiveis
        peaks = [0.0] * num_pontos
        rms_list = [0.0] * num_pontos
        duracao_seg = 0.0

    # Normalizacao e calculo de estatisticas
    if not peaks:
        peaks = [0.0] * num_pontos
        rms_list = [0.0] * num_pontos

    pico_max = max(peaks) if peaks else 0.0
    pico_db = 20.0 * math.log10(pico_max + 1e-9)
    pico_db = max(-60.0, min(0.0, pico_db))

    rms_medio = float(np.mean(rms_list)) if rms_list else 0.0
    rms_medio_db = 20.0 * math.log10(rms_medio + 1e-9)
    rms_medio_db = max(-60.0, min(0.0, rms_medio_db))

    # Atividade sonora: percentual de blocos acima de limiar auditivo (-45 dB ou RMS > 0.005)
    limiar = 0.005
    blocos_ativos = sum(1 for r in rms_list if r >= limiar)
    atividade_pct = (blocos_ativos / len(rms_list)) * 100.0 if rms_list else 0.0

    # Escala normalizada [0.0, 1.0] para desenho
    escala = pico_max if pico_max > 0.0 else 1.0
    norm_peaks = [min(1.0, pk / escala) for pk in peaks]
    norm_rms = [min(1.0, r / escala) for r in rms_list]

    res = {
        "pontos": norm_peaks,
        "rms_pontos": norm_rms,
        "pico_max": pico_max,
        "pico_db": pico_db,
        "rms_medio_db": rms_medio_db,
        "atividade_pct": round(atividade_pct, 1),
        "duracao_seg": duracao_seg,
        "valido": pico_max > 0.0001
    }

    _raw_waveform_cache[cache_key] = res
    return res


def gerar_sparkline_thumbnail(caminho_wav: Path, largura: int = 90, altura: int = 22) -> ImageTk.PhotoImage:
    """Gera um PhotoImage em miniatura (sparkline) da forma de onda para exibicao na tabela."""
    p = Path(caminho_wav)
    stat = p.stat() if p.exists() else None
    cache_key = (str(p.resolve()) if stat else str(p), getattr(stat, "st_mtime", 0), getattr(stat, "st_size", 0), largura, altura)

    if cache_key in _sparkline_cache:
        return _sparkline_cache[cache_key]

    num_barras = max(10, largura // 2)
    dados = extrair_amostras_waveform(p, num_pontos=num_barras)
    pontos = dados["pontos"]
    valido = dados["valido"]

    # Fundo transparente / slate escuro combinando com a interface
    img = Image.new("RGBA", (largura, altura), (15, 23, 42, 255))
    draw = ImageDraw.Draw(img)

    if not valido:
        # Linha fina central para audios vazios ou sem sinal
        cy = altura // 2
        draw.line([(2, cy), (largura - 2, cy)], fill=(71, 85, 105, 180), width=1)
    else:
        # Barras verticais simetricas
        passo = largura / len(pontos)
        for i, val in enumerate(pontos):
            x = int(i * passo)
            bar_h = max(2, int(val * (altura - 4)))
            y0 = (altura - bar_h) // 2
            y1 = y0 + bar_h

            # Gradiente de cor: ciano (#38bdf8) para som ativo, slate escuro (#334155) para silêncio
            if val > 0.15:
                cor = (56, 189, 248, 255)
            elif val > 0.05:
                cor = (14, 165, 233, 220)
            else:
                cor = (51, 65, 85, 180)

            draw.line([(x, y0), (x, y1)], fill=cor, width=1)

    photo = ImageTk.PhotoImage(img)
    _sparkline_cache[cache_key] = photo
    return photo


def gerar_onda_texto(caminho_wav: Path, num_barras: int = 18) -> str:
    """Gera uma representacao em texto/caracteres Unicode (sparkline) da forma de onda.

    Permite exibicao nativa em colunas de dados do Treeview com alinhamento perfeito,
    posicionada logo apos o nome do arquivo.
    """
    p = Path(caminho_wav)
    stat = p.stat() if p.exists() else None
    cache_key = (
        str(p.resolve()) if stat else str(p),
        getattr(stat, "st_mtime", 0),
        getattr(stat, "st_size", 0),
        num_barras
    )

    if cache_key in _text_waveform_cache:
        return _text_waveform_cache[cache_key]

    dados = extrair_amostras_waveform(p, num_pontos=num_barras)
    pontos = dados.get("pontos", [])
    valido = dados.get("valido", False)

    if not valido or not pontos:
        res = "·" * num_barras
    else:
        chars = []
        n_bars = len(BARS_UNICODE)
        for val in pontos:
            idx = int(val * (n_bars - 1))
            idx = max(0, min(n_bars - 1, idx))
            chars.append(BARS_UNICODE[idx])
        res = "".join(chars)

    _text_waveform_cache[cache_key] = res
    return res


