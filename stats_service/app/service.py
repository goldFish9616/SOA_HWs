# app/service.py
from app import proto_pb2_grpc, proto_pb2
from app.db import get_client

class StatService(proto_pb2_grpc.StatServiceServicer):
    def __init__(self):
        self.client = get_client()

    def GetPromocodeStats(self, request, context):
        query = f"""
            SELECT type, count(*) as total
            FROM promocode_events
            WHERE promocode_id = {request.promocode_id}
            GROUP BY type
        """
        rows = self.client.execute(query)
        counts = {t: 0 for t in ['view', 'click', 'like', 'comment']}
        for t, total in rows:
            counts[t] = total

        return proto_pb2.PromocodeStatsResponse(
            views=counts["view"],
            clicks=counts["click"],
            likes=counts["like"],
            comments=counts["comment"]
        )
