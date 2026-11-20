"""Modulo de gravacao de audio continua com alta resiliencia e selecao de microfone.
Projetado para gravacao continua de salas durante todo o dia com recuperacao automatica.
"""

import os
import re
import json
import time
import math
import queue
import shutil
import threading
import datetime
import traceback
from pathlib import Path
from typing import Optional, Callable
import numpy as np
import sounddevice as sd
import soundfile as sf

try:
    from scripts.logger_audit import get_logger
except ImportError:
    from logger_audit import get_logger

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
CONFIG_FILE = DATA_DIR / "recorder_config.json"
STATE_FILE = DATA_DIR / "recorder_state.json"
DATA_DIR.mkdir(parents=True, exist_ok=True)

DEFAULT_CONFIG = {
    "device_id": None,
    "device_name": None,
    "sample_rate": 16000,
    "channels": 1,
    "chunk_seconds": 30,
    "auto_record": False,
    "model_size": "base",
    "language": "pt",
    "output_dir": str(BASE_DIR),
    "auto_transcribe_on_stop": False,
    "auto_generate_minutes_on_transcribe": False,
    "auto_rename_contextual": True,
    "watchdog_timeout_sec": 120
}

def validar_arquivo_wav(caminho: Path | str) -> dict:
    """Verifica e valida a integridade do arquivo WAV gerado."""
    try:
        p = Path(caminho).resolve()
        if not p.exists():
            return {"valid": False, "error": "Arquivo inexistente"}
        tamanho = p.stat().st_size
        if tamanho < 44:
            return {"valid": False, "error": f"Arquivo muito pequeno ({tamanho} bytes)"}

        info = sf.info(str(p))
        return {
            "valid": True,
            "duration": round(info.duration, 2),
            "samplerate": info.samplerate,
            "channels": info.channels,
            "format": info.format,
            "subtype": info.subtype,
            "size_bytes": tamanho,
            "size_mb": round(tamanho / (1024 * 1024), 2)
        }
    except Exception as e:
        return {"valid": False, "error": str(e)}

def obter_espaco_disco(caminho: Path | str) -> dict:
    """Calcula espaco total, usado, livre e percentual da particao."""
    try:
        p = Path(caminho).resolve()
        # Se a pasta nao existe ainda, busca o pai existente mais proximo
        while not p.exists() and p.parent != p:
            p = p.parent
        total, used, free = shutil.disk_usage(str(p))
        drive = p.drive or str(p)
        return {
            "total_gb": round(total / (1024**3), 1),
            "used_gb": round(used / (1024**3), 1),
            "free_gb": round(free / (1024**3), 1),
            "percent_free": round((free / total) * 100, 1),
            "drive": drive
        }
    except Exception as e:
        return {"total_gb": 0, "used_gb": 0, "free_gb": 0, "percent_free": 0, "drive": "?"}

def carregar_configuracao() -> dict:
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                saved = json.load(f)
                config = DEFAULT_CONFIG.copy()
                config.update(saved)
                return config
        except Exception:
            pass
    return DEFAULT_CONFIG.copy()

def salvar_configuracao(config: dict):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

def listar_microfones() -> list[dict]:
    """Retorna todos os dispositivos de entrada de audio disponiveis no sistema."""
    devices = sd.query_devices()
    hostapis = {i: h['name'] for i, h in enumerate(sd.query_hostapis())}
    try:
        default_input = sd.default.device[0]
    except Exception:
        default_input = None

    resultado = []
    for idx, dev in enumerate(devices):
        if dev["max_input_channels"] > 0:
            api_name = hostapis.get(dev["hostapi"], "")
            resultado.append({
                "id": idx,
                "name": dev["name"],
                "api": api_name,
                "channels": dev["max_input_channels"],
                "default_samplerate": int(dev.get("default_samplerate", 16000)),
                "is_default": (idx == default_input)
            })
    return resultado

class AudioRecorder:
    def __init__(self, transcriber):
        self.transcriber = transcriber
        self.config = carregar_configuracao()
        self.is_recording = False
        self.is_paused = False
        self._lock = threading.Lock()

        # Metricas e estados de execucao
        self.session_id: str = ""
        self.current_audio_file: Optional[Path] = None
        self.last_completed_audio_file: Optional[Path] = None
        self.current_md_file: Optional[Path] = None
        self.current_sf: Optional[sf.SoundFile] = None
        self.stream: Optional[sd.InputStream] = None
        
        self.current_date_str: str = ""
        self.session_start_time: float = 0.0
        self.last_audio_tick: float = 0.0
        self.current_level_rms: float = 0.0
        self.current_level_db: float = -60.0
        self.total_frames_recorded: int = 0
        self.is_muted: bool = False

        # Buffer circular para visualizacao de som em tempo real (ultimos 5 segundos)
        self.live_buffer_seconds: float = 5.0
        sr_inicial = int(self.config.get("sample_rate", 16000))
        self.live_buffer_len: int = int(sr_inicial * self.live_buffer_seconds)
        self.live_buffer = np.zeros(self.live_buffer_len, dtype=np.float32)
        self.live_buffer_pos: int = 0
        self._live_lock = threading.Lock()

        # Buffer para despacho periodico ao transcritor
        self.chunk_buffer = []
        self.chunk_buffer_samples = 0
        self.chunk_target_samples = int(self.config["sample_rate"] * self.config["chunk_seconds"])

        # Controle de watchdog e recuperacao
        self.watchdog_thread: Optional[threading.Thread] = None
        self.should_run = True

        self._iniciar_watchdog()

    def _iniciar_watchdog(self):
        """Monitora e recupera a gravacao caso haja falha ou desconexao."""
        def watchdog_loop():
            while self.should_run:
                time.sleep(2.0)
                if not self.is_recording or self.is_paused:
                    continue

                # 1. Verifica virada de dia (meia-noite)
                hoje = datetime.date.today().strftime("%Y-%m-%d")
                if self.current_date_str and hoje != self.current_date_str:
                    print(f"[WATCHDOG] Virada de dia detectada ({self.current_date_str} -> {hoje}). Rotacionando arquivos...")
                    self._rotacionar_dia()
                    continue

                # 2. Verifica se o stream congelou ou travou (sem audio por mais de 6 segundos)
                agora = time.time()
                if self.last_audio_tick > 0 and (agora - self.last_audio_tick > 6.0):
                    print("[WATCHDOG] Nao foram recebidos dados de audio nos ultimos 6s. Tentando reiniciar captura...")
                    self._reiniciar_captura_silenciosa()

        self.watchdog_thread = threading.Thread(target=watchdog_loop, daemon=True, name="RecorderWatchdog")
        self.watchdog_thread.start()

    def get_output_dir(self) -> Path:
        """Retorna o diretorio base configurado para salvar gravacoes e transcricoes."""
        out = self.config.get("output_dir")
        if out:
            p = Path(out).resolve()
            try:
                p.mkdir(parents=True, exist_ok=True)
                return p
            except Exception:
                pass
        return BASE_DIR

    def set_output_dir(self, novo_dir: str | Path):
        """Atualiza e persiste o novo diretorio de destino."""
        p = Path(novo_dir).resolve()
        p.mkdir(parents=True, exist_ok=True)
        (p / "gravacoes").mkdir(parents=True, exist_ok=True)
        (p / "transcricoes").mkdir(parents=True, exist_ok=True)
        self.config["output_dir"] = str(p)
        salvar_configuracao(self.config)

    def obter_diretorios(self) -> tuple[Path, Path]:
        """Garante a criacao e retorna as pastas de gravacoes e transcricoes."""
        base = self.get_output_dir()
        gravacoes = base / "gravacoes"
        transcricoes = base / "transcricoes"
        gravacoes.mkdir(parents=True, exist_ok=True)
        transcricoes.mkdir(parents=True, exist_ok=True)
        return gravacoes, transcricoes

    def _rotacionar_dia(self):
        """Fecha o arquivo de audio e MD do dia anterior e abre os do novo dia."""
        with self._lock:
            self._fechar_arquivo_atual()
            self._abrir_novo_arquivo_dia()

    def _abrir_novo_arquivo_dia(self):
        """Cria novos arquivos de gravacao e transcricao identificados por data e hora."""
        agora = datetime.datetime.now()
        self.current_date_str = agora.strftime("%Y-%m-%d")
        timestamp = agora.strftime("%Y-%m-%d_%H-%M-%S")
        self.session_id = f"REC-{timestamp}"

        nome_audio = f"gravando_{timestamp}.wav"
        nome_md = f"transcricao_{timestamp}.md"

        gravacoes_dir, transcricoes_dir = self.obter_diretorios()
        self.current_audio_file = gravacoes_dir / nome_audio
        self.current_md_file = transcricoes_dir / nome_md

        sr = int(self.config["sample_rate"])
        ch = int(self.config["channels"])

        self.current_sf = sf.SoundFile(
            str(self.current_audio_file),
            mode="w",
            samplerate=sr,
            channels=ch,
            subtype="PCM_16",
            format="WAV"
        )
        self.session_start_time = time.time()
        self.total_frames_recorded = 0
        self.chunk_buffer = []
        self.chunk_buffer_samples = 0

        # Grava estado persistente
        self._salvar_estado(gravando=True)
        print(f"[RECORDER] Iniciada nova sessao de gravacao: {nome_audio}")

    def _fechar_arquivo_atual(self):
        """Fecha o arquivo WAV com seguranca."""
        self.chunk_buffer = []
        self.chunk_buffer_samples = 0

        if self.current_sf:
            try:
                self.current_sf.flush()
                self.current_sf.close()
            except Exception as e:
                print(f"[RECORDER] Erro ao fechar arquivo: {e}")
            self.current_sf = None

    def alternar_mute(self) -> bool:
        """Alterna o estado de mudo temporario do microfone."""
        self.is_muted = not self.is_muted
        logger = get_logger()
        if self.is_muted:
            logger.info("GRAVADOR", "MUTE", "Mudo temporario ATIVADO: audio silenciado.")
        else:
            logger.info("GRAVADOR", "MUTE", "Mudo temporario DESATIVADO: captura normal de audio retomada.")
        return self.is_muted

    def set_mute(self, muted: bool):
        """Define o estado de mudo temporario do microfone."""
        self.is_muted = bool(muted)

    def _adicionar_ao_live_buffer(self, bloco: np.ndarray):
        """Adiciona bloco de audio ao ring buffer dos ultimos 5 segundos de forma thread-safe."""
        n_bloco = len(bloco)
        if n_bloco <= 0 or self.live_buffer_len <= 0:
            return
        with self._live_lock:
            if n_bloco >= self.live_buffer_len:
                self.live_buffer[:] = bloco[-self.live_buffer_len:]
                self.live_buffer_pos = 0
            else:
                espaco = self.live_buffer_len - self.live_buffer_pos
                if n_bloco <= espaco:
                    self.live_buffer[self.live_buffer_pos:self.live_buffer_pos + n_bloco] = bloco
                    self.live_buffer_pos = (self.live_buffer_pos + n_bloco) % self.live_buffer_len
                else:
                    self.live_buffer[self.live_buffer_pos:] = bloco[:espaco]
                    resto = n_bloco - espaco
                    self.live_buffer[:resto] = bloco[espaco:]
                    self.live_buffer_pos = resto

    def obter_amostras_tempo_real(self, segundos: float = 5.0) -> np.ndarray:
        """Retorna uma copia 1D linear das amostras de audio dos ultimos N segundos (ordem cronologica)."""
        sr = int(self.config.get("sample_rate", 16000))
        qtd_desejada = min(self.live_buffer_len, int(sr * segundos))
        if qtd_desejada <= 0:
            return np.zeros(0, dtype=np.float32)
        with self._live_lock:
            linear = np.concatenate((self.live_buffer[self.live_buffer_pos:], self.live_buffer[:self.live_buffer_pos]))
        if len(linear) > qtd_desejada:
            return linear[-qtd_desejada:]
        return linear

    def _audio_callback(self, indata, frames, time_info, status):
        """Callback de alta performance chamado pelo sounddevice a cada bloco de audio."""
        if status:
            print(f"[AUDIO CALLBACK STATUS] {status}", flush=True)

        self.last_audio_tick = time.time()

        if self.is_muted:
            # Mudo temporario ativado: forca nivel a -60 dB e alimenta buffer com silencio
            self.current_level_rms = 0.0
            self.current_level_db = -60.0
            self._adicionar_ao_live_buffer(np.zeros(frames, dtype=np.float32))

            if not self.is_recording or self.is_paused:
                return

            if self.current_sf is not None:
                try:
                    bloco_silencio = np.zeros_like(indata)
                    self.current_sf.write(bloco_silencio)
                    self.total_frames_recorded += frames
                except Exception as e:
                    print(f"[RECORDER] Erro de gravacao de silencio em disco: {e}")
            return

        # Mede nivel de volume RMS e Decibeis
        audio_mono = indata[:, 0] if indata.ndim > 1 else indata
        rms = float(np.sqrt(np.mean(audio_mono**2)))
        self.current_level_rms = rms
        db = 20 * math.log10(rms + 1e-9)
        self.current_level_db = max(-60.0, min(0.0, db))

        # Alimenta buffer continuo dos ultimos 5 segundos
        self._adicionar_ao_live_buffer(audio_mono.astype(np.float32))

        if not self.is_recording or self.is_paused:
            return

        # Escreve diretamente no arquivo WAV em disco
        if self.current_sf is not None:
            try:
                self.current_sf.write(indata)
                self.total_frames_recorded += frames
            except Exception as e:
                print(f"[RECORDER] Erro de gravacao em disco: {e}")

    def iniciar_monitoramento(self, device_id: Optional[int] = None):
        """Inicia fluxo continuo de monitoramento em segundo plano para o VU meter e medidor de dB."""
        with self._lock:
            if device_id is not None:
                self.config["device_id"] = device_id
                salvar_configuracao(self.config)

            dev_id = self.config.get("device_id")
            sr = int(self.config.get("sample_rate", 16000))
            ch = int(self.config.get("channels", 1))

            # Sincroniza capacidade do buffer circular de tempo real
            with self._live_lock:
                desejado_len = int(sr * self.live_buffer_seconds)
                if self.live_buffer_len != desejado_len:
                    self.live_buffer_len = desejado_len
                    self.live_buffer = np.zeros(self.live_buffer_len, dtype=np.float32)
                    self.live_buffer_pos = 0

            try:
                # Se ja esta ativo com o mesmo dispositivo e taxa, nao precisa recriar
                if self.stream is not None:
                    try:
                        self.stream.stop()
                        self.stream.close()
                    except Exception:
                        pass
                    self.stream = None

                self.stream = sd.InputStream(
                    device=dev_id,
                    channels=ch,
                    samplerate=sr,
                    callback=self._audio_callback,
                    blocksize=2048,
                    dtype="float32"
                )
                self.stream.start()
                self.last_audio_tick = time.time()
                print(f"[RECORDER] Monitoramento de nível de áudio (VU) ativo no dispositivo ID: {dev_id}")
            except Exception as e:
                print(f"[RECORDER] Falha ao iniciar monitoramento no dispositivo {dev_id}: {e}")

    def iniciar_gravacao(self, device_id: Optional[int] = None) -> dict:
        """Inicia ou retoma a gravacao continua com o microfone selecionado."""
        with self._lock:
            if self.is_recording and not self.is_paused:
                return {"status": "already_recording", "file": str(self.current_audio_file)}

            if device_id is not None:
                self.config["device_id"] = device_id
                salvar_configuracao(self.config)

            dev_id = self.config.get("device_id")
            sr = int(self.config.get("sample_rate", 16000))
            ch = int(self.config.get("channels", 1))

            # Sincroniza capacidade do buffer circular de tempo real
            with self._live_lock:
                desejado_len = int(sr * self.live_buffer_seconds)
                if self.live_buffer_len != desejado_len:
                    self.live_buffer_len = desejado_len
                    self.live_buffer = np.zeros(self.live_buffer_len, dtype=np.float32)
                    self.live_buffer_pos = 0

            try:
                # Se nao tiver sessao aberta, abre
                if self.current_sf is None:
                    self._abrir_novo_arquivo_dia()

                # Se a stream nao estiver rodando, inicia
                if self.stream is None or not self.stream.active:
                    self.stream = sd.InputStream(
                        device=dev_id,
                        channels=ch,
                        samplerate=sr,
                        callback=self._audio_callback,
                        blocksize=2048,
                        dtype="float32"
                    )
                    self.stream.start()

                self.is_recording = True
                self.is_paused = False
                self.last_audio_tick = time.time()
                self._salvar_estado(gravando=True)

                logger = get_logger()
                logger.info("GRAVADOR", "INICIAR", f"Gravacao iniciada ({self.session_id}, Arquivo: {self.current_audio_file.name}, Dispositivo ID: {dev_id})")
                print(f"[RECORDER] Captura iniciada com sucesso no dispositivo ID: {dev_id}")
                return {
                    "status": "success",
                    "device_id": dev_id,
                    "session_id": self.session_id,
                    "audio_file": self.current_audio_file.name if self.current_audio_file else None,
                    "md_file": self.current_md_file.name if self.current_md_file else None
                }
            except Exception as e:
                err_msg = str(e)
                get_logger().error("GRAVADOR", "ERRO_INICIAR", f"Falha ao iniciar gravacao: {err_msg}")
                print(f"[RECORDER] Falha ao iniciar gravacao: {err_msg}")
                traceback.print_exc()
                self._fechar_arquivo_atual()
                self.is_recording = False
                return {"status": "error", "message": err_msg}

    def pausar_gravacao(self):
        """Pausa temporariamente a gravacao mantendo o arquivo aberto."""
        with self._lock:
            self.is_paused = True
            self._salvar_estado(gravando=False)
            get_logger().info("GRAVADOR", "PAUSAR", "Gravacao pausada pelo usuario.")

    def parar_gravacao(self) -> dict:
        """Para a gravacao e finaliza os arquivos atuais, mantendo o monitoramento de dB ativo."""
        with self._lock:
            self.is_recording = False
            self.is_paused = False

            arquivo_finalizado = self.current_audio_file
            self._fechar_arquivo_atual()
            self._salvar_estado(gravando=False)
            self.last_completed_audio_file = arquivo_finalizado

            validacao = {"valid": False}
            if arquivo_finalizado and arquivo_finalizado.exists():
                validacao = validar_arquivo_wav(arquivo_finalizado)
                if validacao["valid"]:
                    get_logger().info(
                        "GRAVADOR",
                        "CONCLUSAO",
                        f"Gravacao finalizada e arquivo WAV validado com sucesso ({validacao['duration']}s, {validacao['size_mb']} MB): {arquivo_finalizado.name}"
                    )
                else:
                    get_logger().warn(
                        "GRAVADOR",
                        "AVISO_VALIDACAO",
                        f"Arquivo WAV gerado mas com ressalva ({validacao.get('error')}): {arquivo_finalizado.name}"
                    )
            else:
                get_logger().info("GRAVADOR", "CONCLUSAO", "Gravacao finalizada sem arquivo aberto.")

            # Mantem a stream ativa para que o VU meter e a barra de dB continuem operando mesmo parada
            if self.stream is None or not self.stream.active:
                try:
                    dev_id = self.config.get("device_id")
                    sr = int(self.config.get("sample_rate", 16000))
                    ch = int(self.config.get("channels", 1))
                    self.stream = sd.InputStream(
                        device=dev_id,
                        channels=ch,
                        samplerate=sr,
                        callback=self._audio_callback,
                        blocksize=2048,
                        dtype="float32"
                    )
                    self.stream.start()
                except Exception as e:
                    print(f"[RECORDER] Falha ao reativar monitoramento: {e}")

            print("[RECORDER] Gravacao finalizada com sucesso. Monitoramento de dB ativo.")
            return {
                "status": "stopped",
                "audio_file": arquivo_finalizado,
                "validation": validacao
            }

    def encerrar(self):
        """Encerra completamente o gravador e libera o dispositivo de audio do sistema."""
        self.should_run = False
        with self._lock:
            self.is_recording = False
            if self.stream is not None:
                try:
                    self.stream.stop()
                    self.stream.close()
                except Exception:
                    pass
                self.stream = None
            self._fechar_arquivo_atual()

    def obter_ultimo_audio_finalizado(self) -> Optional[Path]:
        """Retorna o caminho do ultimo arquivo de audio gravado e validado."""
        if self.last_completed_audio_file and self.last_completed_audio_file.exists():
            return self.last_completed_audio_file
        # Se nao estiver em memoria, busca o arquivo .wav mais recente na pasta gravacoes/
        gravacoes_dir, _ = self.obter_diretorios()
        arquivos = sorted(gravacoes_dir.glob("*.wav"), key=lambda x: x.stat().st_mtime, reverse=True)
        return arquivos[0] if arquivos else None

    def _reiniciar_captura_silenciosa(self):
        """Reinicia o fluxo de captura de audio apos queda de hardware ou interrupcao."""
        print("[RECORDER] Reiniciando fluxo de audio automaticamente...")
        try:
            if self.stream:
                try:
                    self.stream.stop()
                    self.stream.close()
                except Exception:
                    pass
                self.stream = None

            dev_id = self.config.get("device_id")
            sr = int(self.config.get("sample_rate", 16000))
            ch = int(self.config.get("channels", 1))

            # Sincroniza capacidade do buffer circular de tempo real
            with self._live_lock:
                desejado_len = int(sr * self.live_buffer_seconds)
                if self.live_buffer_len != desejado_len:
                    self.live_buffer_len = desejado_len
                    self.live_buffer = np.zeros(self.live_buffer_len, dtype=np.float32)
                    self.live_buffer_pos = 0

            self.stream = sd.InputStream(
                device=dev_id,
                channels=ch,
                samplerate=sr,
                callback=self._audio_callback,
                blocksize=2048,
                dtype="float32"
            )
            self.stream.start()
            self.last_audio_tick = time.time()
            print("[RECORDER] Fluxo reiniciado e operando normalmente.")
        except Exception as e:
            print(f"[RECORDER] Falha na recuperacao automatica: {e}")

    def _salvar_estado(self, gravando: bool):
        estado = {
            "is_recording": gravando,
            "device_id": self.config.get("device_id"),
            "audio_file": self.current_audio_file.name if self.current_audio_file else None,
            "md_file": self.current_md_file.name if self.current_md_file else None,
            "last_active": datetime.datetime.now().isoformat()
        }
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(estado, f, indent=2)

    def recuperar_estado_inicial(self):
        """Verifica se o sistema deve retomar a gravacao ao reiniciar."""
        if not self.config.get("auto_record", False):
            return

        deve_gravar = False
        if STATE_FILE.exists():
            try:
                with open(STATE_FILE, "r", encoding="utf-8") as f:
                    st = json.load(f)
                    if st.get("is_recording", False):
                        deve_gravar = True
            except Exception:
                deve_gravar = False
        else:
            deve_gravar = False

        if deve_gravar:
            print("[RECORDER] Auto-recovery: Retomando gravacao automatica do sistema...")
            self.iniciar_gravacao()

    def get_status(self) -> dict:
        duracao_seg = 0
        if self.is_recording and self.session_start_time > 0:
            duracao_seg = int(time.time() - self.session_start_time)

        # Calcula tamanho do arquivo atual em MB
        file_size_mb = 0.0
        if self.is_recording and self.current_audio_file and self.current_audio_file.exists():
            try:
                file_size_mb = round(self.current_audio_file.stat().st_size / (1024 * 1024), 2)
            except Exception:
                file_size_mb = round((self.total_frames_recorded * 2) / (1024 * 1024), 2)

        # Informacoes de espaco livre na particao/disco do diretorio atual
        disk_info = obter_espaco_disco(self.get_output_dir())

        return {
            "is_recording": self.is_recording,
            "is_paused": self.is_paused,
            "is_muted": self.is_muted,
            "device_id": self.config.get("device_id"),
            "device_name": self.config.get("device_name"),
            "current_audio_file": self.current_audio_file.name if self.current_audio_file else None,
            "current_md_file": self.current_md_file.name if self.current_md_file else None,
            "duration_seconds": duracao_seg,
            "file_size_mb": file_size_mb,
            "disk_info": disk_info,
            "output_dir": str(self.get_output_dir()),
            "level_rms": round(self.current_level_rms, 4),
            "level_db": round(self.current_level_db, 1),
            "queue_size": self.transcriber.task_queue.qsize() if self.transcriber else 0
        }

