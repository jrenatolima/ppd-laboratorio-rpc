# RPC Lab — Atividade 1 (30%) e Atividade 2 (70%) — Guia Completo

Este repositório entrega as **duas atividades** do laboratório de RPC em Python/gRPC
- **Atividade 1 — `calc_rpc/`**: Calculadora via gRPC (cliente com menu interativo)
- **Atividade 2 — `miner_grpc/`**: “Minerador” com servidor gRPC e cliente (menu + mineração multi-thread)

---

## 1) Pré‑requisitos

- **Python 3.10+** (recomendado 3.10 ou 3.11).
- `pip` funcional.
- Acesso de terminal (PowerShell no Windows; Terminal no macOS/Linux).

---

## 2) Estrutura do projeto

```
rrpc_lab/
├─ calc_rpc/                  # ATIVIDADE 1
│  ├─ calc.proto              # definição do serviço/mensagens
│  ├─ client.py               # cliente (menu)
│  ├─ server.py               # servidor (porta padrão 50051)
│  └─ (gerados) calc_pb2*.py  # stubs gRPC (gerados pelo protoc)
│
├─ miner_grpc/                # ATIVIDADE 2
│  ├─ miner.proto             # definição do serviço/mensagens
│  ├─ client.py               # cliente (menu + mineração multi-thread)
│  ├─ server.py               # servidor (porta padrão 50052)
│  └─ (gerados) miner_pb2*.py # stubs gRPC (gerados pelo protoc)
│
├─ requirements.txt
└─ README.md
```

---

## 3) Instalar dependências e preparar ambiente

**IMPORTANTE:** Execute `pip install -r requirements.txt` **na raiz do projeto (`rpc_lab/`)**.
Se você estiver dentro de `calc_rpc/` ou `miner_grpc/`, use caminho relativo:

- No Windows: `pip install -r ..\requirements.txt`
- No macOS/Linux: `pip install -r ../requirements.txt`


> Recomenda-se usar **ambiente virtual** (venv) para isolar as dependências.

### 3.1 Windows (PowerShell)
```powershell
#entrar na RAIZ do projeto (onde está requirements.txt)
cd C:\caminho\para\rpc_lab

#criar e ativar venv (desbloqueando scripts somente nesta sessão)
py -m venv .venv
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process
.\.venv\Scripts\Activate.ps1

#instalar dependências (na RAIZ)
pip install -r requirements.txt

#checar versão do Python (opcional)
py --version
```


### 3.2 macOS / Linux
```bash
#entrar no diretório do projeto
cd /caminho/para/rrpc_lab

#criar e ativar venv
python3 -m venv .venv
source .venv/bin/activate

#instalar dependências
pip install -r requirements.txt

#checar versão do Python (opcional)
python --version
```

> Para sair do venv: `deactivate`.

---

## 4) **Gerar os stubs gRPC** (obrigatório antes de rodar)

Os arquivos `*_pb2.py` e `*_pb2_grpc.py` **não** estão comitados. Gere-os com o `grpc_tools.protoc`.  
> Rode os comandos **dentro das pastas** `calc_rpc` e `miner_grpc`.

### 4.1 Atividade 1 — `calc_rpc`
Windows/macOS/Linux (mesmo comando):
```bash
cd calc_rpc
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. ./calc.proto
```
Espera gerar:
- `calc_pb2.py`
- `calc_pb2_grpc.py`

### 4.2 Atividade 2 — `miner_grpc`
```bash
cd ../miner_grpc
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. ./miner.proto
```
Espera gerar:
- `miner_pb2.py`
- `miner_pb2_grpc.py`

> **Erros comuns**:  
> - `ModuleNotFoundError: calc_pb2` (ou `miner_pb2`) → stubs não gerados ou rodando fora da pasta correta.  
> - Permissões no Windows → rode o terminal “como Administrador” caso necessário.

---

## 5) Executar **Atividade 1** (Calculadora gRPC)

### 5.1 Subir o servidor (porta padrão **50051**)
No mesmo **terminal** dos passos anteriores:
```bash
cd <sua_pasta>/rrpc_lab/calc_rpc
python server.py
```
Saída esperada:
```
Calculator gRPC server listening on 0.0.0.0:50051
```

### 5.2 Rodar o cliente (menu interativo)
Abra **outro terminal** (Terminal B):
```bash
cd <sua_pasta>/rrpc_lab

Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process

.\.venv\Scripts\Activate.ps1

cd <sua_pasta>/rrpc_lab/calc_rpc

python client.py  #conecta em localhost:50051

#ou: python client.py 127.0.0.1:50051
```
Exemplo de sessão:
```
=== CALCULADORA RPC ===
1) Soma
2) Subtração
3) Multiplicação
4) Divisão
q) Sair
Escolha: 1
a = 7
b = 5
Resultado = 12.0
```
- **Divisão por zero** retorna erro

- **Encerrar**: digite `q` no cliente. Para parar o servidor, `Ctrl+C` no Terminal A

> **Porta ocupada?** Edite `server.py`, mude `50051` para `50061`, salve e reinicie. No cliente, passe o novo `host:porta`

---

## 6) Executar **Atividade 2** (Minerador gRPC)

### 6.1 Subir o servidor (porta padrão **50052**)
Abra **um terminal** (Terminal A):
```bash
cd <sua_pasta>/rrpc_lab/miner_grpc
python server.py
```
Saída esperada:
```
Miner gRPC server listening on 0.0.0.0:50052
[SERVER] Nova transação criada: id=0, challenge=...
```

### 6.2 Rodar o cliente (menu + mineração)
Abra **outro terminal** (Terminal B):
```bash
cd <sua_pasta>/rrpc_lab

Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process

.\.venv\Scripts\Activate.ps1

cd <sua_pasta>/rrpc_lab/miner_grpc

python client.py                # usa ClientID=1 por padrão
# ou: python client.py 127.0.0.1:50052 2   # ClientID=2
```
Menu do cliente:
```
=== MINER MENU ===
1) getTransactionID
2) getChallenge
3) getTransactionStatus
4) getWinner
5) getSolution
6) Mine (multi-thread) e Submit
q) Sair
```

#### Dicas de uso:
1. **1) getTransactionID** → veja a transação atual (ex.: `0`).  
2. **2) getChallenge** → informe `transactionID` para ver o `challenge` (1..20).  
3. **6) Mine** → o cliente busca uma **solução** localmente usando **múltiplas threads** (quantidade ≈ núm. de CPUs).
   - Regra implementada (*proof-of-work*):  
     Uma `solution S` é **válida** se  
     `int(sha1(f"{transaction_id}:{S}"), 16) % challenge == 0`.  
     Quanto maior o `challenge`, mais difícil (probabilidade ≈ `1/challenge`).  
   - Após encontrar, o cliente chama `SubmitChallenge`:
     - **1** = válida
     - **0** = inválida
     - **2** = já resolvida
     - **-1** = transação inválida
4. **3) getTransactionStatus** → `1` pendente; `0` resolvida; `-1` inválida.  
5. **4) getWinner** → retorna o `ClientID` vencedor (`0` se ninguém ainda, `-1` se inválida).  
6. **5) getSolution** → mostra `{status, challenge, solution}` da transação.

> Quando uma transação é resolvida, o servidor **cria automaticamente** a próxima (`TransactionID`+1, `challenge` aleatório em [1..20]).
> Você pode ver isso repetindo as opções 1 e 2.