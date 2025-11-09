import grpc
from concurrent import futures
import time

import calc_pb2
import calc_pb2_grpc

class CalculatorServicer(calc_pb2_grpc.CalculatorServicer):
    def Compute(self, request, context):
        a = request.a
        b = request.b
        op = request.op

        try:
            if op == calc_pb2.ADD:
                value = a + b
            elif op == calc_pb2.SUB:
                value = a - b
            elif op == calc_pb2.MUL:
                value = a * b
            elif op == calc_pb2.DIV:
                if b == 0:
                    return calc_pb2.Result(value=0.0, error="Divisão por zero")
                value = a / b
            else:
                return calc_pb2.Result(value=0.0, error="Operação inválida")
            return calc_pb2.Result(value=value, error="")
        except Exception as e:
            return calc_pb2.Result(value=0.0, error=str(e))

def serve(port: int = 50051):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=8))
    calc_pb2_grpc.add_CalculatorServicer_to_server(CalculatorServicer(), server)
    server.add_insecure_port(f"[::]:{port}")
    print(f"Calculator gRPC server listening on 0.0.0.0:{port}")
    server.start()
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        print("Shutting down...")
        server.stop(0)

if __name__ == "__main__":
    serve()
