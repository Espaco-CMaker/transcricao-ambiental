"""Script para mapeamento cronologico detalhado das equipes nos Blocos 1 e 2.
Bloco 1 (08:11:41): 2 equipes.
Bloco 2 (09:44:49): 5 equipes.
"""

from datetime import datetime, timedelta
from pathlib import Path
import re

t1_base = datetime.strptime('2026-11-17 08:11:41', '%Y-%m-%d %H:%M:%S')
t2_base = datetime.strptime('2026-11-17 09:44:49', '%Y-%m-%d %H:%M:%S')

def parse_time(ts_str):
    parts = [int(p) for p in ts_str.split(':')]
    if len(parts) == 3:
        return timedelta(hours=parts[0], minutes=parts[1], seconds=parts[2])
    return timedelta(minutes=parts[0], seconds=parts[1])

def process_file(file_path, base_time, block_name):
    print(f"\n{'='*30} {block_name} {'='*30}")
    lines = Path(file_path).read_text(encoding='utf-8').splitlines()
    
    events = []
    for i, line in enumerate(lines):
        m = re.search(r'\[(\d+:\d+:\d+) -> (\d+:\d+:\d+)\]\s*(.*)', line)
        if not m:
            continue
        start_ts, end_ts, text = m.group(1), m.group(2), m.group(3).strip()
        wall_start = base_time + parse_time(start_ts)
        wall_end = base_time + parse_time(end_ts)
        
        events.append({
            'idx': i + 1,
            'rel_start': start_ts,
            'rel_end': end_ts,
            'wall_start': wall_start,
            'wall_end': wall_end,
            'text': text
        })
    return events

events1 = process_file('transcricoes/transcricao_2026-11-17_08-11-41.md', t1_base, 'BLOCO 1')
events2 = process_file('transcricoes/transcricao_2026-11-17_09-44-49.md', t2_base, 'BLOCO 2')

# Let's search Block 2 for key boundaries and transitions between the 5 teams
print(f"\nTotal falas Bloco 2: {len(events2)}")
for ev in events2:
    txt = ev['text'].lower()
    if any(k in txt for k in ['grupo', 'equipe', 'próxim', 'começar', 'obrigado', 'valeu', 'parabéns', 'apresentação', 'apresentar', 'passar para']):
        # Filter for transitions, calls or closings
        if any(w in txt for w in ['próxim', 'equipe', 'grupo', 'obrigado', 'parabéns', 'começar', 'fechou', 'passar', 'cadê']):
            print(f"[{ev['rel_start']} | {ev['wall_start'].strftime('%H:%M:%S')}] L{ev['idx']}: {ev['text'][:120]}")

