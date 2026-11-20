"""Modulo de transcricao continua de audio com Faster-Whisper.
Processa fragmentos de audio em fila em segundo plano e transcreve arquivos completos.
"""

import os
import re
import queue
import threading
import datetime
import traceback
from pathlib import Path
from typing import Callable, Optional, Tuple, List
import numpy as np

try:
    from scripts.logger_audit import get_logger
except ImportError:
    from logger_audit import get_logger

BASE_DIR = Path(__file__).resolve().parent.parent
TRANSCRICOES_DIR = BASE_DIR / "transcricoes"
TRANSCRICOES_DIR.mkdir(parents=True, exist_ok=True)


def calcular_horarios_arquivo(audio_path: Path, duracao_segundos: float = 0.0) -> Tuple[datetime.datetime, datetime.datetime]:
    """Calcula os horarios de inicio e termino da gravacao a partir do arquivo.
    Adota a data e hora do arquivo como referencia de TERMINO (fim da gravacao)
    e calcula a hora de INICIO subtraindo a duracao do audio.
    """
    dt_fim = None
    try:
        if audio_path.exists():
            st = audio_path.stat()
            dt_fim = datetime.datetime.fromtimestamp(st.st_mtime)
    except Exception:
        pass

    # Verifica se ha carimbo no nome do arquivo (YYYY-MM-DD_HH-MM-SS)
    m = re.search(r'(\d{4}-\d{2}-\d{2})_(\d{2})-(\d{2})-(\d{2})', audio_path.name)
    if m:
        try:
            dt_nome = datetime.datetime.strptime(
                f"{m.group(1)} {m.group(2)}:{m.group(3)}:{m.group(4)}",
                "%Y-%m-%d %H:%M:%S"
            )
            # Se dt_fim for nulo ou se a data do mtime for de dia diferente
            # (ex: arquivo copiado ou transferido recentemente), prioriza a data do nome
            if dt_fim is None or dt_fim.date() != dt_nome.date():
                dt_fim = dt_nome
        except Exception:
            pass

    if dt_fim is None:
        dt_fim = datetime.datetime.now()

    dur_sec = max(0.0, float(duracao_segundos))
    dt_inicio = dt_fim - datetime.timedelta(seconds=dur_sec)

    return dt_inicio, dt_fim


def ajustar_tempos_transcricao(caminho_md: Path, audio_path: Optional[Path] = None, duracao_informada: Optional[float] = None) -> bool:
    """Ajusta os timestamps de uma transcricao existente para horarios reais (hora de inicio calculada
    a partir da data/hora de termino do arquivo de audio menos sua duracao).
    """
    if not caminho_md.exists():
        return False

    conteudo = caminho_md.read_text(encoding="utf-8")
    linhas = conteudo.splitlines()

    padrao_seg = re.compile(r'^(-\s*`\[)(\d+:\d+:\d+)(\s*->\s*)(\d+:\d+:\d+)(\]`\s*.*)$')

    def str_to_sec(t_str: str) -> int:
        partes = [int(p) for p in t_str.split(':')]
        if len(partes) == 3:
            return partes[0] * 3600 + partes[1] * 60 + partes[2]
        return partes[0] * 60 + partes[1]

    # Se nao foi passado audio_path, tenta encontrar na pasta gravacoes correspondente
    if audio_path is None or not audio_path.exists():
        pref = None
        m_pref = re.search(r'(\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2})', caminho_md.name)
        if m_pref:
            pref = m_pref.group(1)
        # Procura em gravacoes/
        grav_dir = caminho_md.parent.parent / "gravacoes"
        if not grav_dir.exists():
            grav_dir = BASE_DIR / "gravacoes"
        if grav_dir.exists() and pref:
            for w in grav_dir.glob("*.wav"):
                if pref in w.name:
                    audio_path = w
                    break

    duracao_sec = 0.0
    if duracao_informada is not None and duracao_informada > 0:
        duracao_sec = float(duracao_informada)
    elif audio_path and audio_path.exists():
        try:
            import soundfile as sf
            duracao_sec = sf.info(str(audio_path)).duration
        except Exception:
            pass

    # Se duracao_sec ainda for 0, infere a partir do ultimo segmento da transcricao
    if duracao_sec <= 0.0:
        for l in reversed(linhas):
            m = padrao_seg.match(l.strip())
            if m:
                ultimo_seg_sec = str_to_sec(m.group(4))
                if ultimo_seg_sec > 0:
                    duracao_sec = float(ultimo_seg_sec)
                break

    ref_path = audio_path if (audio_path and audio_path.exists()) else caminho_md
    dt_inicio, dt_fim = calcular_horarios_arquivo(ref_path, duracao_sec)

    # Verifica se os timestamps comecam em 0:00:00 ou similar (relativos)
    primeiro_seg_sec = None
    for l in linhas:
        m = padrao_seg.match(l.strip())
        if m:
            primeiro_seg_sec = str_to_sec(m.group(2))
            break
        if m:
            primeiro_seg_sec = str_to_sec(m.group(2))
            break

    precisa_ajustar = (primeiro_seg_sec is not None and primeiro_seg_sec < 3600)

    novas_linhas = []
    modificado = False

    for l in linhas:
        m = padrao_seg.match(l.strip())
        if m and precisa_ajustar:
            sec_ini = str_to_sec(m.group(2))
            sec_fim = str_to_sec(m.group(4))
            t_abs_ini = dt_inicio + datetime.timedelta(seconds=sec_ini)
            t_abs_fim = dt_inicio + datetime.timedelta(seconds=sec_fim)
            novo_ini_str = t_abs_ini.strftime("%H:%M:%S")
            novo_fim_str = t_abs_fim.strftime("%H:%M:%S")
            nova_linha = f"{m.group(1)}{novo_ini_str}{m.group(3)}{novo_fim_str}{m.group(5)}"
            novas_linhas.append(nova_linha)
            modificado = True
        else:
            novas_linhas.append(l)

    if modificado:
        caminho_md.write_text("\n".join(novas_linhas) + "\n", encoding="utf-8")
        return True

    return False


class TranscriberEngine:
    def __init__(self, model_size: str = "base", device: str = "auto", language: str = "pt"):
        self.model_size = model_size
        self.device = device
        self.language = language
        self.model = None
        self._lock = threading.Lock()
        self.task_queue: queue.Queue = queue.Queue()
        self.is_running = False
        self.worker_thread: Optional[threading.Thread] = None
        self.subscribers: list[Callable[[dict], None]] = []
        self.current_transcription_file: Optional[Path] = None
        self._cancel_transcription = threading.Event()
        self.last_progress_tick: float = 0.0
        self.is_running = False
        self.worker_thread: Optional[threading.Thread] = None
        self.subscribers: list[Callable[[dict], None]] = []
        self.current_transcription_file: Optional[Path] = None
        self._cancel_transcription = threading.Event()

    def _init_model(self):
        if self.model is None:
            with self._lock:
                if self.model is None:
                    from faster_whisper import WhisperModel
                    import ctranslate2

                    # Verifica se o modelo existe localmente na pasta models/ (modo offline)
                    model_target = self.model_size
                    local_dir = BASE_DIR / "models" / self.model_size
                    if local_dir.exists() and (local_dir / "model.bin").exists():
                        model_target = str(local_dir)
                        print(f"[TRANSCRIBER] Utilizando modelo offline local: {local_dir}")

                    actual_device = self.device
                    if actual_device == "auto":
                        try:
                            actual_device = "cuda" if ctranslate2.get_cuda_device_count() > 0 else "cpu"
                        except Exception:
                            actual_device = "cpu"

                    if actual_device == "cuda":
                        try:
                            print("[TRANSCRIBER] Validando suporte a CUDA no dispositivo...")
                            test_model = WhisperModel(model_target, device="cuda", compute_type="float16")
                            # Teste rapido de warm-up para certificar que cublas64_12.dll e cudnn estao presentes
                            dummy_segs, _ = test_model.transcribe(np.zeros(1600, dtype=np.float32), beam_size=1)
                            list(dummy_segs)
                            self.model = test_model
                            print("[TRANSCRIBER] Aceleracao GPU CUDA validada e operacional!")
                        except Exception as e_cuda:
                            print(f"[TRANSCRIBER] CUDA indisponivel ou DLLs ausentes ({e_cuda}). Utilizando CPU (int8)...")
                            self.model = WhisperModel(model_target, device="cpu", compute_type="int8")
                    else:
                        print(f"[TRANSCRIBER] Carregando modelo Whisper '{self.model_size}' em CPU (int8)...")
                        self.model = WhisperModel(model_target, device="cpu", compute_type="int8")

                    print("[TRANSCRIBER] Modelo Whisper pronto para uso.")

    def set_model(self, model_size: str, device: str = "auto", language: str = "pt"):
        with self._lock:
            self.model_size = model_size
            self.device = device
            self.language = language
            self.model = None # Recarrega no proximo uso

    def add_subscriber(self, callback: Callable[[dict], None]):
        if callback not in self.subscribers:
            self.subscribers.append(callback)

    def remove_subscriber(self, callback: Callable[[dict], None]):
        if callback in self.subscribers:
            self.subscribers.remove(callback)

    def _broadcast(self, data: dict):
        for cb in list(self.subscribers):
            try:
                cb(data)
            except Exception:
                pass

    def start_worker(self):
        if self.worker_thread and self.worker_thread.is_alive():
            return
        self.is_running = True
        self.worker_thread = threading.Thread(target=self._worker_loop, daemon=True, name="TranscriberWorker")
        self.worker_thread.start()
        print("[TRANSCRIBER] Thread de transcricao em segundo plano iniciada.")

    def stop_worker(self):
        self.is_running = False
        self.task_queue.put(None) # Sinal de encerramento
        if self.worker_thread:
            self.worker_thread.join(timeout=2.0)

    def enqueue_chunk(self, audio_data: np.ndarray, samplerate: int, md_file_path: Path, timestamp_str: str, time_offset_sec: float):
        """Enfileira um trecho de audio em memoria para transcricao."""
        item = {
            "type": "chunk",
            "audio": audio_data,
            "samplerate": samplerate,
            "md_path": md_file_path,
            "timestamp": timestamp_str,
            "offset_sec": time_offset_sec
        }
        self.task_queue.put(item)

    def _sanitize_text(self, text: str) -> str:
        """Remove travessoes e meias-riscas conforme regras obrigatorias."""
        text = text.replace("\u2014", " - ").replace("\u2013", " - ")
        return text.strip()

    def _worker_loop(self):
        while self.is_running:
            try:
                task = self.task_queue.get(timeout=1.0)
            except queue.Empty:
                continue

            if task is None:
                break

            try:
                self._process_task(task)
            except Exception as e:
                print(f"[TRANSCRIBER] Erro ao processar trecho de transcricao: {e}")
                traceback.print_exc()
            finally:
                self.task_queue.task_done()

    def _process_task(self, task: dict):
        self._init_model()
        audio = task["audio"]
        samplerate = task["samplerate"]
        md_path = Path(task["md_path"])
        offset_sec = task["offset_sec"]

        # Converte para float32 normalizado se necessario
        if audio.dtype != np.float32:
            audio = audio.astype(np.float32)

        # Se for stereo, converte para mono
        if audio.ndim > 1:
            audio = np.mean(audio, axis=1)

        # Se estiver em escala int16, divide por 32768.0
        max_val = np.max(np.abs(audio))
        if max_val > 1.0:
            audio = audio / 32768.0

        # Silencio: se energia muito baixa, nao transcreve
        rms = np.sqrt(np.mean(audio**2))
        if rms < 0.003: # Limiar de silencio de sala
            return

        segments, info = self.model.transcribe(
            audio,
            language=self.language,
            vad_filter=True,
            vad_parameters=dict(min_silence_duration_ms=500),
            beam_size=5
        )

        detected_texts = []
        for segment in segments:
            text = self._sanitize_text(segment.text)
            if not text:
                continue

            seg_start = offset_sec + segment.start
            seg_end = offset_sec + segment.end
            
            str_start = str(datetime.timedelta(seconds=int(seg_start)))
            str_end = str(datetime.timedelta(seconds=int(seg_end)))
            
            line = f"- `[{str_start} -> {str_end}]` {text}\n"
            detected_texts.append((str_start, str_end, text, line))

        if detected_texts:
            self._append_to_md(md_path, [d[3] for d in detected_texts])
            for d in detected_texts:
                payload = {
                    "type": "new_segment",
                    "file": md_path.name,
                    "start": d[0],
                    "end": d[1],
                    "text": d[2]
                }
                self._broadcast(payload)

    def _append_to_md(self, md_path: Path, lines: list[str]):
        """Adiciona linhas de texto ao arquivo Markdown do dia com seguranca."""
        md_path.parent.mkdir(parents=True, exist_ok=True)
        is_new = not md_path.exists()

        with open(md_path, "a", encoding="utf-8") as f:
            if is_new:
                data_hoje = datetime.date.today().strftime("%d/%m/%Y")
                f.write(f"# Transcricao de Audio da Sala: {data_hoje}\n\n")
                f.write(f"> Arquivo iniciado em: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n")
                f.write("## Registro Cronologico de Falas\n\n")

            for line in lines:
                f.write(line)
            f.flush()

    def request_cancel_transcription(self):
        """Sinaliza solicitacao de cancelamento para a transcricao em andamento."""
        self._cancel_transcription.set()
        print("[TRANSCRIBER] Solicitacao de cancelamento de transcricao recebida.")

    def transcribe_full_file(self, audio_path: Path, output_md_path: Optional[Path] = None, progress_cb: Optional[Callable[[dict], None]] = None) -> Optional[Path]:
        """Transcreve um arquivo de audio completo do disco com suporte a cancelamento sob demanda."""
        logger = get_logger()
        logger.info("TRANSCRICAO", "INICIAR", f"Iniciando transcricao de: {audio_path.name}")
        self.last_progress_tick = datetime.datetime.now().timestamp()
        self._cancel_transcription.clear()

        if progress_cb:
            progress_cb({
                "percent": 0.0,
                "current_sec": 0,
                "total_sec": 0,
                "canceled": False,
                "message": "Carregando modelo e decodificando arquivo de áudio..."
            })

        self._init_model()

        if output_md_path is None:
            nome_base = audio_path.stem.replace("gravando_", "transcricao_").replace("gravacao_", "transcricao_")
            if audio_path.parent.name == "gravacoes":
                dest_dir = audio_path.parent.parent / "transcricoes"
                dest_dir.mkdir(parents=True, exist_ok=True)
                output_md_path = dest_dir / f"{nome_base}.md"
            else:
                output_md_path = TRANSCRICOES_DIR / f"{nome_base}.md"

        if progress_cb:
            progress_cb({
                "percent": 0.0,
                "current_sec": 0,
                "total_sec": 0,
                "canceled": False,
                "message": "Executando VAD (detecção de voz) e preparando segmentos..."
            })

        try:
            segments, info = self.model.transcribe(
                str(audio_path),
                language=self.language,
                beam_size=5,
                vad_filter=True
            )
            total_duration = info.duration if info.duration and info.duration > 0 else 1.0
        except Exception as e_trans:
            logger.warn("TRANSCRICAO", "FALLBACK_CPU", f"Falha no motor GPU ({e_trans}). Alternando para CPU (int8)...")
            print(f"[TRANSCRIBER] Falha na inicializacao ({e_trans}). Alternando para CPU (int8)...")
            from faster_whisper import WhisperModel
            local_dir = BASE_DIR / "models" / self.model_size
            m_target = str(local_dir) if (local_dir / "model.bin").exists() else self.model_size
            self.model = WhisperModel(m_target, device="cpu", compute_type="int8")
            segments, info = self.model.transcribe(
                str(audio_path),
                language=self.language,
                beam_size=5,
                vad_filter=True
            )
            total_duration = info.duration if info.duration and info.duration > 0 else 1.0

        if progress_cb:
            progress_cb({
                "percent": 0.0,
                "current_sec": 0,
                "total_sec": int(total_duration),
                "canceled": False,
                "message": "Decodificando falas com Whisper..."
            })

        count = 0
        canceled = False

        dt_inicio, dt_fim = calcular_horarios_arquivo(audio_path, total_duration)

        with open(output_md_path, "w", encoding="utf-8") as f:
            data_gravacao = dt_inicio.strftime("%d/%m/%Y")
            hora_ini_str = dt_inicio.strftime("%H:%M:%S")
            hora_fim_str = dt_fim.strftime("%H:%M:%S")
            dur_total_fmt = str(datetime.timedelta(seconds=int(total_duration)))

            f.write(f"# Transcricao Completa da Gravacao: {audio_path.name}\n\n")
            f.write(f"> Arquivo de audio: `{audio_path.name}`\n")
            f.write(f"> Data da Gravacao: {data_gravacao}\n")
            f.write(f"> Horario de Inicio (Calculado): {hora_ini_str}\n")
            f.write(f"> Horario de Termino (Referencia do Arquivo): {hora_fim_str}\n")
            f.write(f"> Duracao Total: {dur_total_fmt}\n")
            f.write(f"> Processado em: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
            f.write(f"> Idioma detectado: {info.language} (confianca: {info.language_probability:.2f})\n\n")
            f.write("## Registro Cronologico de Falas\n\n")

            for segment in segments:
                self.last_progress_tick = datetime.datetime.now().timestamp()
                if self._cancel_transcription.is_set():
                    canceled = True
                    f.write("\n> [AVISO: Transcrição interrompida/cancelada pelo usuário]\n")
                    f.flush()
                    logger.info("TRANSCRICAO", "CANCELAMENTO", f"Transcricao cancelada pelo usuario: {audio_path.name}")
                    print(f"[TRANSCRIBER] Transcricao interrompida pelo usuario: {audio_path.name}")
                    break

                text = self._sanitize_text(segment.text)
                if not text:
                    continue

                t_seg_ini = dt_inicio + datetime.timedelta(seconds=int(segment.start))
                t_seg_fim = dt_inicio + datetime.timedelta(seconds=int(segment.end))
                str_start = t_seg_ini.strftime("%H:%M:%S")
                str_end = t_seg_fim.strftime("%H:%M:%S")

                f.write(f"- `[{str_start} -> {str_end}]` {text}\n")
                f.flush()
                count += 1
                if progress_cb:
                    pct = min(100.0, max(0.0, (segment.end / total_duration) * 100.0))
                    dur_cur_fmt = str(datetime.timedelta(seconds=int(segment.end)))
                    progress_cb({
                        "percent": round(pct, 1),
                        "current_sec": int(segment.end),
                        "total_sec": int(total_duration),
                        "segments_count": count,
                        "canceled": False,
                        "message": f"Transcrevendo: {pct:.1f}% ({dur_cur_fmt} / {dur_total_fmt} | {str_end})"
                    })

        if canceled:
            if progress_cb:
                progress_cb({
                    "percent": 0.0,
                    "canceled": True,
                    "segments_count": count,
                    "message": f"Transcrição cancelada pelo usuário ({count} falas salvas)."
                })
            return None

        logger.info("TRANSCRICAO", "CONCLUSAO", f"Transcricao 100% concluida: {output_md_path.name} ({count} falas)")
        if progress_cb:
            progress_cb({
                "percent": 100.0,
                "current_sec": int(total_duration),
                "total_sec": int(total_duration),
                "segments_count": count,
                "canceled": False,
                "message": f"Transcricao 100% concluida ({count} falas)!"
            })

        return output_md_path
