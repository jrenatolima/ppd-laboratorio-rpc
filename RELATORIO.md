# Laboratório de RPC — Relatório Técnico
*(Atividade 1 — 30% | Atividade 2 — 70%)*

---

## 1. Identificação
- **Disciplina:** Programação Distribuída e Paralela
- **Integrantes do grupo:** _José Renato da Silva Lima, 1-2213760; Manoela de Paula Rangel Romanelli, 1- 2213460_

---

## 2. Objetivos
Implementar e validar duas aplicações cliente/servidor utilizando RPC sobre gRPC/Protobuf em Python:
- **Atividade 1:** Calculadora remota interativa (operações aritméticas básicas).
- **Atividade 2:** Servidor “minerador” com estado de transações e cliente com menu completo, incluindo mineração local multi‑thread e envio da solução para validação.

---

## 3. Ambiente e Ferramentas
- **Linguagem:** Python 3.10+
- **Tecnologia RPC:** gRPC com Protobuf (geração de *stubs*)
- **SO utilizado nos testes:** Windows 11 (PowerShell) — ambiente local
- **Dependências principais:** `grpcio`, `grpcio-tools` (referenciadas em `requirements.txt`)

---

## 4. Arquitetura e Interface RPC
As duas atividades seguem o mesmo padrão arquitetural:
- Definição de **interfaces** e **mensagens** em arquivos `.proto` (um por atividade).
- Geração de *stubs* do cliente e do servidor via `grpc_tools.protoc`.
- Implementação do **servidor** (métodos remotos) e do **cliente** (menu e chamadas RPC).
- Serialização binária via **Protobuf** e transporte via gRPC.

### 4.1 Atividade 1 — Calculadora
- **Serviço RPC:** operação única de cálculo recebendo o tipo de operação e dois operandos.
- **Cliente:** menu textual que coleta entrada do usuário e exibe o resultado.
- **Tratamento de erros:** divisão por zero retorna mensagem adequada ao usuário.
- **Critérios de aceite:** funcionalidades de soma, subtração, multiplicação e divisão disponíveis, com retorno correto e tratamento de erro.

### 4.2 Atividade 2 — Minerador
- **Estado mantido no servidor:** para cada `TransactionID` existem os campos `Challenge (1..20)`, `Solution`, `Winner` e `Status` (1 pendente / 0 resolvida).
- **Regras de validação (proof‑of‑work):** a solução `S` é válida quando o valor inteiro do SHA‑1 de `"{transaction_id}:{S}"` é múltiplo do `Challenge`. Formalmente: `int(SHA1(...), 16) % Challenge == 0`.
- **RPCs expostas:** `GetTransactionID`, `GetChallenge`, `GetTransactionStatus`, `SubmitChallenge`, `GetWinner`, `GetSolution`.
- **Cliente:** menu textual com todas as operações e uma ação **Mine** que: descobre a transação atual, obtém o desafio, busca localmente uma solução (multi‑thread) e submete ao servidor.
- **Ciclo de vida:** ao resolver uma transação, o servidor registra `Winner`/`Solution`, muda `Status` e cria automaticamente a próxima transação (ID sequencial) com novo desafio.

---

## 5. Procedimentos de Teste e Evidências

### 5.1 Atividade 1 — Calculadora
**Roteiro executado no vídeo:**
1. Iniciar servidor da calculadora (porta 50051).
2. Iniciar cliente em outro terminal e conectar em `localhost:50051`.
3. Demonstrar **soma**, **multiplicação** e **subtração** com valores simples.
4. Demonstrar **divisão por zero**, mostrando a mensagem de erro amigável.
5. Encerrar o cliente (`q`) e o servidor (Ctrl+C).

**Resultados observados:** operações retornaram valores corretos; divisão por zero tratada adequadamente; latência imperceptível em ambiente local.

### 5.2 Atividade 2 — Minerador
**Roteiro executado no vídeo:**
1. Iniciar servidor do minerador (porta 50052) — criação automática da transação `0`.
2. Abrir cliente e executar na sequência:  
   a) `getTransactionID` → obter o ID atual (ex.: `0`).  
   b) `getChallenge` → confirmar desafio no intervalo `[1..20]`.  
   c) `Mine` → mineração multi‑thread até encontrar solução válida e submeter (`code=1`).  
   d) `getTransactionStatus` (da transação resolvida) → `0`.  
   e) `getWinner` → retorno do `ClientID` vencedor.  
   f) `getSolution` → exibição de `{status=0, challenge, solution}`.  
   g) `getTransactionID` novamente → deve ser `1` (nova transação criada).

**Resultados observados:** a solução submetida foi aceita pelo servidor; os estados internos foram atualizados corretamente; a criação da próxima transação ocorreu automaticamente.

**Observações de robustez:**  
- Utilização de bloqueio **reentrante** no servidor (RLock) para evitar deadlock durante a criação de nova transação imediatamente após uma submissão válida.  
- Timeout aplicado na chamada de submissão do lado do cliente para evitar espera indefinida em caso de falha anômala.  
Esses pontos não alteram o requisito funcional, apenas tornam a solução mais resiliente.

---

## 6. Análise e Discussão
- **Aderência ao enunciado:** As operações e RPCs solicitadas foram implementadas e demonstradas. O cliente apresenta menus completos, e o servidor mantém o ciclo de vida das transações conforme especificado.
- **Desempenho da mineração:** O tempo de busca cresce com o valor do `Challenge`, como esperado, pois a probabilidade de acerto é aproximadamente `1/Challenge`. Em ambiente local, desafios baixos (ex.: 3–7) tendem a ser resolvidos rapidamente; desafios altos (ex.: 18–20) podem levar mais tentativas.
- **Concorrência:** O cliente usa múltiplas threads, o que melhora a chance de encontrar soluções mais rápido em máquinas com vários núcleos.
- **Portabilidade:** O uso de gRPC/Protobuf e Python favorece execução multiplataforma (Windows, macOS, Linux).

---

## 7. Conclusões
- **Atividade 1**: Calculadora gRPC implementada e validada com sucesso, incluindo tratamento de erros.  
- **Atividade 2**: Minerador gRPC com protocolo completo, mineração multi‑thread, atualização de estado no servidor e criação automática de novas transações — validado em testes.
- **Entregáveis**: código‑fonte, `README.md` detalhado, `requirements.txt`, vídeos de demonstração e este relatório técnico.