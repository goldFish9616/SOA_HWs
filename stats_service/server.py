# server.py
import grpc
from concurrent import futures
from app import proto_pb2_grpc
from app.service import StatService

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    proto_pb2_grpc.add_StatServiceServicer_to_server(StatService(), server)
    server.add_insecure_port('[::]:50051')
    print("StatService gRPC server running on :50051")
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()

