"""Modulo de Auditoria e Logs Estruturados para o Gravador de Sons Ambiente.
Mantem arquivo persistente com rotacao em logs/sistema.log e fila em memoria para a GUI.
"""

import os
import sys
import time
import queue
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict

BASE_DIR = Path(__file__).resolve().parent.parent
LOGS_DIR = BASE_DIR / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOGS_DIR / "sistema.log"


class AuditLogger:
    _instance: Optional["AuditLogger"] = None

    def __init__(self):
        self.memory_records: list[Dict] = []
        self.max_memory_records = 1000
        self.queue: queue.Queue = queue.Queue()

        # Configuracao do logger padrao com RotatingFileHandler (max 5 MB, ate 3 backups)
        self.logger = logging.getLogger("GravadorAmbiente")
        self.logger.setLevel(logging.INFO)
        self.logger.propagate = False

        if not self.logger.handlers:
            handler = RotatingFileHandler(
                str(LOG_FILE),
                maxBytes=5 * 1024 * 1024,
                backupCount=3,
                encoding="utf-8"
            )
            formatter = logging.Formatter(
                "%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    @classmethod
    def get_instance(cls) -> "AuditLogger":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def log(self, level: str, modulo: str, tarefa: str, mensagem: str):
        """Registra um evento de auditoria no arquivo e na memoria para a interface."""
        level_upper = level.upper()
        agora = datetime.now()
        timestamp_str = agora.strftime("%Y-%m-%d %H:%M:%S")

        registro = {
            "timestamp": timestamp_str,
            "level": level_upper,
            "modulo": modulo,
            "tarefa": tarefa,
            "mensagem": mensagem
        }

        # Formata para arquivo
        texto_log = f"[{modulo}] [{tarefa}] {mensagem}"
        if level_upper == "ERROR":
            self.logger.error(texto_log)
        elif level_upper == "WARN" or level_upper == "WARNING":
            self.logger.warning(texto_log)
        else:
            self.logger.info(texto_log)

        # Adiciona na memoria
        self.memory_records.append(registro)
        if len(self.memory_records) > self.max_memory_records:
            self.memory_records.pop(0)

        self.queue.put(registro)

    def info(self, modulo: str, tarefa: str, mensagem: str):
        self.log("INFO", modulo, tarefa, mensagem)

    def warn(self, modulo: str, tarefa: str, mensagem: str):
        self.log("WARN", modulo, tarefa, mensagem)

    def error(self, modulo: str, tarefa: str, mensagem: str):
        self.log("ERROR", modulo, tarefa, mensagem)

    def get_recent_records(self, limit: int = 200, level_filter: Optional[str] = None) -> List[Dict]:
        """Retorna registros recentes com filtro opcional por nivel."""
        records = self.memory_records
        if level_filter and level_filter != "TODOS":
            records = [r for r in records if r["level"] == level_filter.upper()]
        return records[-limit:]

    def exportar_logs(self, destino: Path) -> bool:
        """Exporta os logs persistidos para um arquivo externo selecionado."""
        try:
            if LOG_FILE.exists():
                with open(LOG_FILE, "r", encoding="utf-8") as f_in, open(destino, "w", encoding="utf-8") as f_out:
                    f_out.write(f"# Exportacao de Logs de Auditoria - {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n")
                    f_out.write(f_in.read())
                return True
        except Exception as e:
            print(f"[LOGGER] Erro ao exportar logs: {e}")
        return False


def get_logger() -> AuditLogger:
    return AuditLogger.get_instance()

