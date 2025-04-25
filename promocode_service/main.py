import grpc
from concurrent import futures
import time
from sqlalchemy.orm import Session
import crud
from models import Base
from database import SessionLocal, engine
from generated.proto import promo_pb2, promo_pb2_grpc
from kafka_producer import send_event
from collections import defaultdict
from datetime import datetime



Base.metadata.create_all(bind=engine)
comments_by_promo = defaultdict(list)


class PromoCodeService(promo_pb2_grpc.PromoServiceServicer):
    def __init__(self):
        self.db = SessionLocal()

    def CreatePromoCode(self, request, context):
        promo_code = crud.create_promo_code(
            db=self.db,
            name=request.name,
            description=request.description,
            creator_id=request.creator_id,
            discount=request.discount,
            code=request.code
        )

        send_event(
            topic="promo-events",
            event_type="PROMO_CODE_CREATED",
            data={
                "id": promo_code.id,
                "name": promo_code.name,
                "description": promo_code.description,
                "creator_id": promo_code.creator_id,
                "discount": promo_code.discount,
                "code": promo_code.code,
                "created_at": str(promo_code.created_at),
                "updated_at": str(promo_code.updated_at)
            }
        )

        return promo_pb2.PromoCodeResponse(
            id=promo_code.id,
            name=promo_code.name,
            description=promo_code.description,
            creator_id=promo_code.creator_id,
            discount=promo_code.discount,
            code=promo_code.code,
            created_at=str(promo_code.created_at),
            updated_at=str(promo_code.updated_at)
        )

    def DeletePromoCode(self, request, context):
        promo_code = crud.delete_promo_code(db=self.db, promo_code_id=request.id)
        if not promo_code:
            context.set_details('Promo code not found')
            context.set_code(grpc.StatusCode.NOT_FOUND)
        return promo_pb2.PromoCodeResponse(id=request.id)

    def UpdatePromoCode(self, request, context):
        promo_code = crud.update_promo_code(
            db=self.db,
            promo_code_id=request.id,
            name=request.name,
            description=request.description,
            discount=request.discount,
            code=request.code
        )
        if not promo_code:
            context.set_details('Promo code not found')
            context.set_code(grpc.StatusCode.NOT_FOUND)
        return promo_pb2.PromoCodeResponse(
            id=promo_code.id,
            name=promo_code.name,
            description=promo_code.description,
            creator_id=promo_code.creator_id,
            discount=promo_code.discount,
            code=promo_code.code,
            created_at=str(promo_code.created_at),
            updated_at=str(promo_code.updated_at)
        )

    def GetPromoCodeById(self, request, context):
        promo_code = crud.get_promo_code_by_id(db=self.db, promo_code_id=request.id)
        if not promo_code:
            context.set_details('Promo code not found')
            context.set_code(grpc.StatusCode.NOT_FOUND)
            return promo_pb2.PromoCodeResponse()
        return promo_pb2.PromoCodeResponse(
            id=promo_code.id,
            name=promo_code.name,
            description=promo_code.description,
            creator_id=promo_code.creator_id,
            discount=promo_code.discount,
            code=promo_code.code,
            created_at=str(promo_code.created_at),
            updated_at=str(promo_code.updated_at)
        )

    def GetPromoCodes(self, request, context):
        promo_codes = crud.get_promo_codes(db=self.db, skip=(request.page - 1) * request.page_size, limit=request.page_size)
        response = promo_pb2.PromoCodeListResponse()
        for promo_code in promo_codes:
            response.promo_codes.add(
                id=promo_code.id,
                name=promo_code.name,
                description=promo_code.description,
                creator_id=promo_code.creator_id,
                discount=promo_code.discount,
                code=promo_code.code,
                created_at=str(promo_code.created_at),
                updated_at=str(promo_code.updated_at)
            )
        return response
    
    def ViewPromoCode(self, request, context):
        send_event("promo_views", "view", {
            "client_id": request.client_id,
            "promo_code_id": request.promo_code_id
        })
        return promo_pb2.PromoCodeActionResponse(success=True, message="Promo viewed")

    def ClickPromoCode(self, request, context):
        send_event("promo_clicks", "click", {
            "client_id": request.client_id,
         "promo_code_id": request.promo_code_id
        })
        return promo_pb2.PromoCodeActionResponse(success=True, message="Promo clicked")

    def CommentPromoCode(self, request, context):
        comment = crud.create_comment(
            db=self.db,
            promo_code_id=request.promo_code_id,
            client_id=request.client_id,
            text=request.text
        )
        send_event("promo_comments", "comment", {
            "client_id": request.client_id,
            "promo_code_id": request.promo_code_id,
            "text": request.text
        })
        return promo_pb2.PromoCodeActionResponse(success=True, message="Comment added")


    def GetPromoCodeComments(self, request, context):
        all_comments = crud.get_comments_by_promo_id(
            db=self.db,
            promo_code_id=request.promo_code_id,
            skip=(request.page - 1) * request.page_size,
            limit=request.page_size
        )
        total_comments = crud.count_comments_by_promo_id(
            db=self.db,
            promo_code_id=request.promo_code_id
        )

        response = promo_pb2.PromoCodeCommentListResponse()
        for c in all_comments:
            response.comments.add(
                client_id=c.client_id,
                text=c.text,
                created_at=c.created_at.isoformat()
            )
        response.total = total_comments
        return response



def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    promo_pb2_grpc.add_PromoServiceServicer_to_server(PromoCodeService(), server)
    server.add_insecure_port('[::]:50052')
    server.start()
    print("PromoCodeService started on port 50052.")
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == '__main__':
    serve()
