# Especificação de Melhorias — Gravador de Sons Ambiente

**Versão:** 1.0  
**Data:** 17/11/2026  
**Finalidade:** instruções para uma ferramenta de desenvolvimento modificar o projeto existente, preservando as funções atuais.

## 1. Objetivo e contexto
O sistema será utilizado para registrar aulas, atividades do Espaço Maker, bancas acadêmicas, reuniões, discussões técnicas e ideias de projetos. Prioridades: integridade do áudio original, processamento confiável de gravações longas, rastreabilidade e interface responsiva.

**Antes de alterar o código:** analisar arquitetura, tecnologias, dependências, fluxo de gravação/transcrição e logs existentes. Não reescrever componentes funcionais sem necessidade. Preservar a barra de porcentagem já existente.

## 2. Aba Configurações
Criar uma aba **Configurações** contendo:
- [ ] **Transcrever automaticamente ao parar a gravação**.
- [ ] **Gerar ata automaticamente após a transcrição**.

As opções são independentes, persistidas em configuração local e restauradas após reiniciar o programa. Se a geração de ata estiver habilitada, mas não existir transcrição, oferecer processamento da transcrição como dependência (sem descartar a preferência do usuário). Exibir o estado de cada tarefa.

## 3. Fluxo automático
1. Ao iniciar gravação: criar identificador único, salvar data/hora e registrar log.
2. Ao parar: finalizar e validar o arquivo de áudio; nunca depender do sucesso da transcrição para preservar o áudio.
3. Se habilitado, enfileirar a transcrição do **último áudio finalizado**.
4. Ao concluir a transcrição, identificar título contextual e salvar transcrição.
5. Se habilitado, gerar ata com base na transcrição completa.
6. Atualizar nomes e metadados com segurança; exibir links/caminhos para os arquivos.
7. Evitar tarefas duplicadas após cliques repetidos, reinício ou recuperação.

## 4. Organização e nomes dos arquivos
Formato sugerido: `AAAA-MM-DD_HH-MM-SS_Titulo-Contextual.ext`.

Exemplos:
- `2026-11-17_19-30-00_Discussao-Projeto-Robotica.wav`
- `2026-11-17_19-30-00_Discussao-Projeto-Robotica_transcricao.md`
- `2026-11-17_19-30-00_Discussao-Projeto-Robotica_ata.md`

Usar data/hora **do início da gravação**, fuso local configurado, título conciso extraído do conteúdo e caracteres seguros para o sistema de arquivos. Antes da transcrição, utilizar identificador/data-hora provisórios. Renomear de forma atômica, atualizar referências e impedir colisões/sobrescritas. Caso a transcrição falhe, manter o áudio com nome provisório e recuperável.

## 5. Transcrição
- Preservar texto completo, ordem cronológica e marcações temporais por trecho quando disponíveis.
- Identificar interlocutores somente quando a tecnologia permitir, sinalizando incerteza; não atribuir nomes sem evidência.
- Processar áudios longos por segmentos com sobreposição quando necessário, mantendo timestamps absolutos e evitando cortes ou duplicações.
- Salvar resultados parciais e checkpoints por segmento; permitir retomar após falha.
- Exibir progresso real, baseado em etapas/segmentos concluídos; nunca simular porcentagem.
- Executar processamento fora da thread principal da interface, com fila e limites de concorrência.

## 6. Ata automática
Gerar arquivo Markdown com:
- Título contextual, data, horário de início e fim e duração da gravação.
- Participantes identificados e participantes não identificados, conforme evidência.
- Contexto e objetivo do encontro, quando disponíveis.
- Principais assuntos, com referências temporais quando possível.
- Decisões, encaminhamentos, responsáveis, prazos e pendências.
- Síntese final.

**Regra obrigatória:** não inventar fatos, participantes, decisões ou prazos. Quando não identificados, usar “Não identificado na gravação”. Distinguir discussão, sugestão e decisão efetiva.

## 7. Diagnóstico e correção de travamentos
Investigar antes de corrigir:
- Uso de RAM, CPU, disco e espaço livre durante áudios extensos.
- Carregamento integral de áudio na memória.
- Deadlocks, chamadas síncronas na thread de interface, vazamento de recursos.
- Timeouts de modelos locais ou serviços externos.
- Problemas em segmentação, I/O, atualização de progresso e tratamento de exceções.

Registrar causa raiz e correção aplicada. Introduzir segmentação, fila de trabalho, limites de memória, escrita incremental, checkpoints e retomada idempotente quando apropriado. Nunca reiniciar automaticamente uma gravação em andamento sem estratégia comprovada de preservação do áudio.

## 8. Watchdog e recuperação
Monitorar heartbeat e avanço efetivo de cada tarefa, distinguindo etapas naturalmente lentas de travamentos. Tornar limites de inatividade configuráveis e registrar:
- Identificador da tarefa, etapa, último progresso, tempo sem avanço e diagnóstico.
- Detecção de timeout, tentativa de cancelamento controlado e reinício **somente do worker afetado**.
- Retomada a partir do último checkpoint íntegro.
- Tentativas limitadas, com espera progressiva e estado final de falha recuperável.

Evitar ciclos infinitos. Não apagar áudio original, transcrições parciais ou logs. Permitir recuperação manual quando a automática não for possível.

## 9. Aba de logs e auditoria
Na área de Configurações, disponibilizar painel cronológico com data/hora, nível (INFO/WARN/ERROR), módulo, tarefa e mensagem. Eventos mínimos:
- Gravação iniciada, interrompida, concluída e arquivo validado.
- Transcrição iniciada, progresso, segmento concluído, finalização e erro.
- Ata iniciada, concluída ou com falha.
- Watchdog acionado, diagnóstico, recuperação tentada e resultado.
- Alterações de configurações, renomeações e reinicializações.

Persistir logs em arquivo com rotação e limite de tamanho. Permitir filtro, pesquisa e exportação. Evitar registrar conteúdo sensível de conversas nos logs técnicos.

## 10. Segurança, privacidade e consentimento
Como haverá gravações de aulas, bancas e conversas de terceiros, prever informação clara sobre a captação e obtenção de consentimento ou outra base legal adequada conforme o contexto. Definir retenção, exclusão, controle de acesso e proteção dos arquivos. Informar quando a transcrição ou ata utilizar serviços externos; não enviar áudio a terceiros sem configuração e autorização apropriadas.

## 11. Critérios de aceitação e testes
1. Checkboxes mantêm seus valores após fechar e reabrir a aplicação.
2. Parar gravação dispara somente as tarefas habilitadas.
3. Áudio original permanece íntegro mesmo com erro de transcrição/ata.
4. Arquivos possuem data, hora e título contextual quando possível, sem colisões.
5. Transcrição de gravação longa não congela a interface; progresso continua coerente.
6. Falha simulada no meio do processamento é registrada e permite retomada do checkpoint.
7. Watchdog detecta estagnação real e limita tentativas de recuperação.
8. Logs persistem entre sessões e permitem identificar a causa de erros.
9. Ata contém campos especificados e não inventa informações ausentes.
10. Fluxos existentes continuam funcionando (testes de regressão).

Testar gravações curtas e longas, áudio silencioso, múltiplos falantes, pouco espaço em disco, falta de rede, encerramento inesperado, reinício do aplicativo e falha de worker.

## 12. Entregáveis esperados da ferramenta de desenvolvimento
- Código alterado, mantendo compatibilidade com o projeto existente.
- Diagnóstico documentado dos travamentos encontrados.
- Configurações persistentes e interface de logs.
- Watchdog, checkpoints e recuperação automática.
- Exemplos reais de arquivos gerados e evidências dos testes.
- Instruções de instalação/atualização, dependências e limitações conhecidas.

**Prioridade máxima:** nunca perder a gravação original e nunca bloquear a interface por causa de transcrição ou geração de ata.
