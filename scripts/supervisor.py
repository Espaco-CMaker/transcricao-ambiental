"""Supervisor e Guardiao da Aplicacao Desktop (Auto-Recovery & 24/7 Resilience).
Monitora a interface grafica nativa local (scripts/gui_app.py).
Caso ocorra qualquer queda, crash ou interrupcao nao planejada, o supervisor
reinicia o aplicativo automaticamente para garantir gravacao continua ininterrupta.
"""

import os
import sys
import time
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

def main():
    print("=" * 68)
    print("  SUPERVISOR DA APLICACAO DESKTOP DE GRAVACAO CONTINUA (24/7)")
    print("=" * 68)
    print(f"Diretorio base: {BASE_DIR}")
    print("Pressione Ctrl+C nesta janela para encerrar o supervisor.\n")

    restarts = 0
    while True:
        cmd = [sys.executable, str(BASE_DIR / "scripts" / "gui_app.py")]
        print(f"[SUPERVISOR] Executando aplicacao desktop (Execucao #{restarts + 1})...")
        start_time = time.time()

        try:
            process = subprocess.Popen(cmd, cwd=str(BASE_DIR))
            ret_code = process.wait()

            duration = time.time() - start_time
            print(f"[SUPERVISOR] Processo encerrou com codigo {ret_code} apos {int(duration)} segundos.")

            # Se encerrou com codigo 0 e durou mais de 5 segundos por solicitacao voluntaria de fechamento pelo usuario:
            # Se o usuario fechou a janela mas o auto_record ou supervisor 24/7 estiver ativo,
            # ele pode decidir reiniciar ou perguntar. Se ret_code != 0 (crash), reinicia imediatamente.
            if ret_code != 0:
                restarts += 1
                print("[SUPERVISOR] Queda inesperada detectada! Reiniciando aplicativo em 3 segundos...")
                time.sleep(3.0)
            else:
                # Encerramento voluntario pelo usuario (clicou no X da janela)
                print("[SUPERVISOR] Aplicacao fechada normalmente pelo usuario.")
                break

        except KeyboardInterrupt:
            print("\n[SUPERVISOR] Encerrando supervisor por solicitacao do usuario...")
            if 'process' in locals() and process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=4)
                except subprocess.TimeoutExpired:
                    process.kill()
            print("[SUPERVISOR] Finalizado.")
            break
        except Exception as e:
            print(f"[SUPERVISOR] Erro no supervisor: {e}")
            time.sleep(3.0)

if __name__ == "__main__":
    main()
