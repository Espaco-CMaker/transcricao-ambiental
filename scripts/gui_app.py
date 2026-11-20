"""Interface Grafica Nativa para Gravacao e Transcricao Ambiental de Sala (Sem Web).
Desenvolvida com CustomTkinter, SoundDevice, SoundFile, Faster-Whisper e Pygame.
Possui selecao de microfone, reprodutor de audio integrado, editor de Markdown,
VU meter em tempo real, exibicao de tamanho do arquivo e espaco na particao,
com selecao persistente de diretorio de gravacao.
"""

import os
import sys
import time
import math
import queue
import threading
import datetime
import subprocess
from pathlib import Path
from typing import Optional, Callable, Dict, Any, List

# Garante resolucao de caminhos independentemente do diretorio de execucao
BASE_DIR = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = Path(__file__).resolve().parent

if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import customtkinter as ctk
import pygame
import numpy as np
from PIL import Image, ImageDraw, ImageTk

try:
    from scripts.lixeira import mover_para_lixeira
    from scripts.transcriber import TranscriberEngine
    from scripts.recorder import (
        AudioRecorder, listar_microfones, carregar_configuracao,
        salvar_configuracao, obter_espaco_disco, validar_arquivo_wav
    )
    from scripts.logger_audit import get_logger, LOG_FILE
    from scripts.gerador_ata import gerar_ata_de_transcricao, extrair_titulo_contextual
    from scripts.renomeador import renomear_trio_arquivos, extrair_data_hora_prefixo
    from scripts.waveform_generator import extrair_amostras_waveform, gerar_sparkline_thumbnail, gerar_onda_texto
except ImportError:
    from lixeira import mover_para_lixeira
    from transcriber import TranscriberEngine
    from recorder import (
        AudioRecorder, listar_microfones, carregar_configuracao,
        salvar_configuracao, obter_espaco_disco, validar_arquivo_wav
    )
    from logger_audit import get_logger, LOG_FILE
    from gerador_ata import gerar_ata_de_transcricao, extrair_titulo_contextual
    from renomeador import renomear_trio_arquivos, extrair_data_hora_prefixo
    from waveform_generator import extrair_amostras_waveform, gerar_sparkline_thumbnail, gerar_onda_texto

# Configura tema escuro moderno
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

APP_VERSION = "v1.0.42"


def abrir_no_explorer(caminho: Path):
    """Abre o Windows Explorer no local do arquivo ou pasta, selecionando o arquivo se existir."""
    try:
        p = Path(caminho).resolve()
        if p.is_file() and p.exists():
            subprocess.run(["explorer", f"/select,{str(p)}"])
        elif p.is_dir() and p.exists():
            os.startfile(str(p))
        elif p.parent.exists():
            os.startfile(str(p.parent))
    except Exception as e:
        print(f"[EXPLORER] Falha ao abrir Explorer: {e}")
        try:
            target = p.parent if p.is_file() else p
            os.startfile(str(target))
        except Exception:
            pass


class DesktopApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title(f"Gravador e Transcritor Ambiental de Sala: 24/7 - {APP_VERSION}")
        self.geometry("1200x800")
        self.minsize(1020, 700)

        # Inicializa subsistemas
        self.transcriber = TranscriberEngine(model_size="base", device="auto", language="pt")
        self.recorder = AudioRecorder(transcriber=self.transcriber)

        # Inicializa audio mixer do Pygame para reproducao local
        try:
            pygame.mixer.init()
        except Exception as e:
            print(f"[AUDIO MIXER] Falha ao iniciar pygame.mixer: {e}")

        # Variaveis de estado do player
        self.playing_file: Path | None = None
        self.is_playing = False
        self.is_paused = False
        self.player_duration_sec = 0.0
        self.player_start_sec = 0.0

        # Variaveis de microfones e arquivos selecionados
        self.devices_list = []
        self.current_selected_md: Path | None = None
        self._current_transcription_id = 0
        self._sparkline_photos = []
        self._current_waveform_data = None
        self._last_rendered_wf_path = None
        self._last_rendered_wf_width = 0
        self.live_gain_factor = 3.0

        # Inicializa AppUserModelID e icones dinamicos para a barra de tarefas
        self._inicializar_icones_barra_tarefas()

        # Monta interface
        self._construir_interface()

        # Carrega dados iniciais
        self._carregar_dispositivos()
        self.recorder.iniciar_monitoramento()
        self._atualizar_lista_audios()
        self._atualizar_lista_transcricoes()

        # Intercepta fechamento da janela
        self.protocol("WM_DELETE_WINDOW", self._ao_fechar)

        # Inicia loop periodico de atualizacao da interface (50ms)
        self.after(50, self._loop_interface)

        # Auto-recuperacao: retoma gravacao se configurado
        self.after(600, self._verificar_auto_recuperacao)

    def _inicializar_icones_barra_tarefas(self):
        """Inicializa identificador de processo no Windows e gera pares de icones (32x32 e 16x16)
        para alternancia dinamica (piscar em vermelho) na barra de tarefas durante a gravacao.
        """
        try:
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("CMaker.TranscricaoAmbiental.App.1")
        except Exception:
            pass

        self._ultimo_estado_pisca = None
        self._titulo_base = f"Gravador e Transcritor Ambiental de Sala: 24/7 - {APP_VERSION}"

        # Gera os icones em memoria com PIL para 32x32 (taskbar/Alt-Tab) e 16x16 (titulo)
        from PIL import Image, ImageDraw, ImageTk

        def _desenhar_icones(sz: int):
            # 1. Padrao (azul/ardosia)
            img_norm = Image.new("RGBA", (sz, sz), (0, 0, 0, 0))
            d = ImageDraw.Draw(img_norm)
            margin = 1 if sz == 16 else 2
            d.ellipse([margin, margin, sz - 1 - margin, sz - 1 - margin], fill=(15, 23, 42, 255), outline=(56, 189, 248, 255), width=1 if sz == 16 else 2)
            if sz == 32:
                d.rounded_rectangle([13, 8, 19, 17], radius=3, fill=(56, 189, 248, 255))
                d.arc([10, 13, 22, 20], start=0, end=180, fill=(56, 189, 248, 255), width=2)
                d.line([(16, 20), (16, 24)], fill=(56, 189, 248, 255), width=2)
                d.line([(12, 24), (20, 24)], fill=(56, 189, 248, 255), width=2)
            else:
                d.ellipse([5, 5, 10, 10], fill=(56, 189, 248, 255))

            # 2. Gravando Aceso (Vermelho Vivo)
            img_on = Image.new("RGBA", (sz, sz), (0, 0, 0, 0))
            d = ImageDraw.Draw(img_on)
            if sz == 32:
                d.ellipse([0, 0, 31, 31], fill=(239, 68, 68, 130))
                d.ellipse([2, 2, 29, 29], fill=(220, 38, 38, 255), outline=(254, 202, 202, 255), width=2)
                d.ellipse([9, 9, 22, 22], fill=(255, 255, 255, 255))
            else:
                d.ellipse([0, 0, 15, 15], fill=(220, 38, 38, 255), outline=(254, 202, 202, 255), width=1)
                d.ellipse([4, 4, 11, 11], fill=(255, 255, 255, 255))

            # 3. Gravando Apagado (Vinho Escuro)
            img_off = Image.new("RGBA", (sz, sz), (0, 0, 0, 0))
            d = ImageDraw.Draw(img_off)
            if sz == 32:
                d.ellipse([2, 2, 29, 29], fill=(25, 10, 15, 255), outline=(127, 29, 29, 255), width=1)
                d.ellipse([11, 11, 20, 20], fill=(127, 29, 29, 255))
            else:
                d.ellipse([1, 1, 14, 14], fill=(25, 10, 15, 255), outline=(127, 29, 29, 255), width=1)
                d.ellipse([5, 5, 10, 10], fill=(127, 29, 29, 255))

            # 4. Mutado (Ambar)
            img_mute = Image.new("RGBA", (sz, sz), (0, 0, 0, 0))
            d = ImageDraw.Draw(img_mute)
            if sz == 32:
                d.ellipse([2, 2, 29, 29], fill=(217, 119, 6, 255), outline=(254, 243, 199, 255), width=2)
                d.line([(8, 8), (23, 23)], fill=(255, 255, 255, 255), width=3)
            else:
                d.ellipse([1, 1, 14, 14], fill=(217, 119, 6, 255), outline=(254, 243, 199, 255), width=1)
                d.line([(4, 4), (11, 11)], fill=(255, 255, 255, 255), width=2)

            return (
                ImageTk.PhotoImage(img_norm),
                ImageTk.PhotoImage(img_on),
                ImageTk.PhotoImage(img_off),
                ImageTk.PhotoImage(img_mute)
            )

        norm32, on32, off32, mute32 = _desenhar_icones(32)
        norm16, on16, off16, mute16 = _desenhar_icones(16)

        self._ico_pair_padrao = (norm32, norm16)
        self._ico_pair_rec_on = (on32, on16)
        self._ico_pair_rec_off = (off32, off16)
        self._ico_pair_mute = (mute32, mute16)

        try:
            self.iconphoto(False, *self._ico_pair_padrao)
        except Exception:
            pass

    def _atualizar_icone_barra_tarefas(self, gravando: bool, fase_acesa: bool = True, mutado: bool = False):
        """Atualiza dinamicamente o icone da janela e da barra de tarefas do Windows.
        Quando gravando, alterna entre o icone vermelho vivo e o apagado, criando o efeito de piscar em vermelho.
        """
        try:
            if not gravando:
                self.iconphoto(False, *self._ico_pair_padrao)
                if self.title() != self._titulo_base:
                    self.title(self._titulo_base)
            elif mutado:
                ico = self._ico_pair_mute if fase_acesa else self._ico_pair_rec_off
                self.iconphoto(False, *ico)
                txt_titulo = f"🔇 [MUTADO] {self._titulo_base}"
                if self.title() != txt_titulo:
                    self.title(txt_titulo)
            else:
                ico = self._ico_pair_rec_on if fase_acesa else self._ico_pair_rec_off
                self.iconphoto(False, *ico)
                prefixo = "🔴 [GRAVANDO]" if fase_acesa else "⚪ [GRAVANDO]"
                txt_titulo = f"{prefixo} {self._titulo_base}"
                if self.title() != txt_titulo:
                    self.title(txt_titulo)
        except Exception:
            pass

    def _construir_interface(self):
        # 1. Frame do Topo: Titulo, Indicadores de Status, Timer, Tamanho do Arquivo e Espaco na Particao
        self.top_frame = ctk.CTkFrame(self, corner_radius=10)
        self.top_frame.pack(fill="x", padx=14, pady=(10, 4))

        self.lbl_title = ctk.CTkLabel(
            self.top_frame,
            text="🎙️ Transcrição Ambiental de Sala",
            font=ctk.CTkFont(size=17, weight="bold")
        )
        self.lbl_title.pack(side="left", padx=(14, 8), pady=10)

        self.lbl_version_badge = ctk.CTkLabel(
            self.top_frame,
            text=f" {APP_VERSION} ",
            fg_color="#334155",
            text_color="#38bdf8",
            corner_radius=6,
            font=ctk.CTkFont(family="Consolas", size=12, weight="bold")
        )
        self.lbl_version_badge.pack(side="left", padx=(0, 10), pady=10)

        # Indicadores a Direita
        self.badge_status = ctk.CTkButton(
            self.top_frame,
            text="● PRONTO",
            fg_color="#064e3b",
            hover_color="#064e3b",
            text_color="#34d399",
            font=ctk.CTkFont(size=13, weight="bold"),
            width=105,
            height=30
        )
        self.badge_status.pack(side="right", padx=(6, 14), pady=10)

        self.lbl_timer = ctk.CTkLabel(
            self.top_frame,
            text="⏱️ 00:00:00",
            font=ctk.CTkFont(family="Consolas", size=15, weight="bold"),
            text_color="#38bdf8"
        )
        self.lbl_timer.pack(side="right", padx=10, pady=10)

        self.lbl_file_size = ctk.CTkLabel(
            self.top_frame,
            text="📦 Arquivo: 0.0 MB",
            font=ctk.CTkFont(family="Consolas", size=13, weight="bold"),
            text_color="#a5f3fc"
        )
        self.lbl_file_size.pack(side="right", padx=10, pady=10)

        self.lbl_disk_space = ctk.CTkLabel(
            self.top_frame,
            text="💾 Partição: --",
            font=ctk.CTkFont(family="Consolas", size=13, weight="bold"),
            text_color="#38bdf8"
        )
        self.lbl_disk_space.pack(side="right", padx=10, pady=10)

        # 2. Frame de Controles e Configuracoes
        self.control_frame = ctk.CTkFrame(self, corner_radius=10)
        self.control_frame.pack(fill="x", padx=14, pady=4)

        # Linha 1 de controles: Microfone e Botoes de Gravacao
        row1 = ctk.CTkFrame(self.control_frame, fg_color="transparent")
        row1.pack(fill="x", padx=14, pady=(8, 4))

        lbl_mic = ctk.CTkLabel(row1, text="Microfone de Origem:", font=ctk.CTkFont(size=13, weight="bold"))
        lbl_mic.pack(side="left", padx=(0, 6))

        self.combo_mic = ctk.CTkComboBox(row1, width=440, command=self._ao_mudar_microfone)
        self.combo_mic.pack(side="left", padx=(0, 6))

        self.btn_refresh_mics = ctk.CTkButton(row1, text="🔄", width=34, command=self._carregar_dispositivos)
        self.btn_refresh_mics.pack(side="left", padx=(0, 14))

        self.btn_iniciar = ctk.CTkButton(
            row1,
            text="⏺ Iniciar Gravação",
            fg_color="#dc2626",
            hover_color="#b91c1c",
            font=ctk.CTkFont(size=13, weight="bold"),
            height=34,
            width=150,
            command=self._iniciar_gravacao
        )
        self.btn_iniciar.pack(side="left", padx=4)

        self.btn_parar = ctk.CTkButton(
            row1,
            text="⏹ Parar Gravação",
            fg_color="#475569",
            hover_color="#334155",
            font=ctk.CTkFont(size=13, weight="bold"),
            height=34,
            width=140,
            state="disabled",
            command=self._parar_gravacao
        )
        self.btn_parar.pack(side="left", padx=4)

        self.btn_mute = ctk.CTkButton(
            row1,
            text="🎙️ Mudo Temporário",
            fg_color="#334155",
            hover_color="#475569",
            font=ctk.CTkFont(size=13, weight="bold"),
            height=34,
            width=165,
            command=self._alternar_mute
        )
        self.btn_mute.pack(side="left", padx=6)

        # Linha 2 de controles: VU Meter, Modelo Whisper e Auto-recuperacao
        row2 = ctk.CTkFrame(self.control_frame, fg_color="transparent")
        row2.pack(fill="x", padx=14, pady=3)

        lbl_vu = ctk.CTkLabel(row2, text="Nível (VU):", font=ctk.CTkFont(size=12))
        lbl_vu.pack(side="left", padx=(0, 6))

        self.progress_vu = ctk.CTkProgressBar(row2, width=240, height=14)
        self.progress_vu.set(0.0)
        self.progress_vu.pack(side="left", padx=(0, 6))

        self.lbl_vu_db = ctk.CTkLabel(row2, text="-60.0 dB", font=ctk.CTkFont(family="Consolas", size=12), text_color="#94a3b8")
        self.lbl_vu_db.pack(side="left", padx=(0, 10))

        self.lbl_mute_badge = ctk.CTkLabel(
            row2,
            text="",
            font=ctk.CTkFont(family="Consolas", size=12, weight="bold"),
            text_color="#ef4444"
        )
        self.lbl_mute_badge.pack(side="left", padx=(0, 10))

        lbl_modelo = ctk.CTkLabel(row2, text="Whisper:", font=ctk.CTkFont(size=12))
        lbl_modelo.pack(side="left", padx=(0, 6))

        self.combo_modelo = ctk.CTkOptionMenu(
            row2,
            values=["tiny", "base", "small", "medium"],
            width=90,
            command=self._ao_mudar_modelo
        )
        self.combo_modelo.set(self.recorder.config.get("model_size", "base"))
        self.combo_modelo.pack(side="left", padx=(0, 14))

        self.chk_auto = ctk.CTkCheckBox(
            row2,
            text="Auto-iniciar gravação ao abrir",
            font=ctk.CTkFont(size=12),
            command=self._ao_mudar_auto_record
        )
        if self.recorder.config.get("auto_record", False):
            self.chk_auto.select()
        else:
            self.chk_auto.deselect()
        self.chk_auto.pack(side="left", padx=4)

        # Linha de Grafico de Som em Tempo Real (ultimos 5 segundos passando na tela)
        self.frame_live_wave = ctk.CTkFrame(self.control_frame, fg_color="#090d16", corner_radius=8)
        self.frame_live_wave.pack(fill="x", padx=14, pady=(2, 4))

        live_header = ctk.CTkFrame(self.frame_live_wave, fg_color="transparent")
        live_header.pack(fill="x", padx=10, pady=(4, 2))

        lbl_live_title = ctk.CTkLabel(
            live_header,
            text="🌊 Gráfico de Som em Tempo Real (Últimos 5 segundos):",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#38bdf8"
        )
        lbl_live_title.pack(side="left")

        # Controle de Amplitude / Ganho Visual
        lbl_gain = ctk.CTkLabel(
            live_header,
            text="Amplitude:",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#94a3b8"
        )
        lbl_gain.pack(side="left", padx=(16, 4))

        self.seg_gain = ctk.CTkSegmentedButton(
            live_header,
            values=["1x", "2x", "3x", "5x"],
            font=ctk.CTkFont(size=10, weight="bold"),
            width=135,
            height=22,
            command=self._ao_mudar_ganho_live
        )
        self.seg_gain.set("3x")
        self.seg_gain.pack(side="left", padx=(0, 10))

        self.lbl_live_stats = ctk.CTkLabel(
            live_header,
            text="Taxa: 16kHz | Janela: 5.0s",
            font=ctk.CTkFont(family="Consolas", size=10),
            text_color="#64748b"
        )
        self.lbl_live_stats.pack(side="right")

        self.canvas_live_wave = tk.Canvas(
            self.frame_live_wave,
            height=76,
            bg="#090d16",
            highlightthickness=0
        )
        self.canvas_live_wave.pack(fill="x", padx=8, pady=(0, 6))
        self.canvas_live_wave.bind("<Configure>", self._ao_redimensionar_canvas_live)

        # Linha 3 de controles: Diretorio de Destino Persistente e Detalhe da Particao
        row3 = ctk.CTkFrame(self.control_frame, fg_color="transparent")
        row3.pack(fill="x", padx=14, pady=(2, 6))

        lbl_dir = ctk.CTkLabel(row3, text="📁 Pasta de Destino:", font=ctk.CTkFont(size=12, weight="bold"))
        lbl_dir.pack(side="left", padx=(0, 6))

        self.entry_dir = ctk.CTkEntry(row3, width=440, font=ctk.CTkFont(size=11))
        self.entry_dir.insert(0, str(self.recorder.get_output_dir()))
        self.entry_dir.configure(state="readonly")
        self.entry_dir.pack(side="left", padx=(0, 6))

        self.btn_change_dir = ctk.CTkButton(
            row3,
            text="Alterar Pasta...",
            width=120,
            height=28,
            fg_color="#0284c7",
            hover_color="#0369a1",
            font=ctk.CTkFont(size=12),
            command=self._alterar_diretorio_destino
        )
        self.btn_change_dir.pack(side="left", padx=4)

        self.btn_open_dir = ctk.CTkButton(
            row3,
            text="Abrir Pasta",
            width=95,
            height=28,
            fg_color="#334155",
            hover_color="#475569",
            font=ctk.CTkFont(size=12),
            command=self._abrir_pasta_no_explorer
        )
        self.btn_open_dir.pack(side="left", padx=4)

        self.lbl_disk_detail = ctk.CTkLabel(
            row3,
            text="Verificando partição...",
            font=ctk.CTkFont(size=11),
            text_color="#94a3b8"
        )
        self.lbl_disk_detail.pack(side="left", padx=(10, 0))

        # 3. Abas Centrais
        self.tabview = ctk.CTkTabview(self, corner_radius=10)
        self.tabview.pack(fill="both", expand=True, padx=14, pady=4)

        self.tab_audios = self.tabview.add("🎵 Gravações de Áudio (.wav)")
        self.tab_transcricoes = self.tabview.add("📝 Transcrições do Dia (.md)")
        self.tab_config = self.tabview.add("⚙️ Configurações & Auditoria")

        self._construir_aba_audios()
        self._construir_aba_transcricoes()
        self._construir_aba_configuracoes()

        # 4. Barra Inferior: Reprodutor de Audio Local Integrado
        self.player_frame = ctk.CTkFrame(self, height=52, corner_radius=10, fg_color="#1e293b")
        self.player_frame.pack(fill="x", padx=14, pady=(4, 10))

        self.lbl_player_info = ctk.CTkLabel(
            self.player_frame,
            text="🎧 Nenhum áudio em reprodução",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#e2e8f0"
        )
        self.lbl_player_info.pack(side="left", padx=16, pady=8)

        self.btn_play_pause = ctk.CTkButton(
            self.player_frame,
            text="▶ Ouvir",
            width=80,
            height=28,
            command=self._alternar_reproducao
        )
        self.btn_play_pause.pack(side="left", padx=6, pady=8)

        self.btn_stop_audio = ctk.CTkButton(
            self.player_frame,
            text="⏹ Parar",
            width=70,
            height=28,
            fg_color="#475569",
            command=self._parar_reproducao
        )
        self.btn_stop_audio.pack(side="left", padx=6, pady=8)

        self.slider_pos = ctk.CTkSlider(self.player_frame, from_=0, to=100, width=320, command=self._ao_arrastar_slider)
        self.slider_pos.set(0)
        self.slider_pos.pack(side="left", padx=12, pady=8)

        self.lbl_player_tempo = ctk.CTkLabel(
            self.player_frame,
            text="00:00:00 / 00:00:00",
            font=ctk.CTkFont(family="Consolas", size=12),
            text_color="#94a3b8"
        )
        self.lbl_player_tempo.pack(side="left", padx=8, pady=8)

        self.lbl_footer_version = ctk.CTkLabel(
            self.player_frame,
            text=f"Versão {APP_VERSION}",
            font=ctk.CTkFont(family="Consolas", size=11),
            text_color="#64748b"
        )
        self.lbl_footer_version.pack(side="right", padx=16, pady=8)

    # --- Aba 1: Gravacoes de Audio ---
    def _construir_aba_audios(self):
        toolbar = ctk.CTkFrame(self.tab_audios, fg_color="transparent")
        toolbar.pack(fill="x", padx=4, pady=4)

        btn_atualizar = ctk.CTkButton(toolbar, text="🔄 Atualizar", width=95, command=self._atualizar_lista_audios)
        btn_atualizar.pack(side="left", padx=3)

        self.btn_transcrever_sel = ctk.CTkButton(
            toolbar,
            text="⚡ Transcrever",
            fg_color="#3b82f6",
            hover_color="#2563eb",
            width=120,
            command=self._transcrever_audio_selecionado
        )
        self.btn_transcrever_sel.pack(side="left", padx=4)

        self.btn_excluir_audio = ctk.CTkButton(
            toolbar,
            text="🗑️ Excluir Áudio",
            fg_color="#991b1b",
            hover_color="#7f1d1d",
            width=105,
            command=self._excluir_audio_selecionado
        )
        self.btn_excluir_audio.pack(side="left", padx=4)

        self.btn_abrir_local_audio = ctk.CTkButton(
            toolbar,
            text="📂 Abrir Local",
            fg_color="#334155",
            hover_color="#475569",
            width=95,
            command=self._abrir_local_audio
        )
        self.btn_abrir_local_audio.pack(side="left", padx=4)

        # Botão para Cancelar Transcrição / Lote (visível apenas durante o processamento)
        self.btn_cancelar_transcricao = ctk.CTkButton(
            toolbar,
            text="✖ Cancelar Transcrição",
            width=150,
            fg_color="#b91c1c",
            hover_color="#991b1b",
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self._cancelar_transcricao
        )

        # Indicador de Porcentagem de Transcricao em tempo real
        self.progress_transcribe = ctk.CTkProgressBar(toolbar, width=170, height=14)
        self.progress_transcribe.set(0.0)

        self.lbl_transcribe_pct = ctk.CTkLabel(
            toolbar,
            text="",
            font=ctk.CTkFont(family="Consolas", size=12, weight="bold"),
            text_color="#38bdf8"
        )

        self.lbl_transcribe_status = ctk.CTkLabel(
            toolbar,
            text="",
            font=ctk.CTkFont(size=11),
            text_color="#94a3b8"
        )

        # Tabela Treeview
        tree_frame = ctk.CTkFrame(self.tab_audios)
        tree_frame.pack(fill="both", expand=True, padx=4, pady=(4, 2))

        # Estilo para espacamento adequado da miniatura da forma de onda
        style = ttk.Style()
        style.configure("Treeview", rowheight=26)

        colunas = ("nome", "onda", "duracao", "tamanho", "modificado")
        self.tree_audios = ttk.Treeview(tree_frame, columns=colunas, show="headings", selectmode="extended")
        self.tree_audios.heading("nome", text="Arquivo de Áudio (.wav)")
        self.tree_audios.heading("onda", text="Draft de Onda")
        self.tree_audios.heading("duracao", text="Duração")
        self.tree_audios.heading("tamanho", text="Tamanho (MB)")
        self.tree_audios.heading("modificado", text="Data e Hora")

        self.tree_audios.column("nome", width=340)
        self.tree_audios.column("onda", width=160, anchor="center")
        self.tree_audios.column("duracao", width=100, anchor="center")
        self.tree_audios.column("tamanho", width=110, anchor="center")
        self.tree_audios.column("modificado", width=160, anchor="center")

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree_audios.yview)
        self.tree_audios.configure(yscrollcommand=scrollbar.set)

        self.tree_audios.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.tree_audios.tag_configure(
            "separador_dia",
            background="#1e293b",
            foreground="#38bdf8",
            font=("Segoe UI", 9, "bold")
        )

        self.tree_audios.bind("<Double-1>", lambda e: self._tocar_audio_selecionado())
        self.tree_audios.bind("<<TreeviewSelect>>", self._ao_selecionar_audio)
        self.tree_audios.bind("<Control-a>", self._selecionar_todos_audios)
        self.tree_audios.bind("<Control-A>", self._selecionar_todos_audios)

        # Painel Inferior: Grafico Detalhado do Som Capturado (Draft Waveform)
        self.waveform_frame = ctk.CTkFrame(self.tab_audios, corner_radius=8, fg_color="#0f172a")
        self.waveform_frame.pack(fill="x", padx=4, pady=(2, 6))

        # Cabecalho do grafico com titulo e badges de telemetria sonora
        wf_header = ctk.CTkFrame(self.waveform_frame, fg_color="transparent")
        wf_header.pack(fill="x", padx=10, pady=(6, 4))

        self.lbl_wf_titulo = ctk.CTkLabel(
            wf_header,
            text="📊 Draft do Som Capturado: Selecione um áudio na lista",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#e2e8f0"
        )
        self.lbl_wf_titulo.pack(side="left")

        self.lbl_wf_atividade = ctk.CTkLabel(
            wf_header,
            text="🎙️ Atividade: --",
            font=ctk.CTkFont(family="Consolas", size=11, weight="bold"),
            text_color="#38bdf8"
        )
        self.lbl_wf_atividade.pack(side="right", padx=6)

        self.lbl_wf_rms = ctk.CTkLabel(
            wf_header,
            text="🔊 Nível Médio: --",
            font=ctk.CTkFont(family="Consolas", size=11),
            text_color="#94a3b8"
        )
        self.lbl_wf_rms.pack(side="right", padx=6)

        self.lbl_wf_pico = ctk.CTkLabel(
            wf_header,
            text="⚡ Pico Máx: --",
            font=ctk.CTkFont(family="Consolas", size=11),
            text_color="#94a3b8"
        )
        self.lbl_wf_pico.pack(side="right", padx=6)

        self.lbl_wf_duracao = ctk.CTkLabel(
            wf_header,
            text="⏱️ Duração: --",
            font=ctk.CTkFont(family="Consolas", size=11),
            text_color="#94a3b8"
        )
        self.lbl_wf_duracao.pack(side="right", padx=6)

        # Canvas interativo para desenho da forma de onda
        self.canvas_waveform = tk.Canvas(
            self.waveform_frame,
            height=85,
            bg="#020617",
            highlightthickness=1,
            highlightbackground="#1e293b"
        )
        self.canvas_waveform.pack(fill="x", padx=10, pady=(0, 6))
        self.canvas_waveform.bind("<Button-1>", self._ao_clicar_waveform)
        self.canvas_waveform.bind("<Configure>", self._ao_redimensionar_waveform)

    # --- Aba 2: Transcricoes Markdown ---
    def _construir_aba_transcricoes(self):
        split = ctk.CTkFrame(self.tab_transcricoes, fg_color="transparent")
        split.pack(fill="both", expand=True, padx=4, pady=4)

        # Painel Esquerdo
        left_panel = ctk.CTkFrame(split, width=440)
        left_panel.pack(side="left", fill="y", padx=(0, 6), pady=4)

        lbl_md_list = ctk.CTkLabel(left_panel, text="Arquivos Markdown por Dia:", font=ctk.CTkFont(size=13, weight="bold"))
        lbl_md_list.pack(anchor="w", padx=10, pady=(8, 4))

        colunas = ("arquivo", "falas", "modificado")
        self.tree_md = ttk.Treeview(left_panel, columns=colunas, show="headings", selectmode="extended")
        self.tree_md.heading("arquivo", text="Arquivo (.md)")
        self.tree_md.heading("falas", text="Falas")
        self.tree_md.heading("modificado", text="Data/Hora")

        self.tree_md.column("arquivo", width=220)
        self.tree_md.column("falas", width=60, anchor="center")
        self.tree_md.column("modificado", width=120, anchor="center")

        self.tree_md.pack(fill="both", expand=True, padx=6, pady=4)

        self.tree_md.tag_configure(
            "separador_dia",
            background="#1e293b",
            foreground="#38bdf8",
            font=("Segoe UI", 9, "bold")
        )

        self.tree_md.bind("<<TreeviewSelect>>", self._ao_selecionar_md)
        self.tree_md.bind("<Control-a>", self._selecionar_todos_md)
        self.tree_md.bind("<Control-A>", self._selecionar_todos_md)

        md_actions = ctk.CTkFrame(left_panel, fg_color="transparent")
        md_actions.pack(fill="x", padx=6, pady=6)

        btn_refresh_md = ctk.CTkButton(md_actions, text="🔄 Atualizar", width=85, command=self._atualizar_lista_transcricoes)
        btn_refresh_md.pack(side="left", padx=2)

        btn_local_md = ctk.CTkButton(
            md_actions,
            text="📂 Abrir Local",
            fg_color="#334155",
            hover_color="#475569",
            width=90,
            command=self._abrir_local_md
        )
        btn_local_md.pack(side="left", padx=2)

        btn_del_md = ctk.CTkButton(
            md_actions,
            text="🗑️ Excluir",
            fg_color="#991b1b",
            hover_color="#7f1d1d",
            width=75,
            command=self._excluir_md_selecionado
        )
        btn_del_md.pack(side="left", padx=2)

        # Painel Direito: Editor
        right_panel = ctk.CTkFrame(split)
        right_panel.pack(side="right", fill="both", expand=True, padx=(6, 0), pady=4)

        editor_header = ctk.CTkFrame(right_panel, fg_color="transparent")
        editor_header.pack(fill="x", padx=10, pady=(8, 4))

        self.lbl_editing_file = ctk.CTkLabel(
            editor_header,
            text="Nenhum arquivo selecionado para edição",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#38bdf8"
        )
        self.lbl_editing_file.pack(side="left")

        self.btn_salvar_md = ctk.CTkButton(
            editor_header,
            text="💾 Salvar Alterações",
            fg_color="#10b981",
            hover_color="#059669",
            state="disabled",
            command=self._salvar_md_atual
        )
        self.btn_salvar_md.pack(side="right", padx=4)

        self.btn_abrir_externo = ctk.CTkButton(
            editor_header,
            text="📁 Abrir Externo",
            fg_color="#334155",
            hover_color="#475569",
            width=110,
            command=self._abrir_md_externo
        )
        self.btn_abrir_externo.pack(side="right", padx=4)

        self.btn_abrir_local_md_header = ctk.CTkButton(
            editor_header,
            text="📂 Abrir Local do Arquivo",
            fg_color="#334155",
            hover_color="#475569",
            width=165,
            command=self._abrir_local_md
        )
        self.btn_abrir_local_md_header.pack(side="right", padx=4)

        self.txt_md_editor = ctk.CTkTextbox(right_panel, font=ctk.CTkFont(family="Consolas", size=13), wrap="word")
        self.txt_md_editor.pack(fill="both", expand=True, padx=8, pady=8)

    # --- Aba 3: Configuracoes e Auditoria ---
    def _construir_aba_configuracoes(self):
        # 1. Painel de Preferencias de Automacao
        pref_frame = ctk.CTkFrame(self.tab_config, corner_radius=10)
        pref_frame.pack(fill="x", padx=12, pady=8)

        lbl_pref_title = ctk.CTkLabel(
            pref_frame,
            text="⚙️ Fluxos Automáticos do Gravador",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        lbl_pref_title.pack(anchor="w", padx=14, pady=(10, 6))

        # Checkboxes
        self.chk_auto_transcribe = ctk.CTkCheckBox(
            pref_frame,
            text="Transcrever automaticamente ao parar a gravação",
            font=ctk.CTkFont(size=12),
            command=self._ao_mudar_auto_transcribe
        )
        if self.recorder.config.get("auto_transcribe_on_stop", False):
            self.chk_auto_transcribe.select()
        self.chk_auto_transcribe.pack(anchor="w", padx=16, pady=4)

        self.chk_auto_rename = ctk.CTkCheckBox(
            pref_frame,
            text="Renomear transcrições com título contextual (apenas arquivos .md, nunca .wav)",
            font=ctk.CTkFont(size=12),
            command=self._ao_mudar_auto_rename
        )
        if self.recorder.config.get("auto_rename_contextual", True):
            self.chk_auto_rename.select()
        self.chk_auto_rename.pack(anchor="w", padx=16, pady=(4, 10))

        # Status do fluxo
        status_box = ctk.CTkFrame(pref_frame, fg_color="#1e293b", corner_radius=6)
        status_box.pack(fill="x", padx=14, pady=(0, 10))

        self.lbl_auto_status = ctk.CTkLabel(
            status_box,
            text="● Estado da Automação: Ocioso (Aguardando eventos)",
            font=ctk.CTkFont(size=12),
            text_color="#38bdf8"
        )
        self.lbl_auto_status.pack(side="left", padx=12, pady=6)

        # 2. Painel de Auditoria e Logs
        log_frame = ctk.CTkFrame(self.tab_config, corner_radius=10)
        log_frame.pack(fill="both", expand=True, padx=12, pady=(0, 8))

        log_toolbar = ctk.CTkFrame(log_frame, fg_color="transparent")
        log_toolbar.pack(fill="x", padx=12, pady=8)

        lbl_log_title = ctk.CTkLabel(
            log_toolbar,
            text="📋 Painel de Auditoria e Logs do Sistema (logs/sistema.log)",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        lbl_log_title.pack(side="left", padx=(0, 16))

        lbl_filtro = ctk.CTkLabel(log_toolbar, text="Filtro:", font=ctk.CTkFont(size=12))
        lbl_filtro.pack(side="left", padx=(0, 4))

        self.combo_log_filter = ctk.CTkComboBox(
            log_toolbar,
            values=["TODOS", "INFO", "WARN", "ERROR"],
            width=100,
            command=lambda v: self._atualizar_painel_logs()
        )
        self.combo_log_filter.set("TODOS")
        self.combo_log_filter.pack(side="left", padx=(0, 10))

        btn_refresh_log = ctk.CTkButton(
            log_toolbar,
            text="🔄 Atualizar",
            width=90,
            command=self._atualizar_painel_logs
        )
        btn_refresh_log.pack(side="left", padx=4)

        btn_export_log = ctk.CTkButton(
            log_toolbar,
            text="📥 Exportar Logs...",
            width=130,
            fg_color="#0284c7",
            hover_color="#0369a1",
            command=self._exportar_logs
        )
        btn_export_log.pack(side="left", padx=4)

        btn_clear_log = ctk.CTkButton(
            log_toolbar,
            text="🗑️ Limpar Tela",
            width=100,
            fg_color="#334155",
            hover_color="#475569",
            command=self._limpar_tela_logs
        )
        btn_clear_log.pack(side="left", padx=4)

        self.txt_logs = ctk.CTkTextbox(
            log_frame,
            font=ctk.CTkFont(family="Consolas", size=11),
            fg_color="#0f172a",
            text_color="#e2e8f0"
        )
        self.txt_logs.pack(fill="both", expand=True, padx=12, pady=(0, 10))

    # --- Gestao de Diretorio Persistente ---
    def _alterar_diretorio_destino(self):
        dir_atual = str(self.recorder.get_output_dir())
        novo = filedialog.askdirectory(
            parent=self,
            initialdir=dir_atual,
            title="Selecionar Pasta para Gravações e Transcrições"
        )
        if novo:
            if self.recorder.is_recording:
                resp = messagebox.askyesno(
                    "Gravação em Andamento",
                    "A gravação está ativa no momento. Deseja aplicar o novo diretório para as próximas gravações?\n\nA gravação atual continuará no arquivo atual até ser finalizada."
                )
                if not resp:
                    return

            self.recorder.set_output_dir(novo)
            self.entry_dir.configure(state="normal")
            self.entry_dir.delete(0, "end")
            self.entry_dir.insert(0, str(novo))
            self.entry_dir.configure(state="readonly")

            self._atualizar_lista_audios()
            self._atualizar_lista_transcricoes()

            # Atualiza status de disco imediatamente
            disk = obter_espaco_disco(novo)
            self.lbl_disk_space.configure(text=f"💾 {disk['drive']} {disk['free_gb']} GB livres")
            self.lbl_disk_detail.configure(
                text=f"Partição {disk['drive']}: {disk['free_gb']} GB livres de {disk['total_gb']} GB ({disk['percent_free']}%)"
            )

            messagebox.showinfo(
                "Pasta Atualizada e Salva",
                f"O novo diretório foi configurado e persistido com sucesso:\n\n{novo}\n\nSubpastas 'gravacoes/' e 'transcricoes/' foram preparadas."
            )

    def _abrir_pasta_no_explorer(self):
        p = self.recorder.get_output_dir()
        try:
            os.startfile(str(p))
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível abrir a pasta:\n{e}")

    # --- Logica de Dispositivos e Controles ---
    def _carregar_dispositivos(self):
        self.devices_list = listar_microfones()
        nomes = []
        sel_idx = 0
        cfg_dev_id = self.recorder.config.get("device_id")

        for idx, dev in enumerate(self.devices_list):
            padrao = " - Padrão" if dev.get("is_default") else ""
            api = f" ({dev['api']})" if dev.get('api') else ""
            rotulo = f"[{dev['id']}] {dev['name']}{api}{padrao}"
            nomes.append(rotulo)
            if dev["id"] == cfg_dev_id or (cfg_dev_id is None and dev.get("is_default")):
                sel_idx = idx

        if nomes:
            self.combo_mic.configure(values=nomes)
            self.combo_mic.set(nomes[sel_idx])
        else:
            self.combo_mic.configure(values=["Nenhum microfone encontrado"])
            self.combo_mic.set("Nenhum microfone encontrado")

    def _ao_mudar_microfone(self, escolha):
        if not self.devices_list:
            return
        try:
            dev_id = int(escolha.split("]")[0].replace("[", ""))
            self.recorder.config["device_id"] = dev_id
            salvar_configuracao(self.recorder.config)

            if self.recorder.is_recording:
                self.recorder.parar_gravacao()
                time.sleep(0.3)
                self.recorder.iniciar_gravacao(device_id=dev_id)
            else:
                self.recorder.iniciar_monitoramento(device_id=dev_id)
        except Exception as e:
            print(f"[ERRO MIC] {e}")

    def _ao_mudar_modelo(self, modelo):
        self.recorder.config["model_size"] = modelo
        salvar_configuracao(self.recorder.config)
        self.transcriber.set_model(model_size=modelo, language=self.recorder.config.get("language", "pt"))

    def _ao_mudar_auto_record(self):
        valor = bool(self.chk_auto.get())
        self.recorder.config["auto_record"] = valor
        salvar_configuracao(self.recorder.config)
        get_logger().info("CONFIG", "ALTERACAO", f"Auto-recuperar ao iniciar: {'ATIVADO' if valor else 'DESATIVADO'}")
        self._atualizar_painel_logs()

    def _ao_mudar_auto_transcribe(self):
        val = bool(self.chk_auto_transcribe.get())
        self.recorder.config["auto_transcribe_on_stop"] = val
        salvar_configuracao(self.recorder.config)
        get_logger().info("CONFIG", "ALTERACAO", f"Auto-transcrever ao parar: {'ATIVADO' if val else 'DESATIVADO'}")
        self._atualizar_painel_logs()

    def _ao_mudar_auto_rename(self):
        val = bool(self.chk_auto_rename.get())
        self.recorder.config["auto_rename_contextual"] = val
        salvar_configuracao(self.recorder.config)
        get_logger().info("CONFIG", "ALTERACAO", f"Renomeacao contextual: {'ATIVADO' if val else 'DESATIVADO'}")
        self._atualizar_painel_logs()

    def _atualizar_painel_logs(self):
        if not hasattr(self, "txt_logs"):
            return
        filtro = self.combo_log_filter.get() if hasattr(self, "combo_log_filter") else "TODOS"
        registros = get_logger().get_recent_records(limit=250, level_filter=filtro)
        self.txt_logs.delete("1.0", "end")
        for r in registros:
            linha = f"{r['timestamp']} [{r['level']:5s}] [{r['modulo']}] [{r['tarefa']}] {r['mensagem']}\n"
            self.txt_logs.insert("end", linha)
        self.txt_logs.see("end")

    def _limpar_tela_logs(self):
        if hasattr(self, "txt_logs"):
            self.txt_logs.delete("1.0", "end")

    def _exportar_logs(self):
        destino = filedialog.asksaveasfilename(
            parent=self,
            defaultextension=".log",
            filetypes=[("Arquivos de Log", "*.log"), ("Todos os arquivos", "*.*")],
            title="Exportar Logs de Auditoria",
            initialfile=f"auditoria_gravador_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        )
        if destino:
            ok = get_logger().exportar_logs(Path(destino))
            if ok:
                messagebox.showinfo("Exportação Concluída", f"Logs exportados com sucesso para:\n{destino}")
            else:
                messagebox.showerror("Erro", "Falha ao exportar arquivo de logs.")

    def _verificar_auto_recuperacao(self):
        if self.recorder.config.get("auto_record", False) and not self.recorder.is_recording:
            print("[AUTO-RECOVERY] Retomando gravação contínua na inicialização...")
            self._iniciar_gravacao()

    def _alternar_mute(self):
        mudo = self.recorder.alternar_mute()
        if mudo:
            self.btn_mute.configure(
                text="🔇 MUTADO (Ativo)",
                fg_color="#dc2626",
                hover_color="#b91c1c"
            )
            self.lbl_mute_badge.configure(text="[ 🔇 MUDO ATIVO: Captação Silenciada ]")
        else:
            self.btn_mute.configure(
                text="🎙️ Mudo Temporário",
                fg_color="#334155",
                hover_color="#475569"
            )
            self.lbl_mute_badge.configure(text="")
        self._atualizar_painel_logs()

    def _iniciar_gravacao(self):
        res = self.recorder.iniciar_gravacao()
        if res.get("status") in ["success", "already_recording"]:
            self.btn_iniciar.configure(state="disabled")
            self.btn_parar.configure(state="normal", fg_color="#dc2626", hover_color="#b91c1c")
            self.badge_status.configure(
                text="● GRAVANDO",
                fg_color="#7f1d1d",
                hover_color="#7f1d1d",
                text_color="#fca5a5"
            )
            self._atualizar_icone_barra_tarefas(gravando=True, fase_acesa=True, mutado=False)
            self._atualizar_lista_audios()
            self._atualizar_lista_transcricoes()
        else:
            messagebox.showerror("Erro ao Iniciar", f"Não foi possível iniciar a gravação:\n{res.get('message')}")

    def _parar_gravacao(self):
        res = self.recorder.parar_gravacao()
        if self.recorder.is_muted:
            self.recorder.set_mute(False)
            self.btn_mute.configure(
                text="🎙️ Mudo Temporário",
                fg_color="#334155",
                hover_color="#475569"
            )
            self.lbl_mute_badge.configure(text="")
        self.btn_iniciar.configure(state="normal")
        self.btn_parar.configure(state="disabled", fg_color="#475569")
        self.badge_status.configure(
            text="● PRONTO",
            fg_color="#064e3b",
            hover_color="#064e3b",
            text_color="#34d399"
        )
        self.lbl_timer.configure(text="⏱️ 00:00:00")
        self.lbl_file_size.configure(text="📦 Arquivo: 0.0 MB")
        self.progress_vu.set(0.0)
        self.lbl_vu_db.configure(text="-60.0 dB")
        self._atualizar_icone_barra_tarefas(gravando=False)
        self._atualizar_lista_audios()
        self._atualizar_lista_transcricoes()
        self._atualizar_painel_logs()

        # Fluxo automatico: se habilitado, enfileira e transcreve o ultimo audio finalizado
        if self.recorder.config.get("auto_transcribe_on_stop", False):
            ultimo_audio = res.get("audio_file") or self.recorder.obter_ultimo_audio_finalizado()
            if ultimo_audio and ultimo_audio.exists():
                get_logger().info("AUTOMACAO", "DISPARO", f"Disparando transcricao automatica pos-parada: {ultimo_audio.name}")
                self._atualizar_painel_logs()
                self._executar_pipeline_transcricao(ultimo_audio, is_auto=True)

    # --- Loop Periodico da Interface ---
    def _loop_interface(self):
        st = self.recorder.get_status()

        # 1. Atualiza Timer, Tamanho do Arquivo e Medidor VU/dB (ativo continuamente)
        if st.get("is_muted"):
            self.lbl_vu_db.configure(text="🔇 MUDO", text_color="#ef4444")
            self.progress_vu.set(0.0)
            if not self.lbl_mute_badge.cget("text"):
                self.lbl_mute_badge.configure(text="[ 🔇 MUDO ATIVO: Captação Silenciada ]")
        else:
            db = st["level_db"]
            self.lbl_vu_db.configure(text=f"{db:.1f} dB", text_color="#94a3b8")
            pct = max(0.0, min(1.0, (db + 60.0) / 60.0))
            self.progress_vu.set(pct)
            if self.lbl_mute_badge.cget("text"):
                self.lbl_mute_badge.configure(text="")

        # 1.1. Atualiza Grafico de Som em Tempo Real (ultimos 5 segundos passando na tela)
        try:
            self._atualizar_grafico_tempo_real()
        except Exception as e_live:
            get_logger().warn("GRAFICO_LIVE", "ERRO", f"Falha ao atualizar grafico de som: {e_live}")

        if st["is_recording"]:
            dur_fmt = self._formatar_segundos(st["duration_seconds"])
            self.lbl_timer.configure(text=f"⏱️ {dur_fmt}")
            self.lbl_file_size.configure(text=f"📦 {st.get('file_size_mb', 0.0):.1f} MB")

            # Piscamento do icone da barra de tarefas em vermelho (alterna a cada 500ms)
            fase_acesa = int(time.time() * 2) % 2 == 0
            is_muted = bool(st.get("is_muted", False))
            chave_pisca = (True, fase_acesa, is_muted)
            if getattr(self, "_ultimo_estado_pisca", None) != chave_pisca:
                self._ultimo_estado_pisca = chave_pisca
                self._atualizar_icone_barra_tarefas(gravando=True, fase_acesa=fase_acesa, mutado=is_muted)
        else:
            self.lbl_timer.configure(text="⏱️ 00:00:00")
            self.lbl_file_size.configure(text="📦 Arquivo: 0.0 MB")

            # Restaura icone padrao da barra de tarefas quando nao esta gravando
            if getattr(self, "_ultimo_estado_pisca", None) != (False, False, False):
                self._ultimo_estado_pisca = (False, False, False)
                self._atualizar_icone_barra_tarefas(gravando=False)

        # 2. Atualiza informacoes da Particao/Disco
        disk = st.get("disk_info", {})
        if disk and disk.get("drive"):
            self.lbl_disk_space.configure(text=f"💾 {disk['drive']} {disk['free_gb']} GB livres")
            self.lbl_disk_detail.configure(
                text=f"Partição {disk['drive']}: {disk['free_gb']} GB livres de {disk['total_gb']} GB ({disk['percent_free']}%)"
            )
            if disk["percent_free"] < 10.0:
                self.lbl_disk_space.configure(text_color="#ef4444")
            else:
                self.lbl_disk_space.configure(text_color="#38bdf8")

        # 3. Atualiza reproducao de audio
        if self.is_playing and not self.is_paused:
            pos_ms = pygame.mixer.music.get_pos()
            if pos_ms >= 0:
                start_offset = getattr(self, "player_start_sec", 0.0)
                pos_sec = start_offset + (pos_ms / 1000.0)
                if self.player_duration_sec > 0:
                    pos_sec_capped = min(self.player_duration_sec, pos_sec)
                    pct = min(100.0, (pos_sec_capped / self.player_duration_sec) * 100.0)
                    self.slider_pos.set(pct)
                    str_pos = self._formatar_segundos(pos_sec_capped)
                    str_tot = self._formatar_segundos(self.player_duration_sec)
                    self.lbl_player_tempo.configure(text=f"{str_pos} / {str_tot}")
                    self._atualizar_playhead_waveform(pos_sec_capped)
                else:
                    self._atualizar_playhead_waveform(pos_sec)
            elif not pygame.mixer.music.get_busy():
                self.is_playing = False
                self.player_start_sec = 0.0
                self.btn_play_pause.configure(text="▶ Ouvir")
                if hasattr(self, "canvas_waveform"):
                    self.canvas_waveform.delete("playhead")

        # 5. Watchdog de Transcricao: monitora heartbeat e tempo sem avanco
        if self.transcriber and self.transcriber.last_progress_tick > 0:
            if hasattr(self, "btn_cancelar_transcricao") and self.btn_cancelar_transcricao.winfo_ismapped():
                tempo_sem_avanco = time.time() - self.transcriber.last_progress_tick
                timeout_cfg = self.recorder.config.get("watchdog_timeout_sec", 120)
                if tempo_sem_avanco > timeout_cfg and not getattr(self, "_watchdog_alertado", False):
                    self._watchdog_alertado = True
                    get_logger().warn(
                        "WATCHDOG",
                        "ESTAGNACAO",
                        f"Transcricao sem avanco ha {int(tempo_sem_avanco)}s (limite: {timeout_cfg}s). Processo monitorado."
                    )
                    self._atualizar_painel_logs()
                elif tempo_sem_avanco <= 15:
                    self._watchdog_alertado = False

        # 6. Atualizacao de logs em tempo real
        logger = get_logger()
        if not logger.queue.empty():
            tem_novos = False
            while not logger.queue.empty():
                try:
                    logger.queue.get_nowait()
                    tem_novos = True
                except Exception:
                    break
            if tem_novos:
                self._atualizar_painel_logs()

        self.after(50, self._loop_interface)

    # --- Visualizador de Grafico de Som em Tempo Real (Ultimos 5 segundos) ---
    def _ao_mudar_ganho_live(self, valor):
        try:
            self.live_gain_factor = float(valor.replace("x", ""))
        except Exception:
            self.live_gain_factor = 3.0

    def _ao_redimensionar_canvas_live(self, event=None):
        self._desenhar_grade_tempo_real()

    def _desenhar_grade_tempo_real(self):
        """Desenha a grade de tempo estatica e os marcadores de segundos (-5s ate Agora)."""
        if not hasattr(self, "canvas_live_wave"):
            return
        self.canvas_live_wave.delete("grid")
        largura = self.canvas_live_wave.winfo_width()
        altura = self.canvas_live_wave.winfo_height()
        if largura <= 20:
            try:
                largura = int(self.canvas_live_wave.cget("width"))
            except Exception:
                largura = 800
        if altura <= 10:
            try:
                altura = int(self.canvas_live_wave.cget("height"))
            except Exception:
                altura = 76
        if largura <= 20 or altura <= 10:
            return

        cy = altura / 2.0
        # Linha central de referencia zero
        self.canvas_live_wave.create_line(0, cy, largura, cy, fill="#1e293b", width=1, tags="grid")

        # Marcadores verticais de segundos (-5.0s, -4.0s, -3.0s, -2.0s, -1.0s, Agora)
        etiquetas = ["-5.0s", "-4.0s", "-3.0s", "-2.0s", "-1.0s", "Agora (0s)"]
        for i, rotulo in enumerate(etiquetas):
            x = (i / 5.0) * (largura - 4) + 2
            ancora = "w" if i == 0 else ("e" if i == 5 else "center")
            self.canvas_live_wave.create_line(x, 0, x, altura, fill="#131b2e", dash=(2, 3), tags="grid")
            self.canvas_live_wave.create_text(
                x,
                altura - 6,
                text=rotulo,
                fill="#475569",
                font=("Consolas", 8),
                anchor=ancora,
                tags="grid"
            )

    def _atualizar_grafico_tempo_real(self):
        """Renderiza o grafico de ondas sonoras continuo com as amostras dos ultimos 5 segundos."""
        if not hasattr(self, "canvas_live_wave"):
            return

        largura = self.canvas_live_wave.winfo_width()
        altura = self.canvas_live_wave.winfo_height()
        if largura <= 20:
            try:
                largura = int(self.canvas_live_wave.cget("width"))
            except Exception:
                largura = 800
        if altura <= 10:
            try:
                altura = int(self.canvas_live_wave.cget("height"))
            except Exception:
                altura = 76
        if largura <= 20 or altura <= 10:
            return

        amostras = self.recorder.obter_amostras_tempo_real(5.0)
        n_amostras = len(amostras)
        if n_amostras == 0:
            return

        cy = int(altura // 2)
        max_h = max(2, cy - 6)

        # Atualiza badge textual de estatisticas da janela
        db = self.recorder.current_level_db
        sr = int(self.recorder.config.get("sample_rate", 16000))
        if self.recorder.is_muted:
            txt_stats = f"🔇 MUDO | {sr // 1000}kHz | Janela: 5.0s"
            cor_stats = "#ef4444"
        elif self.recorder.is_recording:
            txt_stats = f"🔴 {db:.1f} dB | {sr // 1000}kHz | Janela: 5.0s"
            cor_stats = "#38bdf8"
        else:
            txt_stats = f"⚪ {db:.1f} dB | {sr // 1000}kHz | Monitorando"
            cor_stats = "#94a3b8"

        if hasattr(self, "lbl_live_stats"):
            self.lbl_live_stats.configure(text=txt_stats, text_color=cor_stats)

        # Renderizacao rasterizada cristalina com PIL (Pixel-Perfect com tracos ultra-finos de 1px)
        img = Image.new("RGB", (largura, altura), "#020617")
        draw = ImageDraw.Draw(img)

        # Linhas de enquadramento discretas (topo e base, identicas a referencia visual)
        draw.line([(0, 5), (largura, 5)], fill="#1e293b", width=1)
        draw.line([(0, altura - 6), (largura, altura - 6)], fill="#1e293b", width=1)

        # Linha central de horizonte
        draw.line([(0, cy), (largura, cy)], fill="#0f172a", width=1)

        if self.recorder.is_muted:
            draw.line([(0, cy), (largura, cy)], fill="#ef4444", width=2)
            draw.text((largura // 2 - 120, cy - 8), "🔇 MICROFONE SILENCIADO (MUDO TEMPORÁRIO)", fill="#ef4444")
        else:
            # Barras em tracos ultra-finos de 1px com passo uniforme de 3px (1px linha, 2px espaco)
            bar_step = 3
            num_bars = max(20, (largura - 4) // bar_step)
            chunk_size = n_amostras // num_bars
            if chunk_size > 0:
                reshaped = amostras[:num_bars * chunk_size].reshape(num_bars, chunk_size)
                v_max = np.max(reshaped, axis=1)
                v_min = np.min(reshaped, axis=1)
                amp = np.maximum(np.abs(v_max), np.abs(v_min))

                ganho = getattr(self, "live_gain_factor", 3.0)
                mult = ganho * 1.5
                cor_barra = "#38bdf8"

                for i in range(num_bars):
                    x1 = i * bar_step + 2
                    a = float(amp[i])
                    if a < 0.003:
                        h_bar = 2
                    else:
                        h_bar = int(min(max_h, max(2, (a ** 0.85) * mult * max_h)))

                    draw.line([(x1, cy - h_bar), (x1, cy + h_bar)], fill=cor_barra, width=1)

            # Traco indicador do instante atual na borda direita (Agora)
            cor_borda = "#22c55e" if self.recorder.is_recording else "#38bdf8"
            draw.line([(largura - 2, 6), (largura - 2, altura - 6)], fill=cor_borda, width=2)

        photo = ImageTk.PhotoImage(img)
        self._live_wave_photo_ref = photo
        self.canvas_live_wave.delete("wave")
        self.canvas_live_wave.create_image(0, 0, image=photo, anchor="nw", tags="wave")

    # --- Gestao de Arquivos de Audio e Waveform Draft ---
    @staticmethod
    def _extrair_data_dia_arquivo(p: Path) -> datetime.date:
        nome = p.name
        partes = nome.replace("gravando_", "").replace("transcricao_", "").replace("ATA_", "").replace("ata_", "").split("_")
        if partes and len(partes[0]) == 10 and partes[0].count("-") == 2:
            try:
                return datetime.datetime.strptime(partes[0], "%Y-%m-%d").date()
            except Exception:
                pass
        return datetime.datetime.fromtimestamp(p.stat().st_mtime).date()

    @staticmethod
    def _formatar_dia_divisor(data_dt: datetime.date) -> str:
        dias_semana = {
            0: "Segunda-feira",
            1: "Terça-feira",
            2: "Quarta-feira",
            3: "Quinta-feira",
            4: "Sexta-feira",
            5: "Sábado",
            6: "Domingo"
        }
        nome_dia = dias_semana.get(data_dt.weekday(), "")
        return f"{data_dt.strftime('%d/%m/%Y')} ({nome_dia})"

    def _atualizar_lista_audios(self):
        item_sel_anterior = None
        sel = [s for s in self.tree_audios.selection() if not s.startswith("sep_")]
        if sel:
            item_sel_anterior = sel[0]

        for item in self.tree_audios.get_children():
            self.tree_audios.delete(item)

        gravacoes_dir, _ = self.recorder.obter_diretorios()
        if not gravacoes_dir.exists():
            return

        ultimo_dia = None
        dias_inseridos = set()
        arquivos = sorted(
            gravacoes_dir.glob("*.wav"),
            key=lambda x: (self._extrair_data_dia_arquivo(x), x.stat().st_mtime),
            reverse=True
        )
        for p in arquivos:
            stat = p.stat()
            data_dia = self._extrair_data_dia_arquivo(p)

            # Insere linha divisoria visual entre cada dia de gravacao
            sep_id = f"sep_dia_{data_dia.strftime('%Y%m%d')}"
            if data_dia != ultimo_dia:
                ultimo_dia = data_dia
                if sep_id not in dias_inseridos and not self.tree_audios.exists(sep_id):
                    dias_inseridos.add(sep_id)
                    dia_fmt = self._formatar_dia_divisor(data_dia)
                    self.tree_audios.insert(
                        "", "end",
                        iid=sep_id,
                        values=(f"── 📅 {dia_fmt} ─────────────────────────────", "────", "───", "───", "─────"),
                        tags=("separador_dia",)
                    )

            size_mb = f"{stat.st_size / (1024 * 1024):.2f}"
            duracao_seg = int(stat.st_size / 32000)
            duracao_fmt = self._formatar_segundos(duracao_seg)
            mtime = datetime.datetime.fromtimestamp(stat.st_mtime).strftime("%d/%m/%Y %H:%M:%S")

            onda_txt = gerar_onda_texto(p, num_barras=18)

            self.tree_audios.insert(
                "", "end",
                iid=p.name,
                values=(p.name, onda_txt, duracao_fmt, size_mb, mtime)
            )

        # Mantem selecao anterior ou seleciona o primeiro item de audio real
        filhos = [i for i in self.tree_audios.get_children() if not i.startswith("sep_")]
        if filhos:
            alvo = item_sel_anterior if item_sel_anterior in filhos else filhos[0]
            self.tree_audios.selection_set(alvo)
            self._ao_selecionar_audio()

    def _ao_selecionar_audio(self, event=None):
        selecao = [s for s in self.tree_audios.selection() if not s.startswith("sep_")]
        if not selecao:
            return
        nome_arquivo = selecao[0]
        gravacoes_dir, _ = self.recorder.obter_diretorios()
        caminho = gravacoes_dir / nome_arquivo
        if not caminho.exists():
            return
        self._desenhar_waveform_detalhado(caminho)

    def _desenhar_waveform_detalhado(self, caminho: Path):
        if not caminho.exists() or not hasattr(self, "canvas_waveform"):
            return

        self.canvas_waveform.delete("all")
        largura = self.canvas_waveform.winfo_width()
        altura = self.canvas_waveform.winfo_height()

        if largura <= 1:
            largura = 800
        if altura <= 1:
            altura = 85

        self._last_rendered_wf_width = largura
        self._last_rendered_wf_path = caminho

        num_pontos = max(80, min(600, largura // 2))
        dados = extrair_amostras_waveform(caminho, num_pontos=num_pontos)

        dur_fmt = self._formatar_segundos(dados["duracao_seg"])
        self.lbl_wf_titulo.configure(text=f"📊 Draft do Som Capturado: {caminho.name}")
        self.lbl_wf_duracao.configure(text=f"⏱️ {dur_fmt}")
        self.lbl_wf_pico.configure(text=f"⚡ Pico: {dados['pico_db']:.1f} dB")
        self.lbl_wf_rms.configure(text=f"🔊 RMS Médio: {dados['rms_medio_db']:.1f} dB")

        ativ_pct = dados["atividade_pct"]
        cor_ativ = "#34d399" if ativ_pct > 30 else ("#f59e0b" if ativ_pct > 5 else "#ef4444")
        self.lbl_wf_atividade.configure(text=f"🎙️ Atividade: {ativ_pct:.1f}%", text_color=cor_ativ)

        self._current_waveform_data = {
            "caminho": caminho,
            "duracao": dados["duracao_seg"],
            "valido": dados["valido"]
        }

        cy = altura // 2

        # Linha base central
        self.canvas_waveform.create_line(0, cy, largura, cy, fill="#1e293b", width=1)

        pontos = dados["pontos"]
        valido = dados["valido"]

        if not valido:
            self.canvas_waveform.create_text(
                largura // 2, cy,
                text="Sem atividade sonora detectada ou áudio nulo (sinal mudo)",
                fill="#64748b",
                font=("Segoe UI", 10, "italic")
            )
            return

        passo = largura / len(pontos)
        margem_y = 12
        h_disponivel = altura - (margem_y * 2)

        for i, val in enumerate(pontos):
            x = i * passo
            bar_h = max(2, int(val * h_disponivel))
            y0 = cy - bar_h // 2
            y1 = cy + bar_h // 2

            if val > 0.6:
                cor = "#38bdf8"
            elif val > 0.2:
                cor = "#0284c7"
            elif val > 0.05:
                cor = "#0369a1"
            else:
                cor = "#1e293b"

            self.canvas_waveform.create_line(x, y0, x, y1, fill=cor, width=2)

        # Marcadores de tempo
        if dados["duracao_seg"] > 0:
            for frac in (0.0, 0.25, 0.5, 0.75, 1.0):
                xm = int(frac * (largura - 2))
                sec_m = frac * dados["duracao_seg"]
                txt = self._formatar_segundos(sec_m)
                anchor = "w" if frac == 0.0 else ("e" if frac == 1.0 else "center")
                self.canvas_waveform.create_line(xm, altura - 16, xm, altura - 6, fill="#334155", width=1)
                self.canvas_waveform.create_text(xm, altura - 8, text=txt, fill="#64748b", font=("Consolas", 8), anchor=anchor)

        # Atualiza cursor do playhead se estiver em reproducao
        if self.is_playing and self.playing_file == caminho:
            self._atualizar_playhead_waveform()

    def _ao_redimensionar_waveform(self, event=None):
        if hasattr(self, "_current_waveform_data") and self._current_waveform_data:
            caminho = self._current_waveform_data.get("caminho")
            if caminho and caminho.exists():
                largura = self.canvas_waveform.winfo_width()
                if abs(largura - getattr(self, "_last_rendered_wf_width", 0)) > 20:
                    self._desenhar_waveform_detalhado(caminho)

    def _ao_clicar_waveform(self, event):
        if not hasattr(self, "_current_waveform_data") or not self._current_waveform_data:
            return
        largura = self.canvas_waveform.winfo_width()
        if largura <= 1:
            return
        pct = max(0.0, min(1.0, event.x / largura))
        duracao = self._current_waveform_data.get("duracao", 0.0)
        caminho = self._current_waveform_data.get("caminho")
        if caminho and duracao > 0:
            start_sec = pct * duracao
            # Desenha instantaneamente o cursor no ponto clicado para resposta visual imediata
            altura = self.canvas_waveform.winfo_height()
            self.canvas_waveform.delete("playhead")
            self.canvas_waveform.create_line(event.x, 0, event.x, altura, fill="#f59e0b", width=2, tags="playhead")
            self._tocar_audio_em_posicao(caminho, start_sec=start_sec)

    def _atualizar_playhead_waveform(self, pos_sec: Optional[float] = None):
        if not hasattr(self, "canvas_waveform") or not getattr(self, "_current_waveform_data", None):
            return
        if self._current_waveform_data.get("caminho") != self.playing_file:
            return

        dur = self._current_waveform_data.get("duracao", 0.0)
        if dur <= 0:
            return

        if pos_sec is None:
            pos_ms = pygame.mixer.music.get_pos()
            start_offset = getattr(self, "player_start_sec", 0.0)
            pos_sec = max(0.0, start_offset + (pos_ms / 1000.0)) if pos_ms >= 0 else start_offset

        largura = self.canvas_waveform.winfo_width()
        altura = self.canvas_waveform.winfo_height()
        if largura <= 1:
            return

        x = min(largura, max(0.0, (pos_sec / dur) * largura))
        self.canvas_waveform.delete("playhead")
        self.canvas_waveform.create_line(x, 0, x, altura, fill="#f59e0b", width=2, tags="playhead")

    def _tocar_audio_selecionado(self):
        selecao = [s for s in self.tree_audios.selection() if not s.startswith("sep_")]
        if not selecao:
            return
        nome_arquivo = selecao[0]
        gravacoes_dir, _ = self.recorder.obter_diretorios()
        caminho = gravacoes_dir / nome_arquivo
        if not caminho.exists():
            return
        self._tocar_audio_em_posicao(caminho, start_sec=0.0)

    def _tocar_audio_em_posicao(self, caminho: Path, start_sec: float = 0.0):
        if not caminho.exists():
            return

        self.playing_file = caminho
        self.player_start_sec = max(0.0, float(start_sec))

        # Obtem a duracao precisa do arquivo
        dur = 0.0
        if hasattr(self, "_current_waveform_data") and self._current_waveform_data and self._current_waveform_data.get("caminho") == caminho:
            dur = self._current_waveform_data.get("duracao", 0.0)
        if dur <= 0:
            try:
                import soundfile as sf
                dur = sf.info(str(caminho)).duration
            except Exception:
                stat = caminho.stat()
                dur = max(1.0, stat.st_size / 32000.0)
        self.player_duration_sec = dur

        try:
            pygame.mixer.music.load(str(caminho))
            pygame.mixer.music.play(start=self.player_start_sec)
            self.is_playing = True
            self.is_paused = False
            self.btn_play_pause.configure(text="⏸ Pausar")
            self.lbl_player_info.configure(text=f"🎧 Reproduzindo: {caminho.name}")

            # Atualiza imediatamente o slider e o tempo exibido para a posicao de seek
            if self.player_duration_sec > 0:
                pct = min(100.0, (self.player_start_sec / self.player_duration_sec) * 100.0)
                self.slider_pos.set(pct)
                str_pos = self._formatar_segundos(self.player_start_sec)
                str_tot = self._formatar_segundos(self.player_duration_sec)
                self.lbl_player_tempo.configure(text=f"{str_pos} / {str_tot}")

            # Se a waveform atual nao for deste arquivo, desenha-a
            if not getattr(self, "_current_waveform_data", None) or self._current_waveform_data.get("caminho") != caminho:
                self._desenhar_waveform_detalhado(caminho)

            # Posiciona o cursor playhead
            self._atualizar_playhead_waveform(self.player_start_sec)
        except Exception as e:
            messagebox.showerror("Erro de Reprodução", f"Não foi possível reproduzir o áudio:\n{e}")

    def _alternar_reproducao(self):
        if not self.playing_file:
            self._tocar_audio_selecionado()
            return

        if self.is_playing and not self.is_paused:
            pygame.mixer.music.pause()
            self.is_paused = True
            self.btn_play_pause.configure(text="▶ Continuar")
        elif self.is_paused:
            pygame.mixer.music.unpause()
            self.is_paused = False
            self.btn_play_pause.configure(text="⏸ Pausar")
        else:
            self._tocar_audio_selecionado()

    def _parar_reproducao(self):
        try:
            pygame.mixer.music.stop()
        except Exception:
            pass
        self.is_playing = False
        self.is_paused = False
        self.player_start_sec = 0.0
        self.slider_pos.set(0)
        self.btn_play_pause.configure(text="▶ Ouvir")
        self.lbl_player_tempo.configure(text="00:00:00 / 00:00:00")
        self.lbl_player_info.configure(text="🎧 Nenhum áudio em reprodução")
        if hasattr(self, "canvas_waveform"):
            self.canvas_waveform.delete("playhead")

    def _ao_arrastar_slider(self, valor):
        if self.playing_file and self.player_duration_sec > 0:
            target_sec = (float(valor) / 100.0) * self.player_duration_sec
            self._tocar_audio_em_posicao(self.playing_file, start_sec=target_sec)

    def _obter_audios_pendentes_transcricao(self) -> List[Path]:
        """Retorna a lista de arquivos .wav que ainda nao possuem transcricao .md correspondente."""
        gravacoes_dir, transcricoes_dir = self.recorder.obter_diretorios()
        if not gravacoes_dir.exists():
            return []
        wavs = sorted(list(gravacoes_dir.glob("*.wav")), key=lambda x: x.stat().st_mtime, reverse=True)
        if not transcricoes_dir.exists():
            return wavs

        mds = list(transcricoes_dir.glob("*.md"))
        pendentes = []
        for w in wavs:
            pref = extrair_data_hora_prefixo(w.name)
            has_trans = any(pref in m.name and not m.name.startswith("ATA") and "_ata" not in m.name.lower() and not m.name.lower().startswith("ata_") for m in mds)
            if not has_trans:
                pendentes.append(w)
        return pendentes

    def _buscar_audio_correspondente(self, md_path: Path) -> Optional[Path]:
        """Busca o arquivo de audio correspondente ao arquivo de transcricao atraves do prefixo temporal."""
        gravacoes_dir, _ = self.recorder.obter_diretorios()
        if not gravacoes_dir.exists():
            return None
        pref = extrair_data_hora_prefixo(md_path.name)
        for w in gravacoes_dir.glob("*.wav"):
            if pref in w.name:
                return w
        return None

    def _selecionar_todos_audios(self, event=None):
        todos = [i for i in self.tree_audios.get_children() if not i.startswith("sep_")]
        if todos:
            self.tree_audios.selection_set(todos)
            if hasattr(self, "lbl_wf_titulo"):
                self.lbl_wf_titulo.configure(text=f"📊 Todos os {len(todos)} arquivos de áudio selecionados (Ctrl+A)")
        return "break"

    def _selecionar_todos_md(self, event=None):
        todos = [i for i in self.tree_md.get_children() if not i.startswith("sep_")]
        if todos:
            self.tree_md.selection_set(todos)
        return "break"

    def _transcrever_audio_selecionado(self):
        """Transcreve os audios atualmente selecionados na tabela (um unico arquivo ou multiplos em lote)."""
        selecao = [s for s in self.tree_audios.selection() if not s.startswith("sep_")]
        if not selecao:
            messagebox.showinfo("Nenhum Áudio Selecionado", "Por favor, selecione um ou mais arquivos de áudio na lista para transcrever.")
            return

        gravacoes_dir, _ = self.recorder.obter_diretorios()

        # Multiplos arquivos selecionados: executa transcricao sequencial dos selecionados
        if len(selecao) > 1:
            caminhos = [gravacoes_dir / nome for nome in selecao if (gravacoes_dir / nome).exists() and (gravacoes_dir / nome).stat().st_size > 44]
            if not caminhos:
                messagebox.showwarning("Aviso", "Nenhum arquivo de áudio válido encontrado entre os selecionados.")
                return

            resp = messagebox.askyesno(
                "Transcrever Áudios Selecionados",
                f"Deseja iniciar a transcrição com Whisper dos {len(caminhos)} arquivos de áudio selecionados?"
            )
            if not resp:
                return

            self._transcrever_lote(caminhos_alvo=caminhos)
            return

        # Um unico arquivo selecionado
        nome_arquivo = selecao[0]
        caminho = gravacoes_dir / nome_arquivo

        resp = messagebox.askyesno(
            "Transcrever Áudio",
            f"Deseja iniciar a transcrição completa com Whisper do arquivo:\n\n{nome_arquivo}?\n\nO progresso em porcentagem (%) será exibido na barra em tempo real."
        )
        if not resp:
            return

        self._executar_pipeline_transcricao(caminho, is_auto=False)

    def _transcrever_lote(self, caminhos_alvo: Optional[List[Path]] = None):
        """Dispara a transcricao em lote de audios selecionados com Whisper."""
        if getattr(self, "_lote_em_andamento", False):
            messagebox.showwarning("Em Andamento", "Um processamento em lote ou transcrição já está em andamento.")
            return

        gravacoes_dir, _ = self.recorder.obter_diretorios()
        fila: List[Path] = []

        if caminhos_alvo:
            fila = [p for p in caminhos_alvo if p.exists() and p.stat().st_size > 44]
        else:
            selecao = [s for s in self.tree_audios.selection() if not s.startswith("sep_")]
            fila = [gravacoes_dir / nome for nome in selecao if (gravacoes_dir / nome).exists() and (gravacoes_dir / nome).stat().st_size > 44]

        if not fila:
            messagebox.showinfo("Nenhum Áudio Selecionado", "Por favor, selecione um ou mais arquivos de áudio na lista para transcrever.")
            return

        # Ignora audio gravando atualmente
        if self.recorder.is_recording and self.recorder.current_audio_file:
            fila = [p for p in fila if p.name != self.recorder.current_audio_file.name]
            if not fila:
                messagebox.showwarning("Aviso", "O único áudio selecionado está gravando no momento. Pare a gravação antes de transcrever.")
                return

        self._lote_em_andamento = True
        self._lote_cancelado = False

        # Desabilita botao de transcricao durante o lote
        self.btn_transcrever_sel.configure(state="disabled")

        self.btn_cancelar_transcricao.configure(text="✖ Cancelar Transcrição", state="normal")
        self.btn_cancelar_transcricao.pack(side="left", padx=6)
        self.progress_transcribe.set(0.0)
        self.progress_transcribe.pack(side="left", padx=6)
        self.lbl_transcribe_pct.configure(text="0.0%")
        self.lbl_transcribe_pct.pack(side="left", padx=4)
        self.lbl_transcribe_status.configure(text=f"[1/{len(fila)}] Iniciando processamento...")
        self.lbl_transcribe_status.pack(side="left", padx=4)

        def worker_lote():
            total = len(fila)
            sucessos = 0
            falhas = 0

            for idx, caminho in enumerate(fila):
                if self._lote_cancelado:
                    break

                num = idx + 1
                nome_audio = caminho.name
                self._current_transcription_id += 1
                session_id = self._current_transcription_id
                if self.transcriber:
                    self.transcriber.last_progress_tick = time.time()

                self.after(0, lambda n=nome_audio, i=num, t=total: self._atualizar_status_lote(f"[Lote {i}/{t}] Transcrevendo {n}..."))

                def on_progresso(info):
                    if session_id != self._current_transcription_id or self._lote_cancelado:
                        return
                    pct = info.get("percent", 0.0)
                    msg = info.get("message", f"{pct:.1f}%")
                    self.after(0, lambda p=pct, m=f"[{num}/{total}] {msg}": self._atualizar_progresso_transcricao(p, m))

                try:
                    out_md = self.transcriber.transcribe_full_file(caminho, progress_cb=on_progresso)
                    if self._lote_cancelado:
                        break

                    if out_md is not None and out_md.exists():
                        sucessos += 1
                        if self.recorder.config.get("auto_rename_contextual", True):
                            try:
                                txt = out_md.read_text(encoding="utf-8")
                                slug = extrair_titulo_contextual(txt)
                                renomear_trio_arquivos(caminho, out_md, None, slug)
                            except Exception:
                                pass

                        self.after(0, self._atualizar_listas_pos_item_lote)
                    else:
                        falhas += 1
                except Exception as e:
                    falhas += 1
                    get_logger().error("LOTE", "ERRO", f"Erro no lote ao transcrever {nome_audio}: {e}")

            self.after(0, lambda: self._finalizar_lote_transcricao(total, sucessos, falhas, self._lote_cancelado))

        threading.Thread(target=worker_lote, daemon=True, name="BatchTranscribeWorker").start()

    def _executar_pipeline_transcricao(self, caminho: Path, is_auto: bool = False):
        nome_arquivo = caminho.name
        self._current_transcription_id += 1
        session_id = self._current_transcription_id
        if self.transcriber:
            self.transcriber.last_progress_tick = time.time()
        self._watchdog_alertado = False

        # Ativa barra, rotulo e botao de cancelamento
        self.btn_transcrever_sel.configure(state="disabled")

        self.btn_cancelar_transcricao.configure(text="✖ Cancelar Transcrição", state="normal")
        self.btn_cancelar_transcricao.pack(side="left", padx=6)
        self.progress_transcribe.set(0.0)
        self.progress_transcribe.pack(side="left", padx=6)
        self.lbl_transcribe_pct.configure(text="0.0%")
        self.lbl_transcribe_pct.pack(side="left", padx=4)
        prefixo = "[Auto] " if is_auto else ""
        self.lbl_transcribe_status.configure(text=f"{prefixo}Processando {nome_arquivo}...")
        self.lbl_transcribe_status.pack(side="left", padx=4)

        if hasattr(self, "lbl_auto_status"):
            self.lbl_auto_status.configure(text=f"● Estado da Automação: Transcrevendo {nome_arquivo}...")

        def on_progresso(info):
            if session_id != self._current_transcription_id:
                return
            pct = info.get("percent", 0.0)
            msg = info.get("message", f"{pct:.1f}%")
            self.after(0, lambda: self._atualizar_progresso_transcricao(pct, msg))

        def worker():
            try:
                out_md = self.transcriber.transcribe_full_file(caminho, progress_cb=on_progresso)
                if session_id == self._current_transcription_id:
                    if out_md is not None:
                        self.after(0, lambda: self._pos_processamento_pipeline(caminho, out_md, is_auto=is_auto))
                    else:
                        self.after(0, self._pos_cancelamento)
            except Exception as e:
                if session_id == self._current_transcription_id:
                    get_logger().error("TRANSCRICAO", "ERRO", f"Erro no processamento de {nome_arquivo}: {e}")
                    self.after(0, lambda: self._falha_transcricao(str(e)))

        threading.Thread(target=worker, daemon=True, name="PipelineWorker").start()

    def _pos_processamento_pipeline(self, caminho_audio: Path, out_md: Path, is_auto: bool):
        self._restaurar_botoes_lote()
        self.progress_transcribe.set(1.0)
        self.lbl_transcribe_pct.configure(text="100.0%")
        self.lbl_transcribe_status.configure(text=f"Transcrição concluída: {out_md.name}")

        # Renomeacao contextual se habilitada
        if self.recorder.config.get("auto_rename_contextual", True):
            try:
                texto = out_md.read_text(encoding="utf-8")
                slug = extrair_titulo_contextual(texto)
                c_audio, c_md, _ = renomear_trio_arquivos(caminho_audio, out_md, None, slug)
                if c_md:
                    out_md = c_md
            except Exception as e_ren:
                get_logger().warn("RENOMEADOR", "AVISO", f"Nao foi possivel aplicar renomeacao contextual ({e_ren}).")

        if hasattr(self, "lbl_auto_status"):
            self.lbl_auto_status.configure(text="● Estado da Automação: Ocioso (Aguardando eventos)")

        self._atualizar_lista_audios()
        self._atualizar_lista_transcricoes()
        self._atualizar_painel_logs()

        if not is_auto:
            messagebox.showinfo("Sucesso", f"Transcrição concluída com 100% de sucesso:\n\n{out_md.name}")

    def _atualizar_status_lote(self, msg: str):
        self.lbl_transcribe_status.configure(text=msg)
        if hasattr(self, "lbl_auto_status"):
            self.lbl_auto_status.configure(text=f"● Estado da Automação: {msg}")

    def _atualizar_listas_pos_item_lote(self):
        self._atualizar_lista_audios()
        self._atualizar_lista_transcricoes()
        self._atualizar_painel_logs()

    def _finalizar_lote_transcricao(self, total: int, sucessos: int, falhas: int, cancelado: bool):
        self._restaurar_botoes_lote()
        self.progress_transcribe.set(1.0 if not cancelado else 0.0)
        self.lbl_transcribe_pct.configure(text="100.0%" if not cancelado else "Interrompido")
        self._atualizar_lista_audios()
        self._atualizar_lista_transcricoes()
        self._atualizar_painel_logs()

        status_msg = "Lote de transcrição concluído!" if not cancelado else "Lote de transcrição interrompido pelo usuário!"
        self.lbl_transcribe_status.configure(text=status_msg)

        resumo = f"{status_msg}\n\n• Áudios processados com sucesso: {sucessos} de {total}"
        if falhas > 0:
            resumo += f"\n• Falhas ou pulados: {falhas}"

        get_logger().info("LOTE", "FINALIZACAO", f"Lote concluido: {sucessos}/{total} transcrevidos.")
        messagebox.showinfo("Lote Concluído", resumo)

    def _restaurar_botoes_lote(self):
        self._lote_em_andamento = False
        self.btn_transcrever_sel.configure(state="normal")
        self.btn_cancelar_transcricao.configure(text="✖ Cancelar Transcrição", state="normal")
        self.btn_cancelar_transcricao.pack_forget()
        if hasattr(self, "lbl_auto_status"):
            self.lbl_auto_status.configure(text="● Estado da Automação: Ocioso (Aguardando eventos)")

    def _cancelar_transcricao(self):
        # Invalida a sessao imediatamente para ignorar callbacks antigos do worker
        self._current_transcription_id += 1
        self._lote_cancelado = True
        self.transcriber.request_cancel_transcription()

        # Restaura a interface e reativa os botoes IMEDIATAMENTE sem travas ou modais
        self._restaurar_botoes_lote()
        self.progress_transcribe.set(0.0)
        self.lbl_transcribe_pct.configure(text="Cancelado")
        self.lbl_transcribe_status.configure(text="Operação cancelada pelo usuário.")
        self._atualizar_lista_transcricoes()

    def _pos_cancelamento(self):
        self._restaurar_botoes_lote()
        self.progress_transcribe.set(0.0)
        self.lbl_transcribe_pct.configure(text="Cancelado")
        self.lbl_transcribe_status.configure(text="Transcrição cancelada pelo usuário.")
        self._atualizar_lista_transcricoes()

    def _atualizar_progresso_transcricao(self, pct, msg):
        self.progress_transcribe.set(pct / 100.0)
        self.lbl_transcribe_pct.configure(text=f"{pct:.1f}%")
        self.lbl_transcribe_status.configure(text=msg)

    def _pos_transcricao(self, nome_md):
        self._restaurar_botoes_lote()
        self.progress_transcribe.set(1.0)
        self.lbl_transcribe_pct.configure(text="100.0%")
        self.lbl_transcribe_status.configure(text=f"Transcrição concluída: {nome_md}")
        self._atualizar_lista_transcricoes()
        messagebox.showinfo("Sucesso", f"Transcrição concluída com 100% de sucesso:\n\n{nome_md}")

    def _falha_transcricao(self, erro):
        self._restaurar_botoes_lote()
        self.lbl_transcribe_status.configure(text="Falha na transcrição.")
        messagebox.showerror("Erro", f"Falha na transcrição:\n{erro}")

    def _excluir_audio_selecionado(self):
        selecao = [s for s in self.tree_audios.selection() if not s.startswith("sep_")]
        if not selecao:
            messagebox.showwarning("Atenção", "Selecione um ou mais arquivos de áudio válidos para excluir.")
            return

        gravacoes_dir, _ = self.recorder.obter_diretorios()
        caminhos = [gravacoes_dir / nome for nome in selecao]

        if self.recorder.is_recording and self.recorder.current_audio_file:
            if any(c.name == self.recorder.current_audio_file.name for c in caminhos):
                messagebox.showerror("Bloqueado", "Um dos arquivos selecionados está sendo gravado no momento. Pare a gravação antes de excluir.")
                return

        qtd = len(caminhos)
        msg_conf = f"Deseja remover o arquivo '{selecao[0]}'?" if qtd == 1 else f"Deseja remover os {qtd} arquivos de áudio selecionados?"
        confirma = messagebox.askyesno(
            "Mover para Lixeira",
            f"{msg_conf}\n\nConforme o protocolo de segurança, todos serão preservados na pasta lixeira/."
        )
        if not confirma:
            return

        removidos = 0
        for c in caminhos:
            if self.playing_file and self.playing_file.name == c.name:
                self._parar_reproducao()
            dest = mover_para_lixeira(c)
            if dest:
                removidos += 1

        self._atualizar_lista_audios()
        if removidos > 0:
            messagebox.showinfo("Lixeira", f"{removidos} arquivo(s) movido(s) com segurança para a lixeira/.")

    # --- Gestao de Transcricoes Markdown ---
    def _atualizar_lista_transcricoes(self):
        for item in self.tree_md.get_children():
            self.tree_md.delete(item)

        _, transcricoes_dir = self.recorder.obter_diretorios()
        if not transcricoes_dir.exists():
            return

        ultimo_dia_md = None
        dias_inseridos_md = set()
        arquivos_md = sorted(
            transcricoes_dir.glob("*.md"),
            key=lambda x: (self._extrair_data_dia_arquivo(x), x.stat().st_mtime),
            reverse=True
        )
        for p in arquivos_md:
            stat = p.stat()
            data_dia = self._extrair_data_dia_arquivo(p)

            # Insere linha divisoria visual entre cada dia de transcricao
            sep_id = f"sep_md_{data_dia.strftime('%Y%m%d')}"
            if data_dia != ultimo_dia_md:
                ultimo_dia_md = data_dia
                if sep_id not in dias_inseridos_md and not self.tree_md.exists(sep_id):
                    dias_inseridos_md.add(sep_id)
                    dia_fmt = self._formatar_dia_divisor(data_dia)
                    self.tree_md.insert(
                        "", "end",
                        iid=sep_id,
                        values=(f"── 📅 {dia_fmt} ────────────────────", "───", "─────"),
                        tags=("separador_dia",)
                    )

            lines = 0
            with open(p, "r", encoding="utf-8", errors="ignore") as f:
                lines = sum(1 for _ in f)

            mtime = datetime.datetime.fromtimestamp(stat.st_mtime).strftime("%d/%m %H:%M")
            self.tree_md.insert("", "end", iid=p.name, values=(p.name, lines, mtime))

    def _ao_selecionar_md(self, event=None):
        selecao = [s for s in self.tree_md.selection() if not s.startswith("sep_")]
        if not selecao:
            return

        nome_md = selecao[0]
        _, transcricoes_dir = self.recorder.obter_diretorios()
        caminho = transcricoes_dir / nome_md
        if not caminho.exists():
            return

        self.current_selected_md = caminho
        self.lbl_editing_file.configure(text=f"Editando: {nome_md}")
        self.btn_salvar_md.configure(state="normal")

        try:
            with open(caminho, "r", encoding="utf-8") as f:
                conteudo = f.read()
            self.txt_md_editor.delete("1.0", "end")
            self.txt_md_editor.insert("end", conteudo)
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível ler o arquivo Markdown:\n{e}")

    def _salvar_md_atual(self):
        if not self.current_selected_md or not self.current_selected_md.exists():
            return

        texto = self.txt_md_editor.get("1.0", "end-1c")
        texto = texto.replace("\u2014", " - ").replace("\u2013", " - ")

        try:
            with open(self.current_selected_md, "w", encoding="utf-8") as f:
                f.write(texto)
            self._atualizar_lista_transcricoes()
            messagebox.showinfo("Salvo", f"Alterações salvas com sucesso em:\n{self.current_selected_md.name}")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao salvar arquivo:\n{e}")

    def _abrir_md_externo(self):
        if not self.current_selected_md or not self.current_selected_md.exists():
            messagebox.showwarning("Atenção", "Selecione uma transcrição para abrir externamente.")
            return
        try:
            os.startfile(str(self.current_selected_md))
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível abrir o arquivo:\n{e}")

    def _abrir_local_audio(self):
        gravacoes_dir, _ = self.recorder.obter_diretorios()
        selecao = self.tree_audios.selection()
        if selecao:
            nome_arquivo = selecao[0]
            caminho = gravacoes_dir / nome_arquivo
            if caminho.exists():
                abrir_no_explorer(caminho)
                return
        abrir_no_explorer(gravacoes_dir)

    def _abrir_local_md(self):
        _, transcricoes_dir = self.recorder.obter_diretorios()
        selecao = self.tree_md.selection()
        if selecao:
            nome_md = selecao[0]
            caminho = transcricoes_dir / nome_md
            if caminho.exists():
                abrir_no_explorer(caminho)
                return
        if self.current_selected_md and self.current_selected_md.exists():
            abrir_no_explorer(self.current_selected_md)
            return
        abrir_no_explorer(transcricoes_dir)

    def _excluir_md_selecionado(self):
        selecao = [s for s in self.tree_md.selection() if not s.startswith("sep_")]
        if not selecao:
            messagebox.showwarning("Atenção", "Selecione um ou mais arquivos Markdown válidos para excluir.")
            return

        _, transcricoes_dir = self.recorder.obter_diretorios()
        caminhos = [transcricoes_dir / nome for nome in selecao]

        if self.recorder.is_recording and self.recorder.current_md_file:
            if any(c.name == self.recorder.current_md_file.name for c in caminhos):
                messagebox.showerror("Bloqueado", "Um dos arquivos selecionados está sendo escrito no momento. Pare a gravação antes de excluir.")
                return

        qtd = len(caminhos)
        msg_conf = f"Deseja remover o arquivo '{selecao[0]}'?" if qtd == 1 else f"Deseja remover os {qtd} arquivos Markdown selecionados?"
        confirma = messagebox.askyesno(
            "Mover para Lixeira",
            f"{msg_conf}\n\nConforme o protocolo, todos serão arquivados na pasta lixeira/."
        )
        if not confirma:
            return

        removidos = 0
        for c in caminhos:
            if self.current_selected_md and self.current_selected_md.name == c.name:
                self.current_selected_md = None
                self.lbl_editing_file.configure(text="Nenhum arquivo selecionado para edição")
                self.btn_salvar_md.configure(state="disabled")
                self.txt_md_editor.delete("1.0", "end")
            dest = mover_para_lixeira(c)
            if dest:
                removidos += 1

        self._atualizar_lista_transcricoes()
        if removidos > 0:
            messagebox.showinfo("Lixeira", f"{removidos} arquivo(s) Markdown movido(s) com segurança para a lixeira/.")

    # --- Utilitarios e Encerramento ---
    def _formatar_segundos(self, segundos):
        s = int(segundos or 0)
        h = s // 3600
        m = (s % 3600) // 60
        sec = s % 60
        return f"{h:02d}:{m:02d}:{sec:02d}"

    def _ao_fechar(self):
        """Ao fechar a janela, encerra com seguranca os processos."""
        if self.recorder.is_recording:
            self.recorder._salvar_estado(gravando=True)
            self.recorder.parar_gravacao()

        self.recorder.encerrar()
        self.transcriber.stop_worker()
        try:
            pygame.mixer.quit()
        except Exception:
            pass
        self.destroy()


def main():
    app = DesktopApp()
    app.mainloop()


if __name__ == "__main__":
    main()
