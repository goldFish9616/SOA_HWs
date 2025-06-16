from promos.proto import promos_pb2, promos_pb2_grpc

def test_create_promo_success(promos_service, test_db):
    request = promos_pb2.CreatePromocodeRequest(name="Test", code="TEST10", discount=10)
    response = promos_service.CreatePromo(request, None)
    assert response.success is True
    assert test_db.query(Promo).filter_by(code="TEST10").first() is not None

def test_get_promo_by_code(promos_service, test_db):
    test_db.add(Promo(name="Test", code="LOOKUP", discount=5))
    test_db.commit()
    request = GetPromoRequest(code="LOOKUP")
    response = promos_service.GetPromo(request, None)
    assert response.promo.code == "LOOKUP"

def test_create_promo_duplicate_code(promos_service, test_db):
    test_db.add(Promo(name="Test", code="DUPLICATE", discount=5))
    test_db.commit()
    request = CreatePromoRequest(name="Test2", code="DUPLICATE", discount=15)
    response = promos_service.CreatePromo(request, None)
    assert response.success is False
