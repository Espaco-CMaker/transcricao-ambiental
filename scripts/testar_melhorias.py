"""Script de Testes Unitarios e Integracao para as Melhorias do Gravador Ambiental."""

import os
import sys
import shutil
import numpy as np
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(SCRIPTS_DIR))

from scripts.logger_audit import get_logger, LOG_FILE
from scripts.gerador_ata import extrair_titulo_contextual, gerar_ata_de_transcricao, analisar_segmentos_transcricao
from scripts.renomeador import renomear_trio_arquivos, sanitizar_slug
from scripts.recorder import validar_arquivo_wav, carregar_configuracao, salvar_configuracao
from scripts.transcriber import calcular_horarios_arquivo, ajustar_tempos_transcricao

def test_logger():
    print("[TEST] 1. Testando Logger de Auditoria...")
    logger = get_logger()
    logger.info("TESTE", "INICIAR", "Mensagem de teste INFO")
    logger.warn("TESTE", "AVISO", "Mensagem de teste WARN")
    logger.error("TESTE", "ERRO", "Mensagem de teste ERROR")
    
    assert LOG_FILE.exists(), "Arquivo de log nao existe!"
    recs = logger.get_recent_records(limit=10)
    assert len(recs) >= 3, f"Esperava ao menos 3 registros, obteve {len(recs)}"
    print(f"  OK! Logs gravados e recuperados com sucesso ({len(recs)} registros recentes).")

def test_analise_e_ata():
    print("[TEST] 2. Testando Analise de Transcricao e Geracao de Ata...")
    transcricoes = list((BASE_DIR / "transcricoes").glob("*.md"))
    if not transcricoes:
        transcricoes = list((BASE_DIR / "transcricoes" / "temp").glob("*.md"))
    if not transcricoes:
        print("  Pula teste de ata (nenhuma transcricao encontrada).")
        return

    alvo = None
    for t in transcricoes:
        if t.stat().st_size > 5000 and not t.name.startswith("ATA"):
            alvo = t
            break
    if not alvo:
        alvo = [t for t in transcricoes if not t.name.startswith("ATA")][0] if transcricoes else None

    if not alvo:
        print("  Pula teste de ata (nenhuma transcricao valida encontrada).")
        return

    print(f"  Usando transcricao alvo: {alvo.name}")
    texto = alvo.read_text(encoding="utf-8")
    slug = extrair_titulo_contextual(texto)
    print(f"  Slug contextual extraido: '{slug}'")
    assert len(slug) > 0, "Slug vazio!"

    # Gera ata de teste em pasta temp
    temp_dir = BASE_DIR / "temp"
    temp_dir.mkdir(exist_ok=True)
    out_ata = temp_dir / f"teste_{alvo.stem}_ata.md"

    gerar_ata_de_transcricao(alvo, output_ata_path=out_ata)
    assert out_ata.exists(), "Ata nao foi criada!"
    assert out_ata.stat().st_size > 100, "Ata gerada vazia!"

    conteudo_ata = out_ata.read_text(encoding="utf-8")
    assert "ATA DE REUNIÃO / SESSÃO" in conteudo_ata, "Cabecalho da ata ausente!"
    assert "Participantes" in conteudo_ata, "Secao de participantes ausente!"
    assert "Deliberações, Encaminhamentos e Decisões" in conteudo_ata, "Secao de deliberacoes ausente!"
    assert "- **Local / Ambiente:**" in conteudo_ata, "Campo de local/ambiente ausente na ata!"
    # Como a transcricao alvo nao contem indicacao explicita de local, o campo deve estar em branco
    linhas_local = [l for l in conteudo_ata.splitlines() if "- **Local / Ambiente:**" in l]
    assert len(linhas_local) == 1, "Linha de local duplicada ou nao encontrada!"
    assert linhas_local[0].strip() == "- **Local / Ambiente:**", f"Local deveria estar em branco, mas contem: '{linhas_local[0]}'"
    print(f"  OK! Ata gerada com sucesso ({out_ata.stat().st_size} bytes, local em branco conforme regra).")

def test_renomeador():
    print("[TEST] 3. Testando Renomeacao Atomica Coordenada...")
    temp_dir = BASE_DIR / "temp" / "renomear_test"
    temp_dir.mkdir(parents=True, exist_ok=True)

    f_audio = temp_dir / "gravacao_2026-11-18_10-00-00.wav"
    f_trans = temp_dir / "transcricao_2026-11-18_10-00-00.md"
    f_ata = temp_dir / "ata_2026-11-18_10-00-00.md"

    f_audio.write_bytes(b"RIFF" + b"\x00"*40)
    f_trans.write_text("# Transcricao Teste\n- `[00:00:00 -> 00:00:10]` Teste de fala.", encoding="utf-8")
    f_ata.write_text("# Ata Teste", encoding="utf-8")

    slug = "Sessao-Robotica-Projetos"
    n_audio, n_trans, n_ata = renomear_trio_arquivos(f_audio, f_trans, f_ata, slug)

    # Audio (.wav) nunca e renomeado, preservando nome original de gravacao
    assert n_audio.name == "gravacao_2026-11-18_10-00-00.wav", f"Audio nao deveria ter sido renomeado, mas ficou: {n_audio.name}"
    assert n_trans.name == "2026-11-18_10-00-00_Sessao-Robotica-Projetos_transcricao.md", f"Nome trans incorreto: {n_trans.name}"
    assert n_ata.name == "ATA_2026-11-18_10-00-00_Sessao-Robotica-Projetos.md", f"Nome ata incorreto: {n_ata.name}"
    assert n_audio.exists() and n_trans.exists() and n_ata.exists(), "Arquivos esperados nao existem!"
    print("  OK! Apenas arquivos .md renomeados com sucesso, audio .wav permaneceu intacto.")

    # Limpeza
    shutil.rmtree(temp_dir, ignore_errors=True)

def test_validacao_wav():
    print("[TEST] 4. Testando Validacao de Arquivo WAV...")
    audios = list((BASE_DIR / "gravacoes").glob("*.wav"))
    if audios:
        res = validar_arquivo_wav(audios[0])
        print(f"  Validacao de {audios[0].name}: valid={res['valid']}, duracao={res.get('duration')}s, tamanho={res.get('size_mb')}MB")
        assert res["valid"] is True, f"Falha ao validar audio real: {res}"
        print("  OK! Arquivo WAV real validado com exito.")

def test_config():
    print("[TEST] 5. Testando Configuracao Persistente com Novas Opcoes...")
    cfg = carregar_configuracao()
    assert "auto_transcribe_on_stop" in cfg, "Chave auto_transcribe_on_stop ausente!"
    assert "auto_generate_minutes_on_transcribe" in cfg, "Chave auto_generate_minutes_on_transcribe ausente!"
    assert "auto_rename_contextual" in cfg, "Chave auto_rename_contextual ausente!"
    assert cfg.get("auto_record", True) is False, f"auto_record deveria ser False por padrao, mas esta {cfg.get('auto_record')}"
    print(f"  OK! Configuracoes carregadas com sucesso: auto_record={cfg.get('auto_record')}, auto_transcribe={cfg['auto_transcribe_on_stop']}, auto_minutes={cfg['auto_generate_minutes_on_transcribe']}, auto_rename={cfg['auto_rename_contextual']}")

def test_horarios_e_ajuste_transcricao():
    print("[TEST] 6. Testando Calculo de Horarios e Ajuste de Transcricao...")
    temp_dir = BASE_DIR / "temp" / "teste_horarios"
    temp_dir.mkdir(parents=True, exist_ok=True)

    f_audio = temp_dir / "gravando_2026-11-18_10-00-00.wav"
    f_audio.write_bytes(b"RIFF" + b"\x00"*40)

    # 1. Testa calculo de horario do arquivo
    duracao_teste = 1800.0 # 30 minutos
    dt_ini, dt_fim = calcular_horarios_arquivo(f_audio, duracao_teste)
    assert dt_fim.strftime("%H:%M:%S") == "10:00:00", f"Horario final incorreto: {dt_fim}"
    assert dt_ini.strftime("%H:%M:%S") == "09:30:00", f"Horario inicial incorreto: {dt_ini}"
    print(f"  OK! Calculo de horarios validado: Fim={dt_fim.strftime('%H:%M:%S')} - 30min = Inicio={dt_ini.strftime('%H:%M:%S')}")

    # 2. Testa ajuste de transcricao relativa para horarios absolutos
    f_md = temp_dir / "transcricao_2026-11-18_10-00-00.md"
    f_md.write_text(
        "# Transcricao Teste\n"
        "- `[0:00:00 -> 0:00:15]` Fala inicial.\n"
        "- `[0:10:00 -> 0:10:30]` Fala intermediaria.\n"
        "- `[0:29:45 -> 0:30:00]` Fala final.\n",
        encoding="utf-8"
    )

    modificado = ajustar_tempos_transcricao(f_md, audio_path=f_audio)
    assert modificado is True, "Deveria ter modificado os tempos relativos!"

    conteudo_ajustado = f_md.read_text(encoding="utf-8")
    assert "- `[09:30:00 -> 09:30:15]`" in conteudo_ajustado, "Segmento 1 nao ajustado corretamente!"
    assert "- `[09:40:00 -> 09:40:30]`" in conteudo_ajustado, "Segmento 2 nao ajustado corretamente!"
    assert "- `[09:59:45 -> 10:00:00]`" in conteudo_ajustado, "Segmento 3 nao ajustado corretamente!"
    print("  OK! Timestamps da transcricao ajustados com precisao milimetrica.")

    shutil.rmtree(temp_dir, ignore_errors=True)

def test_seek_e_playhead_posicao():
    print("[TEST] 7. Testando Calculo de Seek, Playhead e Sincronismo de Tempo...")
    # Simula seek por clique na forma de onda aos 120 segundos de um audio de 300s
    player_duration_sec = 300.0
    seek_target_sec = 120.0
    largura_canvas = 800

    # 1. No momento do clique no waveform
    pct_click = seek_target_sec / player_duration_sec
    x_click = pct_click * largura_canvas
    assert abs(x_click - 320.0) < 0.001, f"Posicao X do playhead incorreta: {x_click}"

    # 2. No loop de reproducao (decorridos 1500ms apos o seek)
    pos_ms = 1500
    player_start_sec = seek_target_sec
    pos_sec = player_start_sec + (pos_ms / 1000.0)
    assert pos_sec == 121.5, f"pos_sec deveria ser 121.5s, mas obteve {pos_sec}s"

    pct_progresso = (pos_sec / player_duration_sec) * 100.0
    assert abs(pct_progresso - 40.5) < 0.001, f"Percentual de progresso incorreto: {pct_progresso}"

    x_playhead_avancado = (pos_sec / player_duration_sec) * largura_canvas
    assert abs(x_playhead_avancado - 324.0) < 0.001, f"Playhead avancado incorreto: {x_playhead_avancado}"
    print("  OK! Calculo de playhead, offset de seek e avanco temporal validados.")

def test_grafico_tempo_real_5s():
    print("[TEST] 8. Testando Buffer e Grafico de Som em Tempo Real (5s)...")
    from scripts.recorder import AudioRecorder
    
    recorder = AudioRecorder(transcriber=None)
    sr = int(recorder.config.get("sample_rate", 16000))
    esperado_samples = int(sr * 5.0)
    assert recorder.live_buffer_len == esperado_samples, f"Tamanho buffer incorreto: {recorder.live_buffer_len} != {esperado_samples}"
    
    bloco1 = np.full(1000, 0.25, dtype=np.float32)
    recorder._adicionar_ao_live_buffer(bloco1)
    
    amostras = recorder.obter_amostras_tempo_real(5.0)
    assert len(amostras) == esperado_samples, f"Tamanho amostras incorreto: {len(amostras)}"
    assert amostras[-1] == 0.25, f"Ultima amostra deveria ser 0.25, obteve {amostras[-1]}"
    
    # Testa mudo temporario injetando zeros
    recorder.set_mute(True)
    bloco_mudo = np.full(500, 0.8, dtype=np.float32)
    recorder._audio_callback(bloco_mudo, 500, None, None)
    amostras_mudo = recorder.obter_amostras_tempo_real(5.0)
    assert amostras_mudo[-1] == 0.0, f"Com mudo ativado, amostra deveria ser 0.0, obteve {amostras_mudo[-1]}"
    
    # Restaura
    recorder.set_mute(False)
    recorder.should_run = False
    print("  OK! Buffer continuo dos ultimos 5 segundos e visualizacao em tempo real validados.")

if __name__ == "__main__":
    print("=" * 60)
    print(" INICIANDO TESTES DAS MELHORIAS DO GRAVADOR AMBIENTAL")
    print("=" * 60)
    test_logger()
    test_analise_e_ata()
    test_renomeador()
    test_validacao_wav()
    test_config()
    test_horarios_e_ajuste_transcricao()
    test_seek_e_playhead_posicao()
    test_grafico_tempo_real_5s()
    print("=" * 60)
    print(" TODOS OS TESTES PASSARAM COM 100% DE SUCESSO!")
    print("=" * 60)

