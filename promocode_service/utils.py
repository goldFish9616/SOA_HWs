from generated.proto import promo_pb2

def request_to_dict(request, exclude_keys=None):
    if exclude_keys is None:
        exclude_keys = []
        
    data = {
        "name": request.name,
        "description": request.description,
        "creator_id": request.creator_id,
        "discount": request.discount,
        "code": request.code
    }
    
    return {k: v for k, v in data.items() if k not in exclude_keys and v is not None}



def promo_to_pb(promo):
    return promo_pb2.PromoResponse(
        id=promo.id,
        name=promo.name,
        description=promo.description,
        creator_id=promo.creator_id,
        discount=promo.discount,
        code=promo.code,
        created_at=str(promo.created_at),
        updated_at=str(promo.updated_at)
    )