# Estrutura técnica do backend

## Visão geral

Este documento descreve os ficheiros e áreas principais do backend `Trader-Bot`, separado do frontend `TraderBotWeb`.

A responsabilidade deste projeto é servir API, WebSocket, candles, runs, métricas, stage tests, estratégias, integração com providers e persistência local.

---

## Estrutura principal

```text
app/
  api/
  core/
  engine/
  indicators/
  models/
  providers/
  registry/
  schemas/
  services/
  stage_tests/
  storage/
  strategies/
  utils/
  main.py
```

---

## Ficheiros e áreas principais

## app/main.py

**Função:**
Ponto de entrada da API.

**Responsabilidade:**
Inicializar a aplicação FastAPI, configurar logging, CORS, router principal e criação de tabelas.

**Usado por:**
Execução principal do backend.

**Entrada:**
Settings, router da API e configuração da aplicação.

**Saída:**
Aplicação HTTP pronta a servir frontend e clientes.

**Atenção:**
Mudanças aqui afetam a inicialização global do backend.

---

## app/core/settings.py

**Função:**
Centralizar configuração da aplicação.

**Responsabilidade:**
Definir ambiente, debug, host, porta, timezone, provider, API keys, base de dados e parâmetros de sync/cache.

**Usado por:**
Todo o backend.

**Entrada:**
Variáveis de ambiente e defaults internos.

**Saída:**
Objeto/configuração de settings.

**Atenção:**
Alterações podem afetar provider, base de dados, CORS e comportamento global.

---

## app/api/v1/router.py

**Função:**
Router central da API.

**Responsabilidade:**
Agrupar os endpoints versionados em `/api/v1`.

**Usado por:**
`app/main.py`

**Entrada:**
Routers parciais de candles, runs, strategies, stage tests, ws e outros.

**Saída:**
API organizada por módulos.

**Atenção:**
Qualquer mudança aqui pode quebrar o contrato esperado pelo frontend.

---

## app/api/v1/endpoints/candles.py

**Função:**
Expor endpoint de candles.

**Responsabilidade:**
Receber símbolo/timeframe/janela, validar parâmetros, sincronizar quando necessário e devolver candles ao frontend.

**Usado por:**
Frontend e fluxos de diagnóstico.

**Entrada:**
Parâmetros de mercado e janela temporal.

**Saída:**
Candles normalizados e metadados de resposta.

**Atenção:**
É um dos endpoints mais sensíveis do sistema.

---

## app/api/v1/endpoints/ws.py

**Função:**
Expor atualização em tempo real por WebSocket.

**Responsabilidade:**
Transmitir eventos de mercado e atualização contínua para o frontend.

**Usado por:**
`useRealtimeFeed.ts` e painel principal.

**Entrada:**
Símbolo, timeframe e contexto do feed.

**Saída:**
Mensagens em tempo real para o frontend.

**Atenção:**
Afeta diretamente a experiência do gráfico e do dashboard.

---

## app/services/candle_sync.py

**Função:**
Sincronizar candles com a origem de dados.

**Responsabilidade:**
Gerir fetch e sincronização entre provider e base local.

**Usado por:**
Endpoint de candles e fluxos de atualização.

**Entrada:**
Símbolo, timeframe, intervalo e settings.

**Saída:**
Base local atualizada e candles disponíveis.

**Atenção:**
É central para consistência entre provider, cache e frontend.

---

## app/services/candle_cache_sync.py

**Função:**
Gerir cache e sincronização auxiliar de candles.

**Responsabilidade:**
Reduzir fetches desnecessários e organizar atualização incremental/local.

**Usado por:**
Fluxos de candles e realtime.

**Entrada:**
Pedidos de candles e estado local.

**Saída:**
Dados de candles disponíveis com menor custo de provider.

**Atenção:**
Impacta cobertura, desempenho e consumo de quota.

---

## app/services/realtime_ws.py

**Função:**
Orquestrar feed em tempo real.

**Responsabilidade:**
Produzir eventos de atualização contínua para o WebSocket.

**Usado por:**
Endpoint WS.

**Entrada:**
Símbolo, timeframe, provider, cache e estado do sistema.

**Saída:**
Mensagens de atualização para o frontend.

**Atenção:**
É uma peça sensível para estabilidade visual do gráfico.

---

## app/providers/base.py

**Função:**
Definir contrato base dos providers.

**Responsabilidade:**
Estabelecer interface comum para as fontes de dados de mercado.

**Usado por:**
Factory e providers concretos.

**Entrada:**
Chamadas de mercado padronizadas.

**Saída:**
Contrato reutilizável para providers.

**Atenção:**
Mudanças aqui exigem alinhamento de todos os providers.

---

## app/providers/factory.py

**Função:**
Escolher e instanciar provider.

**Responsabilidade:**
Resolver qual provider será usado com base na configuração.

**Usado por:**
Services de candles e realtime.

**Entrada:**
Settings e nome do provider.

**Saída:**
Instância concreta do provider.

**Atenção:**
Erro aqui pode impedir qualquer obtenção de dados de mercado.

---

## app/providers/twelvedata.py

**Função:**
Integrar com TwelveData.

**Responsabilidade:**
Buscar dados de mercado reais quando o provider configurado for `twelvedata`.

**Usado por:**
Factory e serviços de candles.

**Entrada:**
Símbolo, timeframe, janela temporal e API key.

**Saída:**
Candles convertidos para o formato interno.

**Atenção:**
É um ponto sensível por quota, cooldown e tratamento de erro externo.

---

## app/engine/run_engine.py

**Função:**
Executar runs.

**Responsabilidade:**
Coordenar a execução lógica de runs e seus resultados.

**Usado por:**
Endpoints e fluxos de análise.

**Entrada:**
Estratégias, candles, parâmetros e contexto de execução.

**Saída:**
Resultados de runs.

**Atenção:**
Mudanças aqui afetam o núcleo analítico do backend.

---

## app/engine/case_engine.py

**Função:**
Executar lógica por caso.

**Responsabilidade:**
Avaliar e produzir casos de análise no contexto das runs.

**Usado por:**
Run engine, métricas e detalhe de resultados.

**Entrada:**
Candles, regras e contexto analítico.

**Saída:**
Casos calculados.

**Atenção:**
Impacta diretamente resultados e diagnóstico operacional.

---

## app/engine/metrics_engine.py

**Função:**
Calcular métricas.

**Responsabilidade:**
Transformar resultados de execução em métricas consumidas pela API e pelo frontend.

**Usado por:**
Endpoints de métricas e visão resumida de runs.

**Entrada:**
Resultados brutos das execuções.

**Saída:**
Indicadores e métricas agregadas.

**Atenção:**
Qualquer alteração precisa manter consistência com o que o frontend espera mostrar.

---

## app/strategies/

**Função:**
Conter as estratégias de análise.

**Responsabilidade:**
Definir regras, decisões, catálogos e mapeamentos de estratégias.

**Usado por:**
Run engine, stage tests e endpoints de estratégias.

**Entrada:**
Candles, indicadores e parâmetros.

**Saída:**
Sinais, decisões e estruturas de estratégia.

**Atenção:**
É uma área crítica do domínio do sistema.

---

## app/stage_tests/

**Função:**
Executar testes por estágio.

**Responsabilidade:**
Disponibilizar catálogo, runner e mapeamentos de Stage Tests.

**Usado por:**
Endpoints de stage tests e interface do frontend.

**Entrada:**
Parâmetros de teste, estratégias e contexto.

**Saída:**
Resultados de testes por estágio.

**Atenção:**
Deve permanecer coerente com a forma como o frontend consome e mostra os testes.

---

## app/storage/

**Função:**
Persistência local e acesso a dados.

**Responsabilidade:**
Gerir modelos, repositórios, queries e acesso à base SQLite.

**Usado por:**
Services, engine, stage tests e API.

**Entrada:**
Objetos de domínio, candles, runs, métricas e casos.

**Saída:**
Leitura e escrita persistente.

**Atenção:**
Alterações aqui impactam toda a camada de dados do sistema.

---

## app/indicators/

**Função:**
Calcular indicadores técnicos.

**Responsabilidade:**
Fornecer ATR, EMA, SMA, RSI, MACD, Bollinger e outros cálculos auxiliares.

**Usado por:**
Strategies, engines e stage tests.

**Entrada:**
Séries de candles.

**Saída:**
Indicadores derivados.

**Atenção:**
Mudanças aqui podem alterar sinais e resultados de estratégias.

---

## Regras de arquitetura

### Separação de responsabilidades
- backend: provider, sync, execução, persistência e API
- frontend: interface, gráfico e experiência do utilizador

### Regra de contrato com o frontend
O backend deve continuar a devolver dados de forma previsível para que o frontend possa:
- manter o último snapshot válido
- distinguir erro, cobertura insuficiente e feed parado
- mostrar diagnósticos sem perder o gráfico
