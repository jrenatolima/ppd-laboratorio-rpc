import grpc
import sys

import calc_pb2
import calc_pb2_grpc

def menu():
    print("\n=== CALCULADORA RPC ===")
    print("1) Soma")
    print("2) Subtração")
    print("3) Multiplicação")
    print("4) Divisão")
    print("q) Sair")
    return input("Escolha: ").strip().lower()

def ask_operands():
    a = float(input("a = "))
    b = float(input("b = "))
    return a, b

def run(target: str):
    with grpc.insecure_channel(target) as channel:
        stub = calc_pb2_grpc.CalculatorStub(channel)
        while True:
            op = menu()
            if op == "q":
                print("Encerrando cliente...")
                break

            mapping = {
                "1": calc_pb2.ADD,
                "2": calc_pb2.SUB,
                "3": calc_pb2.MUL,
                "4": calc_pb2.DIV,
            }
            if op not in mapping:
                print("Opção inválida.")
                continue

            a, b = ask_operands()
            req = calc_pb2.OpRequest(op=mapping[op], a=a, b=b)
            resp = stub.Compute(req)
            if resp.error:
                print(f"ERRO: {resp.error}")
            else:
                print(f"Resultado = {resp.value}")

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "localhost:50051"
    print(f"Conectando a {target}...")
    run(target)
