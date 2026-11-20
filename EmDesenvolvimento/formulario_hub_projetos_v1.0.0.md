# Dados para Preenchimento do Hub de Projetos CMaker

> **Documento de Apoio ao Cadastro no Hub de Projetos**
> **URL do Formulário:** `https://cmaker.com.br/projetos/hub/?r=admin/projetos/novo`
> **Projeto:** 11 - Transcrição Ambiental de Sala
> **Versão do Documento:** `v1.0.0` | **Data:** 20/11/2026
> **Status:** Pronto para Preenchimento e Cópia

---

## 📋 Guia Rápido de Preenchimento (Copiar e Colar)

Este documento foi estruturado exatamente na mesma ordem das seções e campos do formulário administrativo do Hub de Projetos (`admin/projetos/novo`). Basta copiar os valores das caixas abaixo e colar diretamente nos respectivos campos do navegador.

---

## Seção 1: Identificação Geral

### Título do Projeto *

> Campo obrigatório. Nome oficial completo da solução.

```text
Transcrição Ambiental de Sala: Aplicação Desktop 100% Local com Whisper
```

### Código do Projeto

> Código identificador do projeto.

```text
PRJ-2026-011
```

### Slug (URL Amigável)

> Identificador para a URL pública do projeto na vitrine do Hub.

```text
transcricao-ambiental-sala
```

### Resumo Executivo (Máximo 200 caracteres) *

> Texto conciso para cartões da vitrine e indexadores (exatamente 198 caracteres).

```text
Aplicação desktop 100% local em Python com Faster-Whisper, Pygame e CustomTkinter para gravação contínua e transcrição de áudio de sala em Markdown, operando offline e sem servidores.
```

### Descrição Completa e Objetivo da Solução *

> Apresentação detalhada da proposta, problema que resolve, metodologia, componentes e arquitetura técnica. Suporta formatação rica.

```markdown
### 1. Visão Geral e Problema Enfrentado
Ambientes acadêmicos, salas de aula maker, bancas de avaliação e sessões de trabalho produzem diariamente horas contínuas de discussões orais de alto valor que frequentemente se perdem por falta de registro integral. A utilização de ferramentas tradicionais de transcrição em nuvem impõe sérias restrições de privacidade de dados de estudantes e docentes, custos recorrentes por minuto gravado e dependência crítica de conexões de internet de alta velocidade.

O projeto **Transcrição Ambiental de Sala** resolve esse desafio desenvolvendo uma solução desktop nativa em Python que opera com estrito isolamento local: zero portas de rede abertas, zero servidor HTTP e zero envio de pacotes de áudio para nuvens públicas.

### 2. Arquitetura e Engenharia da Solução
A solução foi arquitetada em quatro pilares modulares e desacoplados:

1. **Motor de Captura e Gravação Resiliente (`recorder.py`):**
   - Gravação contínua em formato WAV PCM (16 kHz, mono, 16 bits), padrão ideal para modelos acústicos de inteligência artificial.
   - Buffer circular contínuo em memória dos últimos 5 segundos para telemetria em tempo real.
   - Medição ininterrupta de decibéis (dB) e VU meter dinâmico com suporte a mudo temporário sem corrupção do fluxo de gravação.

2. **Osciloscópio Acústico de Alta Precisão (`gui_app.py`):**
   - Renderização gráfica em tempo real dos últimos 5 segundos via Pillow (PIL) com traços verticais ultra-finos de 1 pixel (`width=1`) e passo uniforme de 3 pixels (`bar_step=3`), proporcionando espaçamento limpo de 2 pixels entre linhas.
   - Oscilação perfeitamente simétrica em torno do horizonte central (`cy`), espelhando padrões estéticos de referência acústica e eliminando borrões ou sobreposições.

3. **Motor de Transcrição Local com Inteligência Artificial (`transcriber.py`):**
   - Implementado com **Faster-Whisper** (CTranslate2), com inicialização em modelo base pré-carregado.
   - Mecanismo de fallback automático: detecta aceleração por GPU NVIDIA CUDA e, na ausência de binários compatíveis, migra automaticamente para CPU em quantização `int8`, garantindo execução universal sem travamentos.
   - Algoritmo de cálculo de horários reais: toma a data e hora do arquivo como referência do término da gravação, calcula a hora inicial subtraindo a duração total e projeta os carimbos temporais de cada fala para os horários exatos do relógio (`HH:MM:SS`), com suporte a virada de meia-noite.

4. **Reprodutor e Navegador Sonoro Interativo:**
   - Visualizador de ondas sonoras com playhead síncrono no Canvas, permitindo busca temporal instantânea (*seek*) ao clicar com o mouse sobre qualquer ponto da forma de onda.

### 3. Resultados e Impacto
- Mais de 10 horas contínuas de gravação e transcrição validadas em ambiente real com consumo estável de memória.
- Transcrição precisa com pontuação, identificação de turnos de fala e geração automática de arquivos Markdown estruturados (`.md`).
- Distribuição portável compilada em executável Windows standalone de um clique, sem requerer instalação de Python ou internet no computador de destino.
```

---

## Seção 2: Equipe de Estudantes e Orientação

### Integrantes / Participantes do Projeto

#### Integrante 1 (Desenvolvedor Principal / Líder):

- **Estudante / Integrante:** Digitar novo nome ou selecionar existente: `Fabricio`
- **Papel:** Selecionar `desenvolvedor` (Desenvolvedor) ou `lider` (Líder de Projeto)

#### Integrante 2 (Orientação / Coordenação Maker):

- **Estudante / Integrante:** Digitar novo nome: `Equipe Espaço CMaker`
- **Papel:** Selecionar `orientador` (Orientador)

---

## Seção 3: Gestão, Ciclo e Campos Extras

### Status do Projeto *

> Selecionar no menu suspenso:

- **Opção:** `concluido` -> **Concluído** (ou `em_andamento` caso pretenda manter em evolução contínua)

### Grau de Maturidade (Curadoria)

> Selecionar no menu suspenso:

- **Opção:** `producao` -> **Produção / Lançado** (solução com executável portátil gerado e testada em produção)

### Versão Semântica

> Versão atual estável do produto.

```text
v1.0.42
```

### Data de Início

> Data de início do desenvolvimento.

```text
2026-11-16
```

### Data de Término

> Data da conclusão da versão estável e entrega do executável.

```text
2026-11-20
```

### Marcos do Projeto (Linha do Tempo)

#### Marco 1:

- **Título do Marco:** Arquitetura do Sistema e Gravação Contínua de Áudio
- **Data:** `2026-11-16`
- **Situação:** Selecionar `concluido` (Concluído)

#### Marco 2:

- **Título do Marco:** Integração do Faster-Whisper Local com Fallback GPU/CPU
- **Data:** `2026-11-17`
- **Situação:** Selecionar `concluido` (Concluído)

#### Marco 3:

- **Título do Marco:** Reprodutor Local com Playhead Síncrono e Busca na Forma de Onda
- **Data:** `2026-11-18`
- **Situação:** Selecionar `concluido` (Concluído)

#### Marco 4:

- **Título do Marco:** Osciloscópio Acústico de 5s com Traços Finos e Agrupamento por Dia
- **Data:** `2026-11-19`
- **Situação:** Selecionar `concluido` (Concluído)

#### Marco 5:

- **Título do Marco:** Botão Único Contextual e Empacotamento em Executável Portátil
- **Data:** `2026-11-20`
- **Situação:** Selecionar `concluido` (Concluído)

---

## Seção 4: Dados Técnicos, Instituição e Links

### Instituição de Vínculo *

> Instituição ou espaço responsável pelo projeto.

```text
Espaço CMaker
```

### Tecnologias Utilizadas

> Lista com as principais linguagens, bibliotecas, frameworks e ferramentas aplicadas.

```text
Python 3.12, CustomTkinter, Faster-Whisper, CTranslate2, Pygame, SoundDevice, SoundFile, Pillow (PIL), NumPy, PyInstaller, CUDA, FFmpeg
```

### Tags, Hashtags ou Palavras-Chave (separadas por vírgula)

> Termos de indexação para a busca do Hub e filtros de categoria.

```text
transcricao, whisper, faster-whisper, audio, gravacao, acessibilidade, python, desktop, offline, cmaker, inteligencia-artificial, sounddevice, pygame, machine-learning, produtividade
```

### Repositório GitHub

> Link para o repositório do código-fonte (ajustar conforme sua organização no GitHub).

```text
https://github.com/espacocmaker/transcricao-ambiental
```

### Website / Demo / Site Oficial

> Link oficial ou página de demonstração (pode apontar para o Hub de Projetos).

```text
https://cmaker.com.br/projetos/hub/
```

### Instagram

> Perfil no Instagram do projeto ou da instituição maker.

```text
https://instagram.com/espacocmaker
```

### YouTube / Vídeo de Demonstração

> Link para vídeo pitch ou demonstração de funcionamento da aplicação (opcional).

```text
https://youtube.com/@espacocmaker
```

### Apresentação em Feiras ou Mostras Científicas / Makers

> Eventos, feiras de ciências, mostras maker ou bancas de inovação em que a solução foi exibida.

```text
Mostra de Projetos de Inovação Maker 2026 - Espaço CMaker
```

### Prêmios ou Menções

> Destaques, premiações ou reconhecimentos do projeto.

```text
Destaque em Privacidade e Eficiência Tecnológica para Inteligência Artificial Local
```

---

## Seção 5: Mídia, Capa e Galeria Fotográfica

### Orientações para Upload de Mídias

Para valorizar a exibição do projeto na vitrine pública do Hub:

1. **Foto de Capa Principal (Marcar a estrela ⭐ "Foto de Capa"):**

   - Captura de tela nítida da tela principal do aplicativo aberto com o osciloscópio em funcionamento e a tabela de gravações agrupada por dia.
   - Classificação recomendada: Selecionar `print_tela` (Print de Tela).
   - Legenda sugerida: `Interface principal do Transcrição Ambiental com osciloscópio sonoro e lista cronológica`.
2. **Imagens Adicionais para a Galeria:**

   - **Imagem 2 (Osciloscópio ao Vivo):** Recorte aproximado do visualizador de ondas dos últimos 5 segundos com traços finos de 1px em azul neon e fundo escuro.*Classificação:* `teste` (Teste / Validação) | *Legenda:* `Osciloscópio acústico dos últimos 5 segundos em tempo real`.
   - **Imagem 3 (Editor e Transcrição Markdown):** Tela exibindo uma transcrição finalizada com horários reais e o editor integrado de texto.*Classificação:* `print_tela` (Print de Tela) | *Legenda:* `Painel de transcrições com horários reais e editor de Markdown integrado`.
   - **Imagem 4 (Pacote Portátil):** Captura da pasta de distribuição com o executável portátil `.exe` e o pacote compactado `.zip`.
     *Classificação:* `prototipo` (Protótipo Concluído) | *Legenda:* `Pacote executável Windows standalone pronto para uso offline sem instalação`.

---

## Seção 6: Controle, Governança e Publicação

### Visibilidade do Projeto *

> Selecionar no menu suspenso:

- **Opção:** `publico` -> **Público (Exibido na vitrine geral)**

### Status de Publicação *

> Selecionar no menu suspenso:

- **Opção:** `aprovado` -> **🟢 Publicado (Aprovado na Vitrine)**

### Divulgação Pública Autorizada

> Caixa de seleção (checkbox).

- **Ação:** **Marcar como Ativado (Checked)** (`consentimento_divulgacao = 1`)

### Fixar em Destaque no Cabeçalho da Vitrine

> Caixa de seleção (checkbox).

- **Ação:** **Marcar como Ativado (Checked)** (`destaque = 1`)

### Nota de Maturidade (0.0 a 10.0)

> Avaliação técnica da maturidade da solução.

```text
10.0
```

### Parecer Técnico Interno da Moderação

> Avaliação interna dos revisores para documentar a qualidade técnica do projeto no banco de dados.

```text
Projeto aprovado com distinção técnica máxima: código-fonte 100% nativo em Python, arquitetura estritamente local sem tráfego de rede ou dependência de servidores web externos. Motor de transcrição offline Faster-Whisper plenamente integrado com fallback automático entre GPU e CPU, tratamento rigoroso de horários reais com virada de dia, osciloscópio em tempo real com excelente nitidez visual e suíte automatizada de testes passando com 100% de sucesso. Executável portátil standalone compilado com êxito, pronto para implantação imediata em ambientes educacionais e de pesquisa.
```
