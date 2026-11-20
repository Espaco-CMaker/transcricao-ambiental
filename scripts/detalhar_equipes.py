"""Extrator de detalhes de cada uma das 7 equipes (2 no Bloco 1 e 5 no Bloco 2)."""
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

def get_events(path, base):
    lines = Path(path).read_text(encoding='utf-8').splitlines()
    events = []
    for l in lines:
        m = re.search(r'\[(\d+:\d+:\d+) -> (\d+:\d+:\d+)\]\s*(.*)', l)
        if m:
            start_ts, end_ts, text = m.group(1), m.group(2), m.group(3).strip()
            events.append({
                'rel_start': start_ts,
                'rel_end': end_ts,
                'wall_start': base + parse_time(start_ts),
                'wall_end': base + parse_time(end_ts),
                'text': text
            })
    return events

ev1 = get_events('transcricoes/transcricao_2026-11-17_08-11-41.md', t1_base)
ev2 = get_events('transcricoes/transcricao_2026-11-17_09-44-49.md', t2_base)

def print_slice(events, start_wall, end_wall, label):
    print(f"\n{'='*20} {label} ({start_wall} ate {end_wall}) {'='*20}")
    sample = [e for e in events if start_wall <= e['wall_start'].strftime('%H:%M:%S') <= end_wall]
    print(f"Total de falas: {len(sample)}")
    for e in sample[:10]:
        print(f"  [{e['wall_start'].strftime('%H:%M:%S')}] {e['text'][:90]}")
    if len(sample) > 20:
        print("  ...")
        for e in sample[-10:]:
            print(f"  [{e['wall_start'].strftime('%H:%M:%S')}] {e['text'][:90]}")

# Bloco 1
# Equipe 1: 08:12 a 08:52
print_slice(ev1, '08:12:00', '08:52:30', 'BLOCO 1 - EQUIPE 1 (Grupo 9)')
# Equipe 2: 08:53 a 09:13
print_slice(ev1, '08:53:00', '09:13:00', 'BLOCO 1 - EQUIPE 2')

# Bloco 2
# Equipe 1: 09:51 a 10:03
print_slice(ev2, '09:51:00', '10:03:30', 'BLOCO 2 - EQUIPE 1 (Grupo 1: Climatizacao)')
# Equipe 2: 10:04 a 10:33
print_slice(ev2, '10:04:00', '10:33:40', 'BLOCO 2 - EQUIPE 2 (Grupo 2)')
# Equipe 3: 10:45 a 11:20
print_slice(ev2, '10:45:00', '11:20:00', 'BLOCO 2 - EQUIPE 3')
# Equipe 4: 11:20 a 11:41
print_slice(ev2, '11:20:00', '11:41:00', 'BLOCO 2 - EQUIPE 4 (Grupo 3: Ventilacao com ESP)')
# Equipe 5: 11:41 a 12:14
print_slice(ev2, '11:41:00', '12:14:00', 'BLOCO 2 - EQUIPE 5')

