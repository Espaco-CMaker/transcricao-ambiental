"""Script para analise profunda e extracao cronologica das transcricoes do dia.
"""

import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
TRANSCRICOES_DIR = BASE_DIR / "transcricoes"

def analisar():
    arquivos = sorted(TRANSCRICOES_DIR.glob("*2026-11-17*.md"))
    print(f"Encontrados {len(arquivos)} arquivos de transcricao de hoje:")
    
    padrao = re.compile(r"^-\s+`\[(\d+):(\d+):(\d+)\s+->\s+(\d+):(\d+):(\d+)\]`\s+(.*)$")
    
    for arq in arquivos:
        print("=" * 70)
        print(f"ARQUIVO: {arq.name} ({arq.stat().st_size} bytes)")
        print("=" * 70)
        
        linhas = arq.read_text(encoding="utf-8").splitlines()
        falas = []
        for l in linhas:
            m = padrao.match(l.strip())
            if m:
                h1, m1, s1 = int(m.group(1)), int(m.group(2)), int(m.group(3))
                h2, m2, s2 = int(m.group(4)), int(m.group(5)), int(m.group(6))
                texto = m.group(7).strip()
                t_ini_seg = h1 * 3600 + m1 * 60 + s1
                t_fim_seg = h2 * 3600 + m2 * 60 + s2
                falas.append((t_ini_seg, t_fim_seg, f"{h1:02d}:{m1:02d}:{s1:02d}", texto))
        
        print(f"Total de falas extraidas: {len(falas)}")
        if not falas:
            continue
            
        dur_total_min = falas[-1][1] // 60
        print(f"Duracao total aproximada: {dur_total_min} minutos")
        
        # Agrupamento a cada 10 minutos
        intervalo = 10 * 60
        max_t = falas[-1][1]
        num_blocos = (max_t // intervalo) + 1
        
        blocos = {i: [] for i in range(num_blocos)}
        for ini, fim, t_str, txt in falas:
            bloco_idx = ini // intervalo
            if bloco_idx in blocos:
                blocos[bloco_idx].append((t_str, txt))
                
        for b_idx, itens in blocos.items():
            if not itens:
                continue
            min_ini = b_idx * 10
            min_fim = (b_idx + 1) * 10
            print(f"\n--- BLOCO [{min_ini:02d}:00 as {min_fim:02d}:00] ({len(itens)} falas) ---")
            # Mostra resumo das falas do bloco
            texto_unido = " ".join([t for _, t in itens])
            print("Trecho inicial: " + texto_unido[:400] + "...")

if __name__ == "__main__":
    analisar()

