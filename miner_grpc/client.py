import grpc
import sys
import time
import hashlib
import threading
import os

import miner_pb2
import miner_pb2_grpc

def sha1_hex(s: str) -> str:
    return hashlib.sha1(s.encode()).hexdigest()

def mine_solution(transaction_id: int, challenge: int, threads: int = os.cpu_count() or 4, timeout_s: int = 0):
    """Procura uma string S tal que int(sha1(f"{transaction_id}:{S}"),16) % challenge == 0.
    Usa múltiplas threads até encontrar. Retorna S.
    """
    found = {"flag": False, "solution": None}
    lock = threading.Lock()

    def worker(start_nonce: int, step: int):
        nonce = start_nonce
        base = f"{transaction_id}:{time.time_ns()}"
        while True:
            with lock:
                if found["flag"]:
                    return
            s = f"{base}:{nonce}"
            h = int(sha1_hex(s), 16)
            if h % challenge == 0:
                with lock:
                    if not found["flag"]:
                        found["flag"] = True
                        found["solution"] = s.split(":", 1)[1]  # retorna só a parte depois do transaction_id:
                return
            nonce += step

    ths = []
    for i in range(threads):
        t = threading.Thread(target=worker, args=(i, threads), daemon=True)
        t.start()
        ths.append(t)

    start = time.time()
    while True:
        with lock:
            if found["flag"]:
                return found["solution"]
        if timeout_s and (time.time() - start) > timeout_s:
            return None
        time.sleep(0.05)

def print_menu():
    print("\n=== MINER MENU ===")
    print("1) getTransactionID")
    print("2) getChallenge")
    print("3) getTransactionStatus")
    print("4) getWinner")
    print("5) getSolution")
    print("6) Mine (multi-thread) e Submit")
    print("q) Sair")

def run(target: str, client_id: int):
    with grpc.insecure_channel(target) as channel:
        stub = miner_pb2_grpc.MinerStub(channel)
        while True:
            print_menu()
            op = input("Escolha: ").strip().lower()
            if op == "q": break

            if op == "1":
                tx = stub.GetTransactionID(miner_pb2.Empty())
                print(f"TransactionID atual: {tx.id}")
            elif op == "2":
                tid = int(input("transactionID: "))
                ch = stub.GetChallenge(miner_pb2.TransactionID(id=tid))
                print(f"Desafio da transação {tid}: {ch.challenge}")
            elif op == "3":
                tid = int(input("transactionID: "))
                st = stub.GetTransactionStatus(miner_pb2.TransactionID(id=tid))
                print(f"Status da transação {tid}: {st.status} (1=pendente, 0=resolved, -1=inválida)")
            elif op == "4":
                tid = int(input("transactionID: "))
                w = stub.GetWinner(miner_pb2.TransactionID(id=tid))
                print(f"Winner de {tid}: {w.winner}")
            elif op == "5":
                tid = int(input("transactionID: "))
                sol = stub.GetSolution(miner_pb2.TransactionID(id=tid))
                print(f"Solution de {tid}: status={sol.status}, challenge={sol.challenge}, solution='{sol.solution}'")
            elif op == "6":
                tx = stub.GetTransactionID(miner_pb2.Empty())
                ch = stub.GetChallenge(miner_pb2.TransactionID(id=tx.id))
                if ch.challenge <= 0:
                    print("Transação inválida.")
                    continue
                print(f"Minerando transação {tx.id} com challenge={ch.challenge}...")
                s = mine_solution(tx.id, ch.challenge)
                if s is None:
                    print("Não encontrou solução no tempo limite.")
                    continue
                print(f"Solução encontrada localmente: '{s}'")
                resp = stub.SubmitChallenge(miner_pb2.SubmitRequest(
                    transaction_id=tx.id,
                    client_id=client_id,
                    solution=s
                ))
                print(f"Resposta do servidor: code={resp.code} (1=válida, 0=inválida, 2=já resolvida, -1=trans inválida)")
            else:
                print("Opção inválida.")

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "localhost:50052"
    client_id = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    print(f"Conectando a {target} como ClientID={client_id}...")
    run(target, client_id)
