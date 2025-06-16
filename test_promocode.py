import pytest
from promocode_service.models import Promo, Base
# from promocode_service.database import SessionLocal
from promocode_service.service_impl import PromoServiceServicer
from promocode_service.generated import promo_pb2
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "postgresql://jinyuz:password@promocode_db:5432/promocodedb"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="module")
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()

@pytest.fixture(scope="module")
def service():
    return PromoServiceServicer()

def test_create_promo(db, service):
    request = promo_pb2.PromoCreateRequest(
        name="Test Promo",
        description="Some description",
        creator_id="1",
        discount=15.5,
        code="TEST15"
    )

    response = service.CreatePromo(request, context=None)
    assert response.name == "Test Promo"
    assert response.code == "TEST15"

def test_get_promo_by_id(db, service):
    create_request = promo_pb2.PromoCreateRequest(
        name="Promo 2",
        description="Another",
        creator_id="1",
        discount=10,
        code="PROMO2"
    )
    created = service.CreatePromo(create_request, context=None)
    
    get_request = promo_pb2.PromoByIdRequest(id=created.id)
    response = service.GetPromoById(get_request, context=None)

    assert response.id == created.id
    assert response.code == "PROMO2"

def test_list_promos(db, service):
    request = promo_pb2.PromoListRequest(page=1, page_size=10)
    response = service.ListPromos(request, context=None)
    assert len(response.promos) >= 2
