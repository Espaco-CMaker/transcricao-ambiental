# Transcrição Ambiental de Sala: Aplicação Desktop 100% Local (Sem Servidor)
> Versão do Projeto: `v1.0.43` | Atualizado em: 20/11/2026

Aplicação em Python **100% Desktop nativa e local, operando totalmente sem servidor**, sem portas de rede e sem navegador web. Desenvolvida com CustomTkinter, SoundDevice, SoundFile, Faster-Whisper e Pygame para gravação contínua do áudio de uma sala durante o dia todo, geração automática de transcrições em arquivos Markdown (.md), reprodução sonora local e editor de texto. Na versão **`v1.0.43`**, o sistema implementa: **documentação canônica de cadastro no Hub de Projetos CMaker**:
- **Documento Canônico de Preenchimento do Hub de Projetos (`v1.0.43`):** Elaboração de guia completo em [EmDesenvolvimento/formulario_hub_projetos_v1.0.0.md](file:///e:/IAGenMaster/2026/CMaker/Projetos/11-TranscricaoAmbiental/EmDesenvolvimento/formulario_hub_projetos_v1.0.0.md) mapeando 100% dos campos do formulário administrativo (`admin/projetos/novo`) do Hub de Projetos CMaker (`https://cmaker.com.br/projetos/hub/`). Inclui textos prontos para cópia com resumo executivo de 198 caracteres, descrição aprofundada da solução e metodologia maker, equipe, marcos cronológicos, tags, tecnologias, diretrizes de fotos e parecer técnico de maturidade com nota 10.0.
- **Botão Único de Transcrição Contextual (`v1.0.42`):** Remoção do botão redundante `⚡ Transcrever em Lote`. A barra de ferramentas agora conta exclusivamente com o botão **`⚡ Transcrever`**, que atua de forma direta sobre os itens selecionados na lista:
  - Se nenhum áudio estiver selecionado, exibe aviso amigável orientando o operador a selecionar;
  - Se 1 único áudio estiver selecionado, dispara a transcrição individual com barra de progresso em tempo real;
  - Se múltiplos arquivos estiverem selecionados (via Shift+clique, Ctrl+clique ou Ctrl+A), solicita confirmação e transcreve automaticamente toda a seleção em lote sequencial com Whisper.
- **Gráfico de Som ao Vivo com Traços de 1px e Passo de 3px (`v1.0.41`):** Refinamento completo da renderização do osciloscópio ao vivo dos últimos 5 segundos: traço vertical de 1 pixel (`width=1`) com passo uniforme de 3 pixels (`bar_step=3`), proporcionando um vão limpo de 2 pixels entre cada linha. A oscilação vertical é perfeitamente simétrica em torno do horizonte central (`cy`), eliminando borroes, pontos de grade e sobreposições de texto para um visual minimalista e de alta fidelidade idêntico à referência de Voice Memo / SoundCloud.
- **Seleção Nativa Multi-Linha para Transcrição em Lote (`v1.0.41`):** Remoção da coluna de caixas de seleção (`☑`/`☐`) e retorno ao padrão nativo de seleção de linhas (clique simples, Shift+clique, Ctrl+clique e Ctrl+A).
- **Remoção das Opções e Módulo de Atas (`v1.0.41`):** Foco estrito na transcrição em Markdown (.md). Removidos todos os botões de ata da aba de transcrições, a opção de geração automática de ata nas configurações e o diálogo confirmatório de ata durante o processamento em lote.
- **Resolução de Inicialização no Terminal (`v1.0.41`):** Correção do ciclo de inicialização gráfica, prevenindo erros de atributos e encerrando de forma definitiva reinicializações cíclicas no terminal com `iniciar_sistema.bat`.
- **Conversão de Áudios Legados (.m4a para .wav) (`v1.0.41`):** Conversão automática dos áudios existentes no formato M4A para WAV PCM 16kHz mono com retenção segura em `lixeira/`.
- **Gráfico de Som ao Vivo com Linhas Ultra-Finas (`v1.0.40`):** Refinamento completo da renderização do osciloscópio ao vivo dos últimos 5 segundos: traço vertical de 1 pixel (`width=1`) com passo uniforme de 4 pixels (`bar_step=4`), proporcionando um vão limpo de 3 pixels entre cada linha. A oscilação vertical agora é perfeitamente simétrica em torno do horizonte central (`cy`), eliminando assimetrias pontiagudas e espelhando fielmente o padrão estético de Voice Memo da referência visual. O ganho de amplitude foi recalibrado com resposta dinâmica natural para fala humana, repouso discreto de 2px no silêncio, enquadramento sutil superior/inferior em `#1e293b` e fundo profundo `#020617`.
- **Marcação e Transcrição em Lote sob Demanda (`v1.0.39`):** Implementada coluna dedicada com caixas de seleção (`☑`/`☐`) na tabela de gravações (`tree_audios`). O operador pode marcar arquivos individuais clicando diretamente na caixa de seleção, no cabeçalho ou pressionando a tecla `<espaço>`. A barra de ferramentas agora conta com botões dedicados de seleção rápida: `⏳ Só Pendentes` (marca com 1 clique apenas os áudios que ainda não possuem transcrição `.md`), `☑ Todos` (marca todos) e `☐ Nenhum` (limpa as marcações). O botão de lote atualiza dinamicamente seu rótulo e contador (`⚡ Transcrever Marcados (N)`) e processa estritamente os arquivos assinalados, com ordenação cronológica decrescente robusta por data e horário.
- **Linhas Mais Finas no Gráfico de Som e Separadores (`v1.0.38`):** O traçado do osciloscópio ao vivo foi refinado para linhas verticais ultra-finas de 1 pixel (`width=1`) com passo de 3 pixels (`bar_step=3`), permitindo renderizar mais de 500 linhas individuais por janela de 5 segundos com máxima definição analógica e zero peso visual. Nas tabelas de arquivos (`tree_audios` e `tree_md`), as linhas divisórias de dia foram suavizadas com traços minimalistas e discretos (`── 📅 DD/MM/AAAA (Dia) ──`).
- **Linhas Divisórias Cronológicas por Dia (`v1.0.37`):** As tabelas de visualização de arquivos (`tree_audios` e `tree_md`) agora agrupam os arquivos por dia de gravação através de separadores visuais elegantes (`sep_dia_...`), com fundo escuro `#1e293b` e texto ciano `#38bdf8`. Todos os atalhos e comandos (Ctrl+A, seleção em lote, reprodução, transcrição e exclusão) foram blindados para operar exclusivamente sobre os arquivos reais, ignorando as linhas divisórias.
- **Renderização Cristalina Pixel-Perfect com PIL (`v1.0.36`):** Eliminação completa do aspecto embaçado ou borrado gerado pelo antialiasing vetorial do Windows GDI/Tkinter. O frame do osciloscópio é renderizado em memória com Pillow/PIL com alinhamento estrito a coordenadas inteiras (`draw.rounded_rectangle` com largura de 3px, passo de 5px e raio de 1px), sendo transferido diretamente para o Canvas como `PhotoImage` via BitBlt nativo, garantindo bordas perfeitamente nítidas e recorte impecável em qualquer resolução de tela.
- **Barras Verticais Arredondadas com Espaçamento Uniforme (`v1.0.35`):** Renderização fiel da forma de onda em colunas verticais discretas com pontas em cápsula arredondada (`width=2`, `capstyle="round"`, passo de 4px), preservando o espaçamento limpo entre as barras, a assimetria acústica real entre as cristas superiores e vales inferiores, cápsulas mínimas de 3px em repouso durante o silêncio e expansão expressiva em azul `#38bdf8` durante a fala (idêntico ao padrão oficial de Voice Memo).
- **Alta Densidade do Gráfico de Som ao Vivo (`v1.0.34`):** Resolução horizontal expandida para até 900 bins de amostragem (1 bin a cada ~1.3px na tela), traçado contínuo denso unindo cristas positivas e vales negativos de cada fatia temporal e ganho de amplitude perceptual calibrado (`mult = (ganho**0.6) * 1.85`), proporcionando textura encorpada, visual de osciloscópio de alta fidelidade e zero preenchimento sólido sob o traço.
- **Forma de Onda com Oscilação Real sem Preenchimento (`v1.0.33`):** Substituição do envelope de polígono fechado preenchido (`create_polygon` com `fill`) pela renderização da forma de onda osciloscópica contínua: o traço acústico oscila dinamicamente entre as cristas positivas e os vales negativos reais da fala humana através de uma linha contínua de 1.5px (`create_line`), eliminando qualquer bloco opaco e exibindo a vibração natural do som, as pausas de silêncio na linha central zero e a dinâmica sonora real captada pelo microfone.
- **Ampliação de Amplitude e Ganho do Gráfico ao Vivo (`v1.0.32`):** Aumento da altura física do canvas do osciloscópio de 46px para 76px (+65% de resolução vertical), implementação de curva de ganho perceptual não-linear com compressão de raiz quadrada (`math.sqrt(p) * mult`) para proporcionar visualização nítida e ampla da fala humana em ambiente de sala, e adição de um seletor interativo de ganho (`CTkSegmentedButton` com opções `["1x", "2x", "3x", "5x"]`, padrão `3x`) integrado diretamente à barra de cabeçalho do osciloscópio.
- **Estabilidade do Loop de Interface e Gravação (`v1.0.31`):** Adicionado `import numpy as np` em `scripts/gui_app.py` e encapsulado o renderizador do gráfico em tempo real em bloco `try...except`, prevenindo que falhas em chamadas de desenho congelem o temporizador, o medidor de decibéis ou interrompam o ciclo contínuo de gravação.
- **Gráfico de Som em Tempo Real dos Últimos 5 Segundos (`v1.0.30`):** Osciloscópio dinâmico contínuo integrado ao painel superior de controle (`canvas_live_wave`), exibindo as ondas sonoras captadas pelo microfone fluindo da direita (`Agora / 0s`) para a esquerda (`-5.0s`), com envelope espelhado neon, marcadores de tempo de 1 em 1 segundo e status dinâmico de decibéis e mudo temporário.
- **Renomeação Restrita aos Arquivos .MD (`v1.0.29`):** A renomeação automática por temas e títulos contextuais atua estritamente sobre as transcrições (`AAAA-MM-DD_HH-MM-SS_Titulo_transcricao.md`) e atas estruturadas (`ATA_AAAA-MM-DD_HH-MM-SS_Titulo.md`). Os arquivos de áudio `.wav` permanecem 100% inalterados com a identificação original (`gravando_AAAA-MM-DD_HH-MM-SS.wav`), prevenindo concorrência de handles, reabertura de mixer e preservando o vínculo temporal direto.
- **Sincronismo de Playhead e Timer na Forma de Onda (`v1.0.28`):** Ao clicar com o mouse em qualquer ponto do gráfico de ondas sonoras no Canvas, o áudio salta imediatamente para a posição temporal exata, a linha vermelha do cursor (*playhead*) salta instantaneamente para as coordenadas clicadas e o rótulo de tempo e a barra deslizante avançam sincronizados e em tempo real a partir do instante selecionado.
- **Abertura em Repouso (`auto_record: false` por padrão) (`v1.0.27`):** O aplicativo abre em estado de espera, sem disparar a gravação automática no disco. O medidor VU e o nível em decibéis operam continuamente para conferência prévia do microfone, mas o arquivo `.wav` só é criado e iniciado quando o operador clica intencionalmente no botão "Iniciar Gravação".
- **Cálculo de Início e Timestamps Reais (`v1.0.26`):** Toma a data/hora do arquivo como referência de término, calcula a hora de início subtraindo a duração do áudio e formata todas as falas da transcrição nos horários reais do relógio (`HH:MM:SS -> HH:MM:SS`).
- **Local em Branco na Ausência de Certeza (`v1.0.25`):** Preserva a integridade documental mantendo o campo de local estritamente em branco caso não haja confirmação verbal inequívoca.
- **Nomenclatura Obrigatória Iniciada por `ATA_` (`v1.0.24`):** Arquivos de ata com prefixo oficial `ATA_AAAA-MM-DD_HH-MM-SS_Titulo.md`.
- **Motor Completo em Lote (`v1.0.23`):** Suporte a processamento em fila com seleção estendida e atalho `Ctrl + A`.

---

## 📊 Gráfico de Som ao Vivo com Linhas Ultra-Finas de 1px e Passo de 4px (`v1.0.40`)

- **Linhas Ultra-Finas de 1 Pixel com Vão de 3 Pixels:**
  - O osciloscópio ao vivo dos últimos 5 segundos (`canvas_live_wave`) teve seu traçado calibrado para linhas verticais finas de exatamente **1 pixel de espessura (`width=1`) com passo uniforme de 4 pixels (`bar_step=4`)**.
  - Esse intervalo garante 3 pixels de espaço escuro entre cada linha adjacente, eliminando o agrupamento massivo e permitindo distinguir cada traço sonoro individualmente com máxima nitidez.
- **Oscilação Vertical Simétrica Centrada no Horizonte:**
  - As barras agora expandem de forma equilibrada e idêntica para cima e para baixo a partir da linha central (`cy`), espelhando a estética limpa de Voice Memo da referência visual.
- **Curva de Resposta Dinâmica Natural para Voz Humana:**
  - Durante o silêncio de repouso, as barras repousam em discretos pontos centrais de 2px de altura (4px total), mantendo o horizonte estável e limpo.
  - Na presença de fala, a escala de amplitude dinâmica (`(a ** 0.85) * mult * max_h`) mapeia fielmente a cadência das sílabas e entonações, sem saturar as linhas em blocos uniformes no topo.
- **Enquadramento Sutil e Fundo Escuro:**
  - Fundo atualizado para `#020617` (ardósia profunda), linha central em `#0f172a` e discretas linhas horizontais de enquadramento no topo e na base em `#1e293b`.
  - O traço de onda em ciano `#38bdf8` ganha alto contraste e definição cirúrgica em qualquer monitor.

---

## ☑️ Marcação e Transcrição em Lote sob Demanda (`v1.0.39`)

- **Coluna Dedicada de Caixa de Seleção (`☑`/`☐`):**
  - A tabela de áudios (`tree_audios`) agora conta com uma primeira coluna de caixas de seleção (`marcar`, 42px) que indica com símbolos visuais nítidos se cada áudio está marcado (`☑`) ou desmarcado (`☐`).
  - Separadores de dia mantêm a coluna em branco para preservar o fluxo limpo da lista.
- **Interação Natural por Mouse e Teclado:**
  - **Clique Direto:** Clicar na célula da coluna 1 de qualquer linha alterna imediatamente a marcação do áudio.
  - **Cabeçalho:** Clicar no cabeçalho `☑` alterna entre selecionar todos e limpar tudo.
  - **Teclado (`<espaço>`):** Pressionar a barra de espaço com uma ou mais linhas selecionadas alterna a marcação de todos os arquivos destacados em bloco.
- **Botões Rápidos na Barra de Ferramentas:**
  - **`⏳ Só Pendentes`:** Identifica automaticamente os áudios gravados que ainda não possuem transcrição `.md` correspondente e marca exatamente esses arquivos, poupando tempo do operador.
  - **`☑ Todos`:** Marca todos os áudios reais da lista com um único clique.
  - **`☐ Nenhum`:** Limpa todas as marcações ativas.
- **Botão Dinâmico `⚡ Transcrever Marcados (N)`:**
  - O rótulo e o contador do botão atualizam em tempo real (`⚡ Transcrever Marcados (3)`).
  - Ao ser acionado, prioriza estritamente os arquivos assinalados, executando a fila sequencial sem requerer seleções contíguas com o mouse.
- **Ordenação Cronológica e Prevenção de Falhas:**
  - As listas de arquivos (`tree_audios` e `tree_md`) agora ordenam prioritariamente por data do arquivo decrescente e segundo por horário/mtime decrescente, eliminando duplicidade de divisores de dia.

---

## 📏 Linhas Finas no Gráfico de Som e Separadores (`v1.0.38`)

- **Traçado Ultra-Fino de Alta Definição (1px com Passo de 3px):**
  - No osciloscópio superior (`canvas_live_wave`), a espessura das barras verticais foi ajustada para **linhas finas de 1 pixel (`width=1`)**, com espaçamento de 2 pixels entre elas (`bar_step=3`).
  - O resultado é uma visualização leve, arejada e analógica, com centenas de linhas verticais que vibram com as cristas e vales da voz sem poluição visual.
- **Divisores de Dia Minimalistas nas Tabelas:**
  - As linhas divisórias de dia em `tree_audios` e `tree_md` receberam um padrão minimalista e limpo (`── 📅 DD/MM/AAAA (Dia-da-semana) ──`), proporcionando distinção clara e elegante entre as jornadas de gravação sem carregar a interface.

---

## 📅 Linhas Divisórias Cronológicas por Dia de Gravação (`v1.0.37`)

- **Agrupamento Visual por Data nas Tabelas de Arquivos:**
  - Tanto na aba de **Gravações de Áudio (.wav)** quanto na aba de **Transcrições do Dia (.md)**, as listas de arquivos agora contam com linhas divisórias visuais inseridas automaticamente a cada transição de dia.
  - Cada separador destaca a data e o dia da semana correspondente (exemplo: `📅 ──── 19/11/2026 (Quinta-feira) ─────────────────────────────`), utilizando fundo destacado `#1e293b` e tipografia em ciano `#38bdf8`.
- **Detecção Inteligente de Data:**
  - A rotina `_extrair_data_dia_arquivo` realiza a extração precisa da data do arquivo a partir de seu prefixo nominal oficial (`gravando_AAAA-MM-DD_...` ou `AAAA-MM-DD_...`), com fallback seguro para a data de modificação (`stat.st_mtime`).
- **Blindagem Completa de Interações e Operações:**
  - **Duplo-clique e Reprodução:** Clicar em um separador não dispara tentativa de reprodução nem gera erros.
  - **Seleção Total (Ctrl+A):** O atalho `Ctrl+A` seleciona exclusivamente os arquivos reais de áudio ou Markdown, pulando automaticamente todos os divisores de dia.
  - **Operações em Lote e Transcrição:** A fila de processamento e a exclusão com envio para `lixeira/` filtram estritamente os arquivos válidos, garantindo integridade absoluta do fluxo de trabalho.

---

## 💎 Renderização Cristalina Pixel-Perfect sem Borrão (`v1.0.36`)

- **Diagnóstico da Causa Raiz do Efeito Borrado:**
  - O desenho vetorial nativo do Tkinter (`create_line` com coordenadas reais e `capstyle="round"`) sofria degradação de antialiasing e interpolação de subpixel do subsistema de desenho do Windows GDI/Tk, produzindo bordas difusas e contornos embaçados ao redor das barras em telas de alta definição.
- **Pipeline de Rasterização de Alta Precisão (Pillow / PIL):**
  - Todo o quadro do osciloscópio é gerado diretamente em memória com a biblioteca Pillow (`PIL.ImageDraw`), com alinhamento estrito a coordenadas inteiras (`x`, `y` inteiros de pixel).
  - Cada coluna vertical possui 3 pixels de largura com passo de 5 pixels (`draw.rounded_rectangle([x1, cy - h_top, x2, cy + h_bot], radius=1)`), conferindo cantos arredondados ultra-definidos e espaçamento milimétrico.
  - A imagem rasterizada é convertida em `ImageTk.PhotoImage` e transferida para o Canvas via transferência direta de bitmap (BitBlt nativo do sistema operacional), garantindo nitidez absoluta, contraste cristalino e zero borrão.
- **Elementos Visuais Nativos Integrados:**
  - Grade de tempo com linhas pontilhadas verticais a cada 1 segundo e marcadores temporais (`-5.0s`, `-4.0s`, etc.).
  - Linha horizontal de horizonte zero (`cy`) em tom sutil `#1e293b`.
  - Cápsulas mínimas de 3 pixels em repouso durante silêncio e marcador verde iluminado no canto direito (`Agora`).

---

## 📊 Forma de Onda em Barras Verticais Arredondadas (`v1.0.35`)

- **Estilo Voice Memo / SoundCloud com Pontas Arredondadas:**
  - A renderização do sinal acústico dos últimos 5 segundos no painel superior (`canvas_live_wave`) foi totalmente alinhada ao padrão visual moderno de barras verticais discretas com espaçamento.
  - Cada fatia temporal do áudio é representada por uma coluna individual com espessura uniforme (`width=2`), passo de 4 pixels e pontas em cápsula arredondada (`capstyle="round"`).
- **Assimetria Acústica Real e Repouso Elegante:**
  - A barra vertical mapeia de forma independente a crista máxima positiva (`y_sup = cy - h_top`) e o vale mínimo negativo (`y_inf = cy + h_bot`), preservando a dinâmica natural da voz.
  - Durante pausas ou silêncio na sala, as barras reduzem-se a uma cápsula mínima de 3 pixels centralizada na linha zero horizontal, eliminando ruídos visuais e oferecendo uma referência de repouso extremamente limpa.
- **Paleta de Cores e Alto Contraste:**
  - Em monitoramento passivo: azul celeste vibrante (`#38bdf8`), proporcionando leitura clara sobre o fundo escuro `#0b1120`.
  - Em gravação ativa: ciano elétrico brilhante (`#00b4d8`), sinalizando a captura contínua de áudio.

---

## ⚡ Alta Densidade na Oscilação do Gráfico ao Vivo (`v1.0.34`)

- **Resolução de Amostragem Elevada (Até 900 Bins):**
  - O número de bins horizontais de amostragem na janela deslizante de 5 segundos foi ampliado de ~300 para **até 900 bins** (`largura / 1.3`), garantindo que praticamente cada coluna de pixels da tela represente um intervalo temporal detalhado de áudio (~5.5 milissegundos).
- **Traçado Denso de Picos e Vales por Coluna:**
  - Para cada coluna de amostragem no eixo horizontal, o traçado conecta os extremos superior e inferior (`y_sup` e `y_inf`), reproduzindo com riqueza analógica a densidade das oscilações acústicas da voz humana.
  - O resultado visual é encorpado e vibrante, mantendo a regra de **zero preenchimento sólido** (*no fill*).
- **Calibração de Ganho e Visibilidade:**
  - O multiplicador de escala da curva de raiz quadrada foi calibrado para `mult = (ganho ** 0.6) * 1.85`, elevando a amplitude visual da fala e destacando os harmônicos e transientes vocais sem saturação artificial.

---

## 〰️ Forma de Onda Contínua com Oscilação Acústica Real (Sem Preenchimento) (`v1.0.33`)

- **Eliminação do Polígono Preenchido (*No Fill*):**
  - Anteriormente, o gráfico de som desenhava um envelope simétrico fechado utilizando `create_polygon` com preenchimento opaco (`fill`), gerando uma mancha visual sólida sob o sinal.
  - Na versão `v1.0.33`, o polígono fechado foi totalmente removido. A forma de onda passa a ser desenhada exclusivamente como um traço contínuo de oscilação acústica (`create_line`), preservando o fundo limpo e a visibilidade dos marcadores temporais.
- **Oscilação Real entre Cristas e Vales:**
  - Em vez de espelhar um valor absoluto forçado (`|x|`), o mecanismo analisa os extremos positivos (`v_max`) e negativos (`v_min`) reais de cada janela de tempo.
  - A linha contínua alterna entre os picos positivos e os vales negativos ao longo do eixo horizontal, reproduzindo a dinâmica ondulatória do som.
- **Horizonte de Silêncio e Alta Fidelidade Visual:**
  - Nos momentos de silêncio ou pausa entre falas, o traço se acomoda suavemente sobre a linha horizontal central de referência (`cy`), evidenciando a ausência de sinal sonoro sem artefatos.
  - Ao detectar fala, a linha oscila instantaneamente com contorno ciano elétrico vibrante (`#06b6d4` durante a gravação; `#38bdf8` em monitoramento passivo), proporcionando a autêntica estética de osciloscópio profissional de áudio.

---

## 🔊 Ampliação de Amplitude e Ganho do Gráfico ao Vivo (`v1.0.32`)

- **Aumento da Altura Física do Canvas (+65%):**
  - A altura visual do osciloscópio de ondas em tempo real (`canvas_live_wave`) foi expandida de 46px para **76px**, conferindo ampla área vertical para observar a dinâmica do sinal sonoro sem comprimir as abas inferiores.
  - O cálculo do ponto central (`cy = h / 2.0`) e a altura máxima útil de crista (`max_h = max(2.0, cy - 4.0)`) utilizam 100% da nova dimensão para renderização do envelope simétrico espelhado.
- **Curva de Ganho Perceptual com Compressão Não-Linear:**
  - Microfones em ambientes amplos ou posicionados à distância captam a fala humana em níveis de amplitude normalizados entre 0.02 e 0.08, resultando em oscilações pequenas em escalas lineares puras.
  - A renderização passou a aplicar compressão de raiz quadrada não-linear:
    - Fórmula de sensibilidade: `h = min(1.0, math.sqrt(p) * mult) * max_h`
    - Multiplicador de escala: `mult = (ganho ** 0.6) * 1.35`
    - Isso garante que conversas normais de sala preencham entre 45% e 85% da altura útil da tela, tornando o sinal sonoro imediatamente nítido e vibrante sem saturar bruscamente em picos sonoros.
- **Controle Dinâmico de Ganho na Barra de Cabeçalho (`CTkSegmentedButton`):**
  - Foi adicionado diretamente no cabeçalho do osciloscópio um seletor visual segmentado com as opções: `1x`, `2x`, `3x` (padrão ativo) e `5x`.
  - O operador pode alternar instantaneamente a sensibilidade visual com um único clique, adaptando o gráfico a microfones de lapela, microfones direcionais, microfones de teto ou captação de vozes mais afastadas.

---

## 🛡️ Estabilidade Contínua do Loop de Interface e Gravação (`v1.0.31`)

- **Diagnóstico do Problema:**
  - Após a inclusão do osciloscópio de som em tempo real, a ausência da diretiva `import numpy as np` no cabeçalho de `scripts/gui_app.py` provocava uma exceção silenciosa (`NameError: name 'np' is not defined`) na rotina de desenho das ondas sonoras.
  - Essa exceção não tratada interrompia o encadeamento de chamadas `after(50, self._loop_interface)`, fazendo com que o temporizador visual, a barra de volume e o gráfico congelassem na tela, dando a impressão de parada de captura de áudio.
- **Correção Aplicada:**
  - Importação explícita do NumPy adicionada ao escopo do aplicativo gráfico.
  - Encapsulamento completo da rotina `_atualizar_grafico_tempo_real()` com tratamento de exceções e registro em log de auditoria, garantindo que o ciclo periódico de interface e gravação nunca seja interrompido sob qualquer condição gráfica transitória.

---

## 🌊 Gráfico de Som Contínuo em Tempo Real (Últimos 5 Segundos) (`v1.0.30`)

- **Visualização Contínua em Tela:**
  - Foi incorporado ao painel superior de controles um osciloscópio visual dedicado (`canvas_live_wave`), exibindo de forma ininterrupta as oscilações acústicas capturadas pelo microfone ao longo de uma janela deslizante contínua de 5,0 segundos.
  - O fluxo do sinal se desloca suavemente da direita para a esquerda:
    - **Extremo Direito (`Agora / 0s`):** Ponto de entrada imediato da voz ou som ambiente emitido na sala.
    - **Extremo Esquerdo (`-5.0s`):** Ponto de saída do histórico após 5 segundos decorridos.
- **Arquitetura de Alta Performance (`scripts/recorder.py`):**
  - Implementado buffer circular thread-safe (*ring buffer* prealocado em NumPy) dimensionado para `sample_rate * 5.0` amostras (80.000 amostras a 16 kHz).
  - O método `obter_amostras_tempo_real(segundos=5.0)` extrai instantaneamente a série linear desdobrada sem impacto na gravação principal.
- **Renderização Gráfica Otimizada (`scripts/gui_app.py`):**
  - **Envelope Espelhado Neon:** Desenha o envelope acústico simétrico preenchido com contorno vibrante (`#06b6d4` durante a gravação ativa; `#38bdf8` em monitoramento passivo).
  - **Grade de Tempo Estática:** Marcadores verticais pontilhados a cada 1 segundo (`-5.0s`, `-4.0s`, `-3.0s`, `-2.0s`, `-1.0s`, `Agora (0s)`), atualizados automaticamente com o redimensionamento da janela.
  - **Sinalização de Mudo Temporário:** Quando o microfone é silenciado pelo botão de mudo, o gráfico se aplaina e exibe em destaque a indicação visual `🔇 MICROFONE SILENCIADO (MUDO TEMPORÁRIO)`.
  - **Badge de Estatísticas em Tempo Real:** Exibe no cabeçalho o nível em decibéis, taxa em kHz e confirmação da janela de 5.0s.

---

## 🏷️ Renomeação Contextual Exclusiva para Arquivos Markdown (.md) (`v1.0.29`)

- **Preservação Absoluta dos Arquivos de Áudio WAV:**
  - Os arquivos de áudio gravados em disco permanecem estritamente com seus nomes originais de gravação no formato `gravando_AAAA-MM-DD_HH-MM-SS.wav`.
  - O módulo `scripts/renomeador.py` e os gatilhos da interface gráfica foram atualizados para que nenhuma chamada de renomeação seja executada sobre arquivos `.wav`.
- **Foco nos Arquivos Textuais e Documentais:**
  - Apenas as transcrições completas (`..._transcricao.md`) e as atas formais (`ATA_...md`) recebem os títulos contextuais extraídos do diálogo.
  - Isso garante que reprodutores de áudio ativos, caches de forma de onda (*waveform*), rotinas de leitura de cabeçalhos PCM e índices cronológicos continuem acessando os arquivos de som sem risco de colisões ou travas por handles abertos no sistema operacional Windows.

---

## 🎯 Sincronização de Playhead e Tempo Decorrido na Forma de Onda (`v1.0.28`)

- **Diagnóstico da Causa Raiz:**
  - No mecanismo de áudio do Pygame (`pygame.mixer.music`), a função `get_pos()` retorna estritamente a quantidade de milissegundos decorridos desde que a chamada `.play()` atual foi invocada, desconsiderando o parâmetro `start=X` (offset inicial da faixa).
  - Como consequência, ao clicar na forma de onda sonora para pular para 30 segundos, o áudio saltava corretamente para os 30 segundos, porém o `get_pos()` reportava imediatamente 0ms, fazendo com que o cursor visual (playhead), a barra deslizante e o contador de tempo voltassem para `00:00:00` em vez de avançarem a partir de `00:00:30`.
- **Solução Implementada e Aprimoramentos:**
  1. **Armazenamento de Offset Absoluto (`player_start_sec`):**
     - O player armazena a posição de início exata sempre que uma busca é acionada (`self.player_start_sec = start_sec`).
  2. **Feedback Visual Imediato no Clique:**
     - Ao clicar com o mouse no gráfico Canvas, o método `_ao_clicar_waveform` calcula a fração temporal e desenha instantaneamente a linha guia vertical vermelha (`playhead`) na coordenada X exata do clique, eliminando qualquer atraso perceptível de interface antes da inicialização do mixer.
  3. **Atualização Imediata de Slider e Rótulo:**
     - A rotina de reprodução calcula a porcentagem exata (`pos_sec / duracao`), ajusta imediatamente o slider de posição (`self.slider_pos.set(pct)`) e formata o rótulo de tempo (`lbl_player_tempo`) com o tempo real (ex.: `00:00:30 / 00:02:15`).
  4. **Loop Contínuo com Deslocamento Real:**
     - O loop periódico de atualização da interface calcula a posição temporal real por `pos_sec = self.player_start_sec + (pos_ms / 1000.0)`, garantindo avanço suave, contínuo e perfeitamente sincronizado do cursor vermelho, do slider e do cronômetro até o final da faixa sonora.

---

## ⏸️ Inicialização Passiva e Desativação de Gravação Automática ao Abrir (`v1.0.27`)

- **Controle Total pelo Operador:**
  - O aplicativo não mais inicia a captura e a gravação de áudio em disco de forma automática na inicialização.
  - Ao abrir o sistema ou reiniciar o computador, o gravador permanece em modo de **monitoramento passivo**: o operador visualiza os decibéis e o medidor VU em tempo real para verificar se o microfone está ativo e funcionando, mas nenhum arquivo WAV é criado ou consumido em disco até que o botão **"Iniciar Gravação"** seja explicitamente acionado.
- **Prevenção de Arquivos Acidentais:**
  - Elimina a criação indesejada de gravações curtas, vazias ou residuais decorrentes de simples aberturas de tela, inspeções ou testes da interface.
- **Configuração Flexível:**
  - Caso o operador deseje a recuperação automática contínua em caso de reinicialização não programada de máquina (modo quiosque 24/7), basta marcar a caixa de seleção **"Auto-iniciar gravação ao abrir"** na interface ou habilitar `auto_record: true` nas preferências.

---

## ⏱️ Cálculo de Início e Ajuste de Horários Reais na Transcrição (`v1.0.26`)

- **Problema Resolvido:**
  - Anteriormente, as transcrições eram geradas com contadores de tempo relativos ao início do áudio (`0:00:00 -> 0:00:10`, `0:10:00 -> 0:10:30`), o que dificultava saber a qual momento exato do dia (manhã, tarde, noite) pertencia cada intervenção de voz em gravações ambientais contínuas.
- **Mecanismo de Cálculo:**
  1. **Referência do Arquivo (Término):** O sistema obtém a data e hora de finalização do arquivo WAV a partir de seus metadados de modificação do sistema de arquivos (`st_mtime`) ou do carimbo de data/hora contido no nome do arquivo.
  2. **Subtração da Duração:** Com a duração precisa do áudio (`total_duration` via cabeçalhos PCM/WAV e Whisper), o sistema calcula retroativamente o exato instante em que a gravação começou:
     `hora_inicio = hora_fim - duracao`
  3. **Deslocamento Linear dos Segmentos:** Cada segmento falado detectado pelo Whisper (`segment.start` e `segment.end`) é somado ao `hora_inicio`, gerando carimbos temporais no horário real de relógio:
     ```markdown
     - `[09:05:19 -> 09:05:29]` Se eles vão lá, é só lembrando que eu estou gravando...
     - `[09:05:29 -> 09:05:40]` São segundo, ele só atualiza a minha planilha aqui...
     ```
  4. **Metadados Completos no Cabeçalho:**
     O documento Markdown registra explicitamente:
     - `Data da Gravação`
     - `Horário de Início (Calculado)`
     - `Horário de Término (Referência do Arquivo)`
     - `Duração Total`
- **Reflexo Automático nas Atas:**
  - O módulo `scripts/gerador_ata.py` extrai automaticamente esses horários reais das falas, preenchendo os campos de Início e Término da sessão com os horários do relógio (exemplo: `09:05:19` às `09:24:32`), bem como dividindo os blocos analíticos em janelas horárias reais (ex.: `Bloco 1 (09:05:19 às 09:15:19)`).
- **Ajuste Automatizado para Acervos Existentes:**
  - Foi implementada a rotina `ajustar_tempos_transcricao()` no módulo `scripts/transcriber.py`, permitindo converter qualquer transcrição legada em formato relativo para o padrão horário real.

---

## 🏛️ Integridade de Local nas Atas: Campo em Branco na Ausência de Certeza (`v1.0.25`)

- **Rigor Documental e Fidelidade ao Áudio:**
  - O gerador de atas estruturadas (`scripts/gerador_ata.py`) segue o princípio fundamental de fidelidade estrita: nenhum dado não falado no áudio deve ser inferido ou assumido.
  - O sistema analisa o texto completo transcrito em busca de declarações inequívocas de localização (ex.: "estamos no laboratório...", "reunidos no espaço...", "na sala 101").
  - Caso o diálogo não contenha certeza absoluta sobre onde o evento ocorreu, o campo correspondente é gerado estritamente em branco:
    `- **Local / Ambiente:** `
  - As seções complementares da ata ("Contexto e Objetivo" e "Síntese Final") também deixam de pressupor ambientes genéricos, preservando a neutralidade e veracidade do documento.
- **Atualização Retroativa do Acervo:**
  - Todas as 22 atas existentes na pasta `transcricoes/` foram atualizadas para o novo formato estrito, deixando o campo de local em branco nos registros em que o local não foi afirmado verbalmente.

---

## 📋 Nomenclatura Padronizada de Atas com Prefixo "ATA_" (`v1.0.24`)

- **Prefixo Obrigatório `ATA_`:**
  - Todas as atas estruturadas geradas tanto individualmente quanto em lote agora adotam como padrão obrigatório o início pelo termo `ATA_`.
  - Formato com tema contextual identificado: `ATA_AAAA-MM-DD_HH-MM-SS_Titulo-Contextual.md` (exemplo: `ATA_2026-11-18_09-05-19_Sensores-Projetos.md`).
  - Formato base por data/hora: `ATA_AAAA-MM-DD_HH-MM-SS.md` (exemplo: `ATA_2026-11-18_10-00-00.md`).
- **Benefícios Imediatos:**
  1. **Agrupamento Alfabético Natural:** No Windows Explorer e no seletor de arquivos, todas as atas do dia ficam naturalmente agrupadas em sequência sob a letra "A", sem se misturar com os arquivos de áudio gravado (`gravando_...`) ou com as transcrições completas (`AAAA-..._transcricao.md`).
  2. **Identificação Visual Instantânea:** O operador bate o olho no nome do arquivo e sabe imediatamente que se trata de uma ata formal executiva, com deliberações, sínteses e encaminhamentos acadêmicos.
  3. **Rastreabilidade Bidirecional:** O carimbo temporal (`AAAA-MM-DD_HH-MM-SS`) é preservado integralmente logo após o prefixo, permitindo o pareamento exato e automático com a gravação de áudio original e a transcrição correspondente.
- **Compatibilidade Retroativa Integral:**
  - O visualizador e editor de transcrições da interface reconhece tanto arquivos com o novo padrão `ATA_*.md` quanto formatos legados (`*_ata.md`), assegurando que nenhum arquivo histórico deixe de ser exibido.
  - O motor de lote verifica a existência da ata prévia considerando tanto o prefixo `ATA_` quanto sufixos legados, evitando duplicações desnecessárias.

---

## ⚡ Transcrições e Geração de Atas Estruturadas em Lote (`v1.0.23`)

- **Botão "⚡ Transcrever em Lote":**
  - Se múltiplos arquivos estiverem selecionados na lista de gravações, transcreve o conjunto selecionado.
  - Se nenhum arquivo estiver selecionado, pesquisa os arquivos `.wav` sem transcrição na pasta e oferece transcrever todos os pendentes em fila.
  - Pergunta ao operador se deseja gerar as atas estruturadas automaticamente para cada áudio concluído.
- **Botão "📋 Atas em Lote":**
  - Disponível tanto na aba de Gravações quanto na aba de Transcrições do Dia.
  - Identifica todas as transcrições que ainda não possuem atas geradas (ou as transcrições selecionadas com Ctrl/Shift/Ctrl+A) e gera as atas estruturadas sequencialmente.
  - Vincula automaticamente cada ata ao respectivo arquivo de áudio original para extrair metadados e minutagem.
- **Seleção Total com Atalho `Ctrl + A`:**
  - Pressionar `Ctrl + A` na lista de gravações seleciona instantaneamente todos os áudios do dia.
  - Pressionar `Ctrl + A` na lista de transcrições seleciona todos os documentos Markdown.
- **Exclusão Segura em Lote para a `lixeira/`:**
  - Selecionar múltiplos áudios ou múltiplos arquivos Markdown e clicar em "🗑️ Excluir" move com segurança todo o lote para a pasta `lixeira/`, preservando a rastreabilidade contra exclusão definitiva.

---

## 🔴 Ícone Dinâmico Piscando em Vermelho na Barra de Tarefas (`v1.0.22`)

- **Alerta Visual Instantâneo no Windows:** Durante a gravação, o ícone da aplicação na barra de tarefas do Windows e na barra de título pisca continuamente em vermelho a cada 500ms (frequência de 1 Hz), sinalizando de forma clara e inconfundível que a sala está sob captação ativa de áudio.
- **Visibilidade mesmo em Segundo Plano:** Graças ao registro de processo `SetCurrentProcessExplicitAppUserModelID("CMaker.TranscricaoAmbiental.App.1")`, o Windows vincula a janela ao seu próprio identificador na barra de tarefas. Isso garante que, mesmo quando a janela estiver minimizada ou em segundo plano atrás de outros programas (navegadores, editores, planilhas), o usuário enxergue de imediato o ícone piscando em vermelho na barra de tarefas.
- **Alternância de Alta Fidelidade (32x32 e 16x16):**
  - **Fase Acesa:** Ícone em vermelho carmim vibrante (`#dc2626`) com anel de brilho translúcido (`#ef4444`) e ponto branco central de gravação, acompanhado pelo prefixo `🔴 [GRAVANDO]` no título da janela.
  - **Fase Apagada:** Ícone em tom vinho escuro/ardósia (`#1e1b2e` / `#7f1d1d`), criando um contraste nítido e pulsante sem piscamentos incômodos.
  - **Estado Mutado:** Quando o operador aciona o botão "🎙️ Mudo Temporário", o ícone da barra de tarefas passa a alternar em tom âmbar/laranja (`#d97706`), com o título `🔇 [MUTADO]`, permitindo saber se a gravação está silenciada sem precisar abrir a janela.
- **Restauração Automática:** Ao finalizar a gravação (ou fechar a aplicação), o ícone padrão do estúdio em azul/ardósia e o título original são imediatamente restaurados.

---

## 📋 Reordenação da Lista de Gravações: Nome do Arquivo antes do Draft de Onda (`v1.0.21`)

- **Primeira Coluna para o Nome do Arquivo:** A tabela de gravações na aba principal foi reorganizada para atender ao fluxo visual padrão de leitura e gestão de arquivos. A coluna **"Arquivo de Áudio (.wav)"** passa a ocupar a primeira posição à esquerda, permitindo identificar imediatamente o arquivo antes dos metadados e gráficos.
- **Draft de Onda Posicionado Imediatamente após o Nome:** A segunda coluna, **"Draft de Onda"**, renderiza diretamente a envoltória sonora de cada áudio utilizando caracteres de blocos Unicode de alta fidelidade (` ▂▃▄▅▆▇█` para áudios com atividade sonora e `··················` para arquivos vazios ou em silêncio).
- **Estrutura Completa de Colunas:**
  1. **Arquivo de Áudio (.wav):** Largura de 340px, alinhamento à esquerda com o nome completo do arquivo.
  2. **Draft de Onda:** Largura de 160px, alinhamento centralizado com o draft da forma de onda.
  3. **Duração:** Largura de 100px, formato `HH:MM:SS`.
  4. **Tamanho (MB):** Largura de 110px.
  5. **Data e Hora:** Largura de 160px, formato `DD/MM/AAAA HH:MM:SS`.
- **Preservação do Painel Interativo Detalhado:** Ao selecionar qualquer arquivo na tabela, o painel inferior continua gerando o gráfico de alta resolução no Canvas, completo com envelope simétrico colorido, badges de pico/RMS/atividade, marcadores temporais, playhead dinâmico sincronizado com a reprodução e seek por clique.

---

## 🔇 Botão de Mudo Temporário sob Demanda (`v1.0.20`)

- **Controle Direto na Barra de Gravação:** O botão **"🎙️ Mudo Temporário"** localizado junto aos controles principais permite suspender a captação sonora a qualquer momento com um único clique, sem necessidade de interromper ou reiniciar o arquivo de gravação.
- **Injeção de Silêncio Matemático (Preservação Temporal):** Enquanto o mudo estiver ativo, o gravador escreve blocos nulos (zeros em PCM) no arquivo `.wav`. Isso assegura que a duração e a sincronização temporal da sessão permaneçam perfeitas, ao mesmo tempo em que conversas paralelas, telefonemas ou momentos confidenciais não são gravados nem transcritos pelo Whisper.
- **Feedback Visual Inconfundível:** Ao ser acionado, o botão assume coloração vermelha destacada (**"🔇 MUTADO (Ativo)"**), o medidor numérico exibe **"🔇 MUDO"** em vermelho e uma badge de aviso surge no painel de controle. Clicar novamente restaura a captação ambiente normal instantaneamente.
- **Restauração Automática:** Ao finalizar qualquer gravação com o botão de parar, o mudo é automaticamente desativado para garantir que a sessão seguinte inicie normalmente.

---

## ⚡ Otimização de Performance e Remoção do Feed em Tempo Real (`v1.0.19`)

- **Eliminação do Processamento Concorrente:** A aba "Feed em Tempo Real" realizava fatiamento de áudio em pedaços de 30 segundos e chamava o Whisper em segundo plano enquanto a gravação acontecia. Isso gerava alto consumo de CPU (50% a 100%), fragmentava o texto e poluía a interface, sendo completamente substituído com muito mais fidelidade pela transcrição do arquivo completo.
- **Captura Ultra-Leve (< 1% CPU):** O motor de gravação agora opera com gravação PCM direta em disco e cálculo imediato de RMS/dB para o VU meter, sem alocações pesadas em memória e sem qualquer risco de travamento de driver de áudio.
- **Interface Focada:** A interface foi simplificada para 3 abas essenciais e objetivas:
  1. **🎵 Gravações de Áudio (.wav):** Lista de áudios com sparklines de onda, painel detalhado de waveform draft, reprodutor com playhead e botões de ação ("⚡ Transcrever com Whisper", "📋 Gerar Ata", "📂 Abrir Local do Arquivo", "🗑️ Excluir Áudio").
  2. **📝 Transcrições do Dia (.md):** Visualizador e editor de texto Markdown com suporte a geração de atas e exportação.
  3. **⚙️ Configurações & Auditoria:** Preferências de automação (transcrição automática ao parar, geração automática de ata, renomeação contextual) e painel completo de logs do sistema (`logs/sistema.log`).

---

## 🏷️ Nomenclatura Estrita de Arquivos de Áudio (`v1.0.18`)

- **Padrão Exclusivo para Áudios (.wav):** Todos os arquivos de gravação gerados e mantidos no sistema adotam estritamente o formato:
  `gravando_AAAA-MM-DD_HH-MM-SS.wav` (exemplo: `gravando_2026-11-18_14-30-00.wav`).
- **Preservação de Nome do Áudio:** O arquivo de áudio não recebe títulos contextuais ou sufixos adicionais, permanecendo limpo e previsível para arquivamento e mala direta.
- **Transcrições e Atas Pareadas:** Os arquivos textuais continuam permitindo títulos contextuais baseados nos temas debatidos (`AAAA-MM-DD_HH-MM-SS_Titulo-Contextual_transcricao.md` e `ATA_AAAA-MM-DD_HH-MM-SS_Titulo-Contextual.md`), mantendo o prefixo temporal idêntico para rastreabilidade direta.

---

## 📊 Gráficos de Som Capturado e Draft de Onda (`v1.0.17`)

- **Miniatura Sparkline por Arquivo Gravado:** Na coluna `"Draft de Onda"` da tabela de gravações, cada arquivo de áudio exibe imediatamente uma representação visual compacta da sua forma de onda sonora. Isso permite ao operador constatar instantaneamente quais áudios contêm voz/sinal real (barras verticais em azul e ciano) e quais estão sem sinal ou mudos (linha sutil em cinza escuro).
- **Painel Interativo de Waveform Draft:** Abaixo da lista de arquivos gravados, a aplicação renderiza um gráfico de alta resolução do arquivo selecionado:
  - **Envelope de Amplitude Símétrico:** Destaque em gradiente com picos de volume e distinção de silêncio.
  - **Telemetria Sonora Instantânea:** Badges com **Duração**, **Pico Máximo (dB)**, **Nível Médio RMS (dB)** e **Porcentagem de Atividade Sonora** (indica se houve fala captada).
  - **Marcadores de Linha do Tempo:** Guias com minutagem distribuídas ao longo de todo o áudio.
  - **Playhead em Tempo Real:** Cursor dinâmico amarelo que percorre o gráfico acompanhando fielmente a reprodução de áudio do mixer.
  - **Click-to-Seek:** Clicar em qualquer ponto do gráfico de onda reposiciona instantaneamente a reprodução do áudio naquele segundo exato.

---

## 🎙️ Monitoramento Ativo de dB e Medidor VU em Tempo Real (`v1.0.16`)

- **Medição Contínua em Espera (Pré-gravação):** A barra de VU e o indicador numérico em decibéis (`-60 dB` a `0 dB`) operam ativamente mesmo com a gravação parada, garantindo que o operador visualize imediatamente se o microfone selecionado está captando áudio real ou se está mudo/desconectado antes de iniciar a sessão.
- **Alternância Instantânea de Entrada:** Ao trocar o dispositivo no menu suspenso de microfones, o fluxo de monitoramento reinicia instantaneamente no novo hardware selecionado, oferecendo resposta visual imediata.
- **Zero Gravação em Disco no Modo Monitor:** Durante o monitoramento prévio, nenhum dado é gravado no disco, preservando o armazenamento e o desempenho.
- **Feedback Transparente de Transcrição:** A barra de progresso do Whisper informa explicitamente as etapas prévias (carregamento de modelo, execução do filtro VAD de detecção de voz e decodificação de falas), eliminando a impressão de estagnação em arquivos extensos.

---

## ⚙️ Nova Aba de Configurações, Automações e Auditoria (`v1.0.15`)

Disponibilizada na interface para controle completo dos fluxos automáticos e rastreabilidade técnica:
1. **Preferências de Automação Independentes:**
   - **Transcrever automaticamente ao parar a gravação:** Ao finalizar qualquer sessão de gravação, o sistema valida a integridade do arquivo `.wav` e inicia em segundo plano a transcrição com Whisper do último áudio finalizado, sem bloquear a interface.
   - **Gerar ata automaticamente após a transcrição:** Concluída a transcrição, compila instantaneamente a ata formal da sessão.
   - **Renomear arquivos com título contextual:** Extrai automaticamente palavras-chave e tópicos centrais das falas transcritas para aplicar o padrão oficial:
     - Áudio: `gravando_AAAA-MM-DD_HH-MM-SS.wav`
     - Transcrição: `AAAA-MM-DD_HH-MM-SS_Titulo-Contextual_transcricao.md`
     - Ata: `ATA_AAAA-MM-DD_HH-MM-SS_Titulo-Contextual.md`
   - Todas as preferências são persistidas no arquivo local `data/recorder_config.json` e restauradas compulsoriamente na inicialização.

2. **Painel de Auditoria e Logs do Sistema:**
   - Visualização cronológica estruturada com data/hora, nível (`INFO`, `WARN`, `ERROR`), módulo e mensagem.
   - Persistência contínua em `logs/sistema.log` com rotação automática de arquivos (limite de 5 MB com até 3 arquivos de backup).
   - Filtro instantâneo por nível de severidade (`TODOS`, `INFO`, `WARN`, `ERROR`).
   - Botão **"📥 Exportar Logs..."** para salvar relatórios técnicos externos em qualquer diretório.
   - Botão **"🗑️ Limpar Tela"** para higienização visual sem exclusão do arquivo em disco.

3. **Geração de Atas com Resolução de Dependência:**
   - Botão **"📋 Gerar Ata"** nas guias de Gravações e Transcrições.
   - Se o estudante/docente solicitar a geração de ata para um áudio que ainda não foi transcrito, o sistema oferece transparentemente a transcrição como dependência prévia e encadeia a confecção da ata ao final.

4. **Validação de Integridade e Watchdog:**
   - Validação técnica rigorosa de cabeçalhos e duração de áudio WAV via `soundfile.info()` ao término da gravação.
   - Monitoramento contínuo de avanço (heartbeat) do Whisper, emitindo alertas diagnósticos no log de auditoria caso ocorra inatividade prolongada superior ao limite configurado.

---

## 📂 Abrir Local do Arquivo no Windows Explorer (`v1.0.14`)

Para facilitar o acesso imediato aos arquivos de mídia e texto gerados pelo sistema, foram implementados botões nativos de exploração de arquivos:
- **Guia Gravações de Áudio (.wav):** Botão **"📂 Abrir Local do Arquivo"** na barra de ferramentas superior. Ao selecionar qualquer gravação na lista, o clique abre o Windows Explorer posicionando o cursor e destacando exatamente o arquivo `.wav` selecionado (`explorer /select,<caminho>`).
- **Guia Transcrições do Dia (.md):** Botão **"📂 Abrir Local do Arquivo"** disponibilizado tanto no painel de seleção de transcrições quanto no cabeçalho do editor Markdown. Permite abrir o arquivo `.md` diretamente em sua pasta de origem no Windows Explorer com foco instantâneo.
- **Abertura Inteligente de Diretório:** Caso nenhum arquivo específico esteja selecionado, o botão abre de forma transparente a pasta correspondente (`gravacoes/` ou `transcricoes/`).

---

## 📋 Geração de Atas e Sínteses de Sessões de Gravação

O sistema permite a compilação cronológica e analítica dos diálogos de sala em documentos de **Ata Executiva** (`ATA-CMAKER-YYYYMMDD-vX.Y.Z.md`):
- **Estrutura Formal:** Identificação do evento, horários de início e término, arquivos de áudio vinculados, mesa avaliadora / participantes, resumo cronológico por blocos de tempo, deliberações técnicas e encaminhamentos acadêmicos.
- **Rastreabilidade:** Todas as deliberações são referenciadas com base nos registros temporais das falas captadas.
- **Localização:** Os rascunhos e análises são alocados em [EmDesenvolvimento/](file:///e:/IAGenMaster/2026/CMaker/Projetos/11-TranscricaoAmbiental/EmDesenvolvimento) conforme o ciclo de vida documental seguro.

---

## 🚀 Resiliência de Motor e Fallback Automático para CPU

- **Validação Antecipada de Hardware:** Ao inicializar a biblioteca Faster-Whisper, o sistema executa um warm-up de teste silencioso. Caso a máquina possua placa NVIDIA mas não possua as bibliotecas dinâmicas do CUDA instaladas (`cublas64_12.dll` ou cuDNN no PATH do Windows), o sistema detecta a ausência no primeiro milissegundo e comuta automaticamente para **CPU otimizado (int8)**.
- **Zero Travamentos em 0.0%:** Elimina qualquer travamento na barra de progresso e impede que arquivos Markdown sejam criados em branco ou corrompidos.
- **Exibição Imediata no Editor:** Os arquivos `.md` são populados com cada fala capturada com timestamp de início e término (`[HH:MM:SS -> HH:MM:SS] Texto`).

---

## 🛑 Cancelamento Instantâneo de Transcrição sob Demanda

Durante a transcrição de qualquer arquivo de áudio gravado:
- Um botão vermelho de destaque **"✖ Cancelar Transcrição"** é exibido dinamicamente na barra de ferramentas enquanto o Whisper estiver operando.
- **Reativação Imediata:** Ao clicar no botão, o cancelamento é disparado instantaneamente, a interface remove o botão de cancelamento e **o botão "⚡ Transcrever com Whisper" é reativado imediatamente (`state="normal"`)**, permitindo iniciar uma nova transcrição sem bloqueios ou esperas.
- **Sem Travas Modais:** Foram removidas caixas de diálogo modais bloqueantes (`messagebox`) no cancelamento, garantindo resposta imediata na tela.
- **Isolamento de Sessão:** O sistema utiliza um identificador numérico incremental de sessão para descartar com segurança qualquer retorno residual da thread anterior em segundo plano.
- O arquivo `.md` é fechado com uma nota informativa (`[AVISO: Transcrição interrompida/cancelada pelo usuário]`), preservando as falas transcritas até aquele instante sem corrupção.

---

## 🏷️ Identificação de Versão na Interface

A versão atual da aplicação (`v1.0.15`) é exibida em pontos estratégicos da interface gráfica:
- **Barra de Título da Janela:** `Gravador e Transcritor Ambiental de Sala: 24/7 - v1.0.15`.
- **Cabeçalho Principal:** Badge destacado ao lado do título principal no topo da janela.
- **Rodapé do Player de Áudio:** Indicação sutil no canto inferior direito da barra de reprodução (`Versão v1.0.15`).

---

## ⚡ Indicador de Porcentagem (%) na Transcrição

Ao clicar no botão **"⚡ Transcrever com Whisper"** em qualquer áudio gravado:
- Uma barra de progresso e um indicador numérico em porcentagem (`0.0%` a `100.0%`) aparecem em tempo real na barra de ferramentas.
- O sistema calcula a razão exata entre o ponto de áudio já decodificado pelo Whisper e a duração total do arquivo (`[segment.end / duration] * 100`).
- Exibe o tempo atual processado e a duração total do arquivo (ex.: `Transcrevendo: 48.5% (00:04:51 / 00:10:00)`).
- Ao atingir 100%, emite aviso amigável de conclusão e atualiza a tabela de transcrições automaticamente.

---

## 🎙️ Listagem Completa de Microfones (Sem Bloqueios de Driver)

- **Todos os Dispositivos Disponíveis:** Lista todas as entradas e microfones do sistema (MME, DirectSound, Windows WASAPI, WDM-KS), permitindo escolher exatamente o microfone desejado (ex.: Headsets Bluetooth, microfones integrados, interfaces de áudio USB).
- **Sem Travamentos de PortAudio:** A listagem é feita por metadados de sistema sem abrir streams concorrentes de teste, prevenindo erros de canal ocupado (*device unavailable*) e bloqueios em fones Bluetooth.
- **Identificação Clara:** Cada item da lista exibe seu ID, nome amigável, API de áudio e indicação de dispositivo padrão do Windows (ex.: `[1] Headset (JBL Tune 780NC) (MME) - Padrão`).

---

## 📦 Executável Portátil para Outro Computador

A aplicação possui distribuição autossuficiente (standalone) com o modelo Whisper pré-instalado:

1. **Pasta do Executável:**
   - Localização: [dist/TranscricaoAmbiental/](file:///e:/IAGenMaster/2026/CMaker/Projetos/11-TranscricaoAmbiental/dist/TranscricaoAmbiental)
   - Executável direto: [TranscricaoAmbiental.exe](file:///e:/IAGenMaster/2026/CMaker/Projetos/11-TranscricaoAmbiental/dist/TranscricaoAmbiental/TranscricaoAmbiental.exe)
   - Atalho de execução: [Iniciar_Transcricao.bat](file:///e:/IAGenMaster/2026/CMaker/Projetos/11-TranscricaoAmbiental/dist/TranscricaoAmbiental/Iniciar_Transcricao.bat)

2. **Arquivo Compactado para Transferência (Pen Drive / Nuvem):**
   - Arquivo: [dist/TranscricaoAmbiental_Portatil.zip](file:///e:/IAGenMaster/2026/CMaker/Projetos/11-TranscricaoAmbiental/dist/TranscricaoAmbiental_Portatil.zip)

---

## 🌟 Principais Recursos da Aplicação

1. **Monitoramento de Tamanho de Arquivo e Espaço na Partição:**
   - **Tamanho do Arquivo:** Exibição dinâmica no topo da tela do tamanho acumulado do áudio em gravação (ex.: `📦 Arquivo: 45.2 MB`), atualizado a cada segundo.
   - **Espaço Livre na Partição:** Exibição em tempo real do espaço livre em disco da unidade de gravação (ex.: `💾 E: 142.3 GB livres` e detalhamento `142.3 GB livres de 476.8 GB - 29.8% livre`).
   - Alerta visual caso o espaço livre na partição fique abaixo de 10%.

2. **Diretório de Gravação Customizável e Persistente:**
   - Campo com botão **"Alterar Pasta..."** que abre o seletor nativo de diretórios do Windows.
   - A pasta escolhida é persistida automaticamente no arquivo `data/recorder_config.json`.
   - As subpastas `gravacoes/` e `transcricoes/` são criadas automaticamente no diretório selecionado.
   - Botão **"Abrir Pasta"** para abrir o local no Windows Explorer com um clique.

3. **Gravação Contínua e Organização por Dia:**
   - Gravação com streaming direto em disco no formato WAV (16 kHz, 16-bit mono), prevenindo sobrecarga de memória mesmo em sessões de 24 horas.
   - Rotatividade automática diária: na virada da meia-noite (00:00:00), o sistema finaliza os arquivos do dia anterior e abre os arquivos do novo dia.
   - Nomenclatura com data e hora: `gravacao_YYYY-MM-DD_HH-MM-SS.wav` e `transcricao_YYYY-MM-DD_HH-MM-SS.md`.

4. **Reprodutor de Áudio Local Integrado:**
   - Barra de reprodução inferior na própria janela com botões Play (▶), Pause (⏸), Stop (⏹) e barra de progresso.
   - Execução sonora nativa via hardware local (Pygame).

5. **Editor de Transcrições Embutido:**
   - Visualização e edição direta do arquivo Markdown selecionado em painel dedicado.
   - Botão "Salvar Alterações" para gravar modificações diretamente no arquivo `.md`.
   - Botão "Abrir Externo" para abrir no editor padrão do Windows (Bloco de Notas, VS Code, etc.).

6. **Recuperação Automática e Resiliência 24/7:**
   - Watchdog de áudio: se o microfone desconectar ou o stream travar por mais de 6 segundos, o sistema tenta restabelecer a captura sem intervenção humana.
   - Loop de resiliência no `iniciar_sistema.bat`: se o aplicativo sofrer uma queda inesperada, ele é reiniciado em 3 segundos.
   - Persistência de estado (`data/recorder_state.json`): ao reabrir o programa ou reiniciar o computador, a gravação é retomada automaticamente.

7. **Retenção Segura (Lixeira):**
   - Proibição de exclusão definitiva (*hard delete*). Qualquer áudio ou Markdown excluído é movido com segurança para a pasta `lixeira/` correspondente.

---

## 📁 Estrutura do Repositório

```
11-TranscricaoAmbiental/
├── README_IA.md               # Contexto executivo para agentes de IA (v1.0.7)
├── README.md                  # Documentação completa para humanos (v1.0.7)
├── iniciar_sistema.bat        # Atalho direto para abrir via Python
├── dist/                      # Pasta contendo o executável compilado
│   ├── TranscricaoAmbiental_Portatil.zip # Pacote ZIP completo para outro PC
│   └── TranscricaoAmbiental/  # Pasta autossuficiente com o .exe
│       ├── TranscricaoAmbiental.exe
│       ├── Iniciar_Transcricao.bat
│       └── models/            # Modelo offline Whisper
├── models/                    # Modelos de IA locais
├── gravacoes/                 # Diretório padrão de áudio (.wav)
├── transcricoes/              # Diretório padrão de Markdown (.md)
├── lixeira/                   # Diretório de retenção segura (sem hard delete)
├── data/                      # Arquivos de estado e configurações persistentes
└── scripts/
    ├── gerar_executavel.py    # Script que recompila a distribuição (.exe)
    ├── gui_app.py             # Aplicação Desktop nativa (CustomTkinter)
    ├── recorder.py            # Gravador resiliente e gerenciador de microfones
    ├── transcriber.py         # Motor Faster-Whisper de transcrição contínua
    ├── supervisor.py          # Supervisor de execução contínua com auto-restart
    └── lixeira.py             # Módulo de retenção segura
```
