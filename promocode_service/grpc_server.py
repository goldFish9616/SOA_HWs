import grpc
from concurrent import futures
from generated.proto import promo_pb2_grpc
from main import PromoCodeService
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
promo_pb2_grpc.add_PromoServiceServicer_to_server(PromoCodeService(), server)
server.add_insecure_port('[::]:50052')
print("PromoCode gRPC server running on port 50052")
server.start()
server.wait_for_termination()
