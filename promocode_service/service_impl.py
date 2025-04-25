from generated.proto import promo_pb2_grpc, promo_pb2
from database import SessionLocal
import crud, utils

class PromoServiceServicer(promo_pb2_grpc.PromoServiceServicer):
    def CreatePromo(self, request, context):
        db = SessionLocal()
        promo = crud.create_promo(db, utils.request_to_dict(request))
        return utils.promo_to_pb(promo)

    def GetPromoById(self, request, context):
        db = SessionLocal()
        promo = crud.get_promo(db, request.id)
        return utils.promo_to_pb(promo)

    def DeletePromo(self, request, context):
        db = SessionLocal()
        promo = crud.delete_promo(db, request.id)
        return utils.promo_to_pb(promo)

    def UpdatePromo(self, request, context):
        db = SessionLocal()
        promo = crud.update_promo(db, request.id, utils.request_to_dict(request, exclude_keys=["id"]))
        return utils.promo_to_pb(promo)

    def ListPromos(self, request, context):
        db = SessionLocal()
        promos = crud.list_promos(db, skip=(request.page - 1) * request.page_size, limit=request.page_size)
        return promo_pb2.PromoListResponse(promos=[utils.promo_to_pb(p) for p in promos])
