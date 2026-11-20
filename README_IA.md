# Transcricao Ambiental de Sala (README_IA.md)
> Versao do Indice: `v1.0.43` | Ultima atualizacao: 2026-11-20 13:20

## TL;DR Executivo
Sistema nativo em Python 100% local e desktop (estritamente sem servidor, sem portas HTTP e sem navegador web), utilizando CustomTkinter e Pygame para gravacao continua de audio de sala durante todo o dia e geracao automatica de transcricoes em Markdown (.md). Desenvolvido com SoundDevice, SoundFile e Faster-Whisper (CUDA/CPU sem dependencia pesada de PyTorch). Na versao `v1.0.43`, elaborou o documento canonico de apoio cadastral ao Hub de Projetos CMaker (`EmDesenvolvimento/formulario_hub_projetos_v1.0.0.md`), mapeando 100% dos campos, identificadores e opcoes do formulario administrativo (`admin/projetos/novo`), fornecendo dados tecnicos, resumo de 198 caracteres, descricao estruturada, marcos, tags e parecer de maturidade prontos para copia e preenchimento. Na versao `v1.0.42`, unificou a acao de transcricao em um unico botao inteligente `⚡ Transcrever`, removendo o botao separado de lote (`⚡ Transcrever em Lote`). Na versao `v1.0.41`, refinou o osciloscopio ao vivo dos ultimos 5 segundos para tracos verticais ultra-finos de 1 pixel (`width=1`) com passo uniforme de 3 pixels (`bar_step=3`), espacamento limpo de 2 pixels entre linhas, oscilacao vertical simetrica em torno do horizonte central (`cy`), eliminou borroes e textos sobrepostos, removeu caixas de selecao e removeu opcoes de atas.

## Regras Inegociaveis (Hard Constraints)
1. **Sem Servidor:** O sistema opera como aplicacao desktop nativa pura (zero servidor web, zero HTTP, zero portas de rede).
2. **Integracao com Explorer:** As guias de Gravacoes (.wav) e Transcricoes (.md) possuem botoes dedicados para abrir diretamente a pasta de destino no Windows Explorer com o arquivo selecionado em foco.
3. **Ciclo de Vida Documental:** Documentos e relatorios analiticos em elaboracao ou refinamento residem obrigatoriamente na pasta `EmDesenvolvimento/`, migrando para `Docs/` apenas apos aprovacao formal.
4. **Fallback Automatico de Aceleracao:** Se a GPU NVIDIA for detectada mas o sistema operacional nao possuir os binarios CUDA (ex.: `cublas64_12.dll`), o sistema realiza fallback automatico e instantaneo para CPU (`int8`), garantindo que nenhuma transcricao congele em 0% ou gere arquivos em branco.
5. **Reativacao Imediata de Transcricao:** O cancelamento de transcricao reativa instantaneamente o botao "⚡ Transcrever" (`state="normal"`), invalida sessoes em background e descarta travas modais para permitir novas operacoes imediatas.
6. **Cancelamento sob Demanda:** Permite interromper/cancelar a qualquer instante a transcricao de um audio em execucao atraves do botao "✖ Cancelar Transcricao", preservando o estado da aplicacao de modo responsivo.
7. **Identificacao de Versao:** A versao atual (`v1.0.43`) e informada de modo claro e visivel no topo, na barra de titulo e no rodape da aplicacao desktop.
8. **Progresso Percentual Real (%):** Durante a transcricao de audio completo, a interface exibe barra visual e porcentagem em tempo real (`0.0%` a `100.0%`) com base em tempo decodificado/total.
9. **Listagem Completa de Microfones:** Exibe todos os microfones e entradas disponiveis no sistema (MME, DirectSound, WASAPI, WDM-KS) sem abrir streams concorrentes que travam drivers de audio e Bluetooth no Windows.
10. **Executavel Portatil:** A distribuicao em `dist/TranscricaoAmbiental` e o arquivo `dist/TranscricaoAmbiental_Portatil.zip` contem todos os binarios e o modelo offline, funcionando em qualquer PC com Windows sem internet e sem Python.
11. **Pontuacao Proibida:** Terminantemente vedado o uso de travessao (em dash, U+2014) e meia-risca (en dash, U+2013). Usar dois-pontos, virgula ou hifen simples (-).
12. **Terminologia:** Usar "estudante", estritamente vedada a utilizacao de termos proibidos correlatos.
13. **Retencao Segura (Lixeira):** Proibido hard delete (`rm`, `os.remove`). Qualquer exclusao de audio ou MD deve ser movida para `lixeira/` via `scripts/lixeira.py`.
14. **Localizacao de Scripts:** Todos os modulos executaveis residem compulsoriamente em `scripts/`.
15. **Nomes de Arquivos WAV e Transcricoes:** Formato compulsorio estrito para gravacoes: `gravando_AAAA-MM-DD_HH-MM-SS.wav` (arquivos de audio `.wav` NUNCA sao renomeados). Apenas os arquivos Markdown (.md) sao renomeados contextualmente: transcricoes adotam `AAAA-MM-DD_HH-MM-SS_Titulo_transcricao.md`.
16. **Horarios Reais em Transcricoes:** A data e hora do arquivo de audio sao tomadas como referencia do encerramento da gravacao. A hora de inicio e compulsoriamente calculada subtraindo a duracao do arquivo da hora final, ajustando todos os carimbos temporais de falas da transcricao para o horario real do relogio (`HH:MM:SS`), eliminando tempos puramente relativos baseados em `0:00:00`.
17. **Inicializacao Passiva sem Gravacao Automatica:** O aplicativo abre sempre em estado de espera (sem iniciar gravacao automaticamente), com `auto_record` padronizado em `False`. A gravacao somente e disparada sob comando voluntario do operador no botao "Iniciar Gravacao".
18. **Sincronismo de Playhead e Busca na Forma de Onda:** O clique na forma de onda sonora expandida (Canvas) posiciona instantaneamente o playhead (linha vermelha) nas coordenadas clicadas, ajusta o slider de progresso, atualiza o tempo decorrido no rotulo de tempo e sincroniza a contagem continua de reproducao com base em `player_start_sec + (get_pos() / 1000.0)`.
19. **Grafico de Som em Tempo Real (Linhas Ultra-Finas de 1px com Passo de 3px, Fundo #020617):** O osciloscopio ao vivo utiliza linhas finas de 1 pixel (`width=1`, passo de 3px) rasterizadas com Pillow/PIL, com oscilacao simetrica centrada em `cy`, enquadramento sutil superior/inferior em `#1e293b` e fundo profundo `#020617`, eliminando agrupamento denso, borroes ou sobreposicoes de texto e proporcionando contornos nitidos e elegantes.
20. **Linhas Divisorias Cronologicas por Dia:** As tabelas de gravacoes (.wav) e transcricoes (.md) organizam os arquivos agrupados por dia atraves de separadores visuais elegantes (`sep_dia_...`), indicando data e dia da semana, com filtros automaticos para operacoes em lote, Ctrl+A e reproducao.
21. **Botao Unico de Transcricao Contextual (`⚡ Transcrever`):** A barra de ferramentas possui um unico botao de transcricao. Ao ser clicado, processa estritamente os arquivos atualmente selecionados na tabela (seja 1 arquivo ou multiplos selecionados via Ctrl, Shift ou Ctrl+A), eliminando redundancia de botoes.
22. **Remocao do Modulo de Atas:** O sistema concentra-se exclusivamente na transcricao textual de alta precisao em Markdown (.md). Toda interface de geracao de ata, botoes e configuracoes automaticas de ata foram descontinuados e removidos da aplicacao.

## Mapa Canonico de Arquivos e Indice de Linhas (Token-Saving Map)
- [EmDesenvolvimento/formulario_hub_projetos_v1.0.0.md](file:///e:/IAGenMaster/2026/CMaker/Projetos/11-TranscricaoAmbiental/EmDesenvolvimento/formulario_hub_projetos_v1.0.0.md) (v1.0.0, ~270 linhas): Documento canônico com dados prontos para copiar e preencher no formulário do Hub de Projetos CMaker (`admin/projetos/novo`).
- [scripts/transcriber.py](file:///e:/IAGenMaster/2026/CMaker/Projetos/11-TranscricaoAmbiental/scripts/transcriber.py) (v1.0.26, ~512 linhas)
  - L1-L60: Imports, configuracoes de modelo e funcao `calcular_horarios_arquivo`.
  - L61-L150: Funcao `ajustar_tempos_transcricao` (converte marcadores relativos para horarios reais de relogio).
  - L151-L320: Motor `TranscriberEngine`, warm-up, fallback automatico para CPU int8 e VAD.
  - L321-L512: `transcribe_full_file` com timestamps reais (`HH:MM:SS`), cancelamento sob demanda e metadados no cabecalho.
- [scripts/gerador_ata.py](file:///e:/IAGenMaster/2026/CMaker/Projetos/11-TranscricaoAmbiental/scripts/gerador_ata.py) (v1.0.26, ~369 linhas)
  - L1-L70: Analise semantica da transcricao, extracao contextual de topicos, agenda, deliberacoes.
  - L71-L190: `analisar_segmentos_transcricao` com suporte a horarios reais (`HH:MM:SS`), cruzamento de meia-noite e blocos cronologicos.
  - L191-L245: `detectar_local_ambiente` (certeza indubitavel ou em branco) e extracao de prefixo temporal.
  - L246-L369: `gerar_ata_de_transcricao` com ajuste automatico de transcricao, prefixo `ATA_`, data da sessao real e local estrito.
- [scripts/renomeador.py](file:///e:/IAGenMaster/2026/CMaker/Projetos/11-TranscricaoAmbiental/scripts/renomeador.py) (v1.0.29, ~106 linhas)
  - L1-L35: Sanitizacao de slugs contextuais e deteccao de prefixo temporal (`AAAA-MM-DD_HH-MM-SS`).
  - L36-L106: Funcao `renomear_trio_arquivos` com renomeacao exclusiva de arquivos Markdown (.md), mantendo arquivos de audio (.wav) 100% inalterados.
- [scripts/waveform_generator.py](file:///e:/IAGenMaster/2026/CMaker/Projetos/11-TranscricaoAmbiental/scripts/waveform_generator.py) (v1.0.21, ~190 linhas)
  - L1-L40: Extracao otimizada de envelope sonoro, calculo de picos, RMS medio e atividade sonora com cache em memoria.
  - L41-L150: Gerador de miniaturas visuais (sparklines PhotoImage) e gerador de onda em texto Unicode (`gerar_onda_texto`) para tabela.
- [scripts/gui_app.py](file:///e:/IAGenMaster/2026/CMaker/Projetos/11-TranscricaoAmbiental/scripts/gui_app.py) (v1.0.42, ~2275 linhas)
  - L1-L64: Imports, numpy, PIL (Image, ImageDraw, ImageTk), logger, renomeador e constante `APP_VERSION = "v1.0.42"`.
  - L65-L85: Funcao auxiliar `abrir_no_explorer`.
  - L86-L230: Janela principal CustomTkinter, geracao de icones dinamicos para a barra de tarefas e controles de audio.
  - L231-L450: Badge de versao `v1.0.42`, botao Mudo Temporario, checkbox de auto-inicio desmarcada por padrao, seletor de ganho do osciloscopio (`1x`, `2x`, `3x`, `5x`) e canvas de 76px (`canvas_live_wave`).
  - L451-L670: Aba de gravacoes com `tree_audios` em selecao nativa multi-linha, botao unico `⚡ Transcrever`, `🗑️ Excluir Áudio` e `📂 Abrir Local`.
  - L671-L750: Painel detalhado de som capturado com Canvas interativo, badges de pico/RMS/atividade e marcadores de tempo.
  - L751-L860: Aba de transcricoes com `tree_md`, configuracao de tag `separador_dia`, botoes de atualizacao, local e exclusao de MDs.
  - L861-L990: Aba de configuracoes com preferencias de transcricao automatica, renomeacao contextual e painel de auditoria/logs.
  - L991-L1330: Pipeline automatico, medidor VU/dB continuo, alternancia de mute, gravacao e loop de interface resiliente (50ms).
  - L1331-L1430: Renderizador rasterizado de alta fidelidade com tracos verticais ultra-finos de 1px com passo de 3px (`_atualizar_grafico_tempo_real`), oscilacao simetrica em torno de `cy`, linhas de enquadramento e fundo `#020617`.
  - L1431-L1550: Funcoes `_extrair_data_dia_arquivo`, `_formatar_dia_divisor`, `_atualizar_lista_audios` com ordenacao cronologica decrescente e prevencao de duplicatas.
  - L1551-L1980: Gestao de audios, reproducao sincronizada com playhead, motor de transcricao unificado `_transcrever_audio_selecionado` para item individual ou multiplos itens selecionados.
  - L1981-L2275: Gestao de transcricoes Markdown (`_atualizar_lista_transcricoes`), editor de texto integrado e encerramento seguro.
- [scripts/recorder.py](file:///e:/IAGenMaster/2026/CMaker/Projetos/11-TranscricaoAmbiental/scripts/recorder.py) (v1.0.30, ~664 linhas)
  - L1-L80: Configuracoes persistentes com `auto_record: False` por padrao, espaco em disco e funcao `validar_arquivo_wav`.
  - L81-L220: Motor `AudioRecorder` com ring buffer continuo de 5 segundos (`live_buffer`), suporte a `alternar_mute` e VU/dB ativo continuo.
  - L221-L340: Metodos `_adicionar_ao_live_buffer` e `obter_amostras_tempo_real` (ordem cronologica do mais antigo ao mais recente).
  - L341-L580: Callback de audio com escrita PCM direta em disco, medicao RMS/dB e alimentacao ininterrupta do buffer de 5s.
  - L581-L664: Persistencia e recuperacao de estado segura sem disparar gravacao automatica indevida.
- [scripts/testar_melhorias.py](file:///e:/IAGenMaster/2026/CMaker/Projetos/11-TranscricaoAmbiental/scripts/testar_melhorias.py) (v1.0.30, ~227 linhas)
  - L1-L45: Setup de testes unitarios de regressao e suite de teste de configuracao e mute.
  - L46-L227: Bateria completa de 8 suites de testes automatizados: teste de nomes de arquivo com preservacao estrita de WAVs, local em branco na ata, horarios reais, sincronismo de seek/playhead e buffer de som em tempo real dos ultimos 5 segundos.
- [scripts/gerar_executavel.py](file:///e:/IAGenMaster/2026/CMaker/Projetos/11-TranscricaoAmbiental/scripts/gerar_executavel.py) (v1.0.15, ~102 linhas)
  - L1-L102: Pipeline automatizado de compilacao com exclusao de torch e empacotamento standalone.
- [scripts/lixeira.py](file:///e:/IAGenMaster/2026/CMaker/Projetos/11-TranscricaoAmbiental/scripts/lixeira.py) (v1.0.15, ~48 linhas)
  - L1-L48: Funcao `mover_para_lixeira` com retencao segura de versoes e arquivos.
- [iniciar_sistema.bat](file:///e:/IAGenMaster/2026/CMaker/Projetos/11-TranscricaoAmbiental/iniciar_sistema.bat) (v1.0.15, ~22 linhas)
  - L1-L22: Launcher de um clique com loop de recuperacao sem bloco de parenteses aninhado.
