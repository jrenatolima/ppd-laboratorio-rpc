import grpc
from concurrent import futures
import time
import random
import hashlib
import threading

import miner_pb2
import miner_pb2_grpc

# Regra de "prova de trabalho" escolhida (documento não fixa uma regra específica):
# Para uma dada transaction_id e challenge C (1..20), a solução S é válida se:
# int(SHA1(f"{transaction_id}:{S}").hexdigest(), 16) % C == 0
# - C=1 é trivial (sempre 0), mais fácil.
# - C maior torna a busca mais difícil (probabilidade ~1/C).
def is_valid_solution(transaction_id: int, solution: str, challenge: int) -> bool:
    h = hashlib.sha1(f"{transaction_id}:{solution}".encode()).hexdigest()
    return int(h, 16) % challenge == 0

class MinerServicer(miner_pb2_grpc.MinerServicer):
    def __init__(self):
        # transactions: {id: {"challenge": int, "solution": str|"", "winner": int, "status": 1|0}}
        self.transactions = {}
        self.lock = threading.RLock()
        self.current_id = 0
        self._create_new_transaction(initial=True)

    def _create_new_transaction(self, initial=False):
        with self.lock:
            if not initial:
                self.current_id += 1
            challenge = random.randint(1, 20)
            self.transactions[self.current_id] = {
                "challenge": challenge,
                "solution": "",
                "winner": -1,
                "status": 1,  # 1 pendente, 0 resolvido
            }
            print(f"[SERVER] Nova transação criada: id={self.current_id}, challenge={challenge}")

    def GetTransactionID(self, request, context):
        with self.lock:
            # Garante que temos uma pendente; se a atual estiver resolvida, cria outra
            if self.transactions[self.current_id]["status"] == 0:
                self._create_new_transaction()
            return miner_pb2.TransactionID(id=self.current_id)

    def _get_tx(self, tid: int):
        return self.transactions.get(tid, None)

    def GetChallenge(self, request, context):
        tx = self._get_tx(request.id)
        if tx is None:
            return miner_pb2.ChallengeResponse(transaction_id=request.id, challenge=-1)
        return miner_pb2.ChallengeResponse(transaction_id=request.id, challenge=tx["challenge"])

    def GetTransactionStatus(self, request, context):
        tx = self._get_tx(request.id)
        if tx is None:
            return miner_pb2.StatusResponse(status=-1)
        return miner_pb2.StatusResponse(status=tx["status"])  # 1 pendente, 0 resolvido

    def SubmitChallenge(self, request, context):
        tx = self._get_tx(request.transaction_id)
        if tx is None:
            return miner_pb2.SubmitResponse(code=-1)
        if tx["status"] == 0:
            return miner_pb2.SubmitResponse(code=2)

        # Validar
        if is_valid_solution(request.transaction_id, request.solution, tx["challenge"]):
            with self.lock:
                # Dupla checagem
                tx = self._get_tx(request.transaction_id)
                if tx is None:
                    return miner_pb2.SubmitResponse(code=-1)
                if tx["status"] == 0:
                    return miner_pb2.SubmitResponse(code=2)

                tx["solution"] = request.solution
                tx["winner"] = request.client_id
                tx["status"] = 0  # resolvido
                print(f"[SERVER] Transação {request.transaction_id} resolvida por {request.client_id}. Solução='{request.solution}'")
                # Prepara próxima transação
                if request.transaction_id == self.current_id:
                    self._create_new_transaction()
            return miner_pb2.SubmitResponse(code=1)
        else:
            return miner_pb2.SubmitResponse(code=0)

    def GetWinner(self, request, context):
        tx = self._get_tx(request.id)
        if tx is None:
            return miner_pb2.WinnerResponse(winner=-1)
        w = tx["winner"]
        if tx["status"] == 1:
            # sem vencedor ainda
            return miner_pb2.WinnerResponse(winner=0)
        return miner_pb2.WinnerResponse(winner=w)

    def GetSolution(self, request, context):
        tx = self._get_tx(request.id)
        if tx is None:
            return miner_pb2.SolutionResponse(status=-1, solution="", challenge=-1)
        return miner_pb2.SolutionResponse(
            status=tx["status"],
            solution=tx["solution"] if tx["status"] == 0 else "",
            challenge=tx["challenge"]
        )

def serve(port: int = 50052):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=16))
    miner_pb2_grpc.add_MinerServicer_to_server(MinerServicer(), server)
    server.add_insecure_port(f"[::]:{port}")
    print(f"Miner gRPC server listening on 0.0.0.0:{port}")
    server.start()
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        print("Shutting down...")
        server.stop(0)

if __name__ == "__main__":
    serve()
