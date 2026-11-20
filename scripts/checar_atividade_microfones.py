"""Script para checar todos os dispositivos de entrada de audio e filtrar
apenas aqueles que apresentarem atividade real de sinal sonoro.
"""

import sys
import time
import math
import json
from pathlib import Path
import numpy as np
import sounddevice as sd

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_FILE = BASE_DIR / "data" / "recorder_config.json"

def main():
    print("=" * 65)
    print("  DIAGNÓSTICO DE ENTRADAS DE ÁUDIO COM ATIVIDADE DE SINAL")
    print("=" * 65)

    # 1. Verifica configuracao atual
    cfg_device_id = None
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                cfg = json.load(f)
                cfg_device_id = cfg.get("device_id")
                print(f"Dispositivo atualmente configurado no app: ID {cfg_device_id} ({cfg.get('device_name')})")
        except Exception:
            pass

    devices = sd.query_devices()
    hostapis = {i: h['name'] for i, h in enumerate(sd.query_hostapis())}
    try:
        default_input = sd.default.device[0]
    except Exception:
        default_input = None

    print(f"Dispositivo padrão do Windows: ID {default_input}")
    print("\nTestando microfones do sistema (capturando sinal de 1 segundo em cada)...")
    print("-" * 65)

    dispositivos_ativos = []
    dispositivos_testados = 0

    for idx, dev in enumerate(devices):
        if dev["max_input_channels"] <= 0:
            continue

        dispositivos_testados += 1
        dev_name = dev["name"]
        api_name = hostapis.get(dev["hostapi"], "")
        sr = int(dev.get("default_samplerate", 16000))

        # Tenta capturar 0.8s de áudio
        frames_to_read = int(sr * 0.8)
        try:
            rec_data = sd.rec(
                frames=frames_to_read,
                samplerate=sr,
                channels=1,
                device=idx,
                dtype="float32",
                blocking=True
            )

            audio = rec_data.flatten()
            rms = float(np.sqrt(np.mean(audio**2)))
            peak = float(np.max(np.abs(audio)))
            db = 20 * math.log10(rms + 1e-9)

            # Critério de atividade: sinal acima do ruído de fundo absoluto
            # RMS > 0.001 ou Peak > 0.005 ou dB > -55 dB
            tem_atividade = (rms > 0.0008 or peak > 0.004) and (db > -58.0)

            if tem_atividade:
                dispositivos_ativos.append({
                    "id": idx,
                    "name": dev_name,
                    "api": api_name,
                    "sr": sr,
                    "rms": rms,
                    "peak": peak,
                    "db": db,
                    "is_current": (idx == cfg_device_id),
                    "is_default": (idx == default_input)
                })

        except Exception as e:
            # Dispositivo ocupado ou incompativel com a taxa
            pass

    print(f"\nTotal de entradas analisadas: {dispositivos_testados}")
    print(f"Entradas com ATIVIDADE DE ÁUDIO DETECTADA: {len(dispositivos_ativos)}\n")

    if dispositivos_ativos:
        print(f"{'ID':<4} | {'Dispositivo':<42} | {'API':<12} | {'Nível (dB)':<10} | {'Status'}")
        print("-" * 85)
        for d in dispositivos_ativos:
            status = []
            if d["is_current"]:
                status.append("CONFIGURADO NO APP")
            if d["is_default"]:
                status.append("PADRÃO WINDOWS")
            status_str = " [" + ", ".join(status) + "]" if status else ""

            # Barra visual de nível
            bar_len = int(max(0, min(15, (d["db"] + 60) / 4)))
            barra = "█" * bar_len

            print(f"[{d['id']:2d}] | {d['name'][:40]:<42} | {d['api']:<12} | {d['db']:>5.1f} dB {barra:<15} | Ativo{status_str}")
        print("-" * 85)
    else:
        print(">>> ATENÇÃO: Nenhuma entrada apresentou sinal de áudio significativo no momento.")
        print("    Possíveis causas:")
        print("    1. O microfone físico está com chave 'Mute' ou botão desligado.")
        print("    2. O volume do microfone está em 0% nas Configurações de Som do Windows.")
        print("    3. A permissão de microfone do Windows está desabilitada para aplicativos.")
        print("    4. O headset Bluetooth está conectado apenas como 'Fone de Ouvido' e não 'Headset'.")

    # Salva o melhor dispositivo ativo se o atual estiver mudo
    if dispositivos_ativos and (cfg_device_id is None or not any(d["id"] == cfg_device_id for d in dispositivos_ativos)):
        melhor = max(dispositivos_ativos, key=lambda x: x["rms"])
        print(f"\nRecomendação: O dispositivo com sinal mais forte é o ID [{melhor['id']}] {melhor['name']} ({melhor['db']:.1f} dB).")

if __name__ == "__main__":
    main()

