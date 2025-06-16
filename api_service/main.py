from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
import httpx
from generated.proto import promo_pb2, promo_pb2_grpc
from pydantic import BaseModel
from datetime import datetime
import grpc

app = FastAPI(title="API Gateway")
USER_SERVICE_URL = "http://user_service:8001"

channel = grpc.insecure_channel("promocode_service:50052")
promo_stub = promo_pb2_grpc.PromoServiceStub(channel)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/users/authenticate")


class PromoCreateRequest(BaseModel):
    name: str
    description: str
    creator_id: int
    discount: float
    code: str

class PromoResponse(BaseModel):
    id: str
    name: str
    description: str
    creator_id: int
    discount: float
    code: str
    created_at: str
    updated_at: str

async def get_current_user_id(token: str = Depends(oauth2_scheme)):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{USER_SERVICE_URL}/api/users/me", headers={"Authorization": f"Bearer {token}"})
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="User authentication failed")
        return response.json().get("id")

@app.post("/api/users/register")
async def register_user(user_data: dict):
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{USER_SERVICE_URL}/api/users/register", json=user_data)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)
        return response.json()

@app.post("/api/users/authenticate")
async def authenticate_user(credentials: dict):
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{USER_SERVICE_URL}/api/users/authenticate", data=credentials)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)
        return response.json()

@app.put("/api/users/profile")
async def update_profile(profile_data: dict, token: str = Depends(oauth2_scheme)):
    async with httpx.AsyncClient() as client:
        response = await client.put(f"{USER_SERVICE_URL}/api/users/profile", json=profile_data, headers={"Authorization": f"Bearer {token}"})
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)
        return response.json()

@app.get("/api/users/profile")
async def get_profile(token: str = Depends(oauth2_scheme)):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{USER_SERVICE_URL}/api/users/profile", headers={"Authorization": f"Bearer {token}"})
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)
        return response.json()

@app.post("/api/promos", response_model=PromoResponse)
async def create_promo(promo: PromoCreateRequest, user_id: int = Depends(get_current_user_id)):
    grpc_request = promo_pb2.PromoCreateRequest(
        name=promo.name,
        description=promo.description,
        creator_id=str(user_id),
        discount=promo.discount,
        code=promo.code
    )
    try:
        response = promo_stub.CreatePromo(grpc_request)
        return PromoResponse(
            id=response.id,
            name=response.name,
            description=response.description,
            creator_id=response.creator_id,
            discount=response.discount,
            code=response.code,
            created_at=response.created_at,
            updated_at=response.updated_at
        )
    except grpc.RpcError as e:
        raise HTTPException(status_code=500, detail=str(e.details()))

@app.get("/api/promos/{promo_id}", response_model=PromoResponse)
async def get_promo(promo_id: str, user_id: int = Depends(get_current_user_id)):
    try:
        response = promo_stub.GetPromoById(promo_pb2.PromoIdRequest(id=promo_id))
        return PromoResponse(
            id=response.id,
            name=response.name,
            description=response.description,
            creator_id=response.creator_id,
            discount=response.discount,
            code=response.code,
            created_at=response.created_at,
            updated_at=response.updated_at
        )
    except grpc.RpcError:
        raise HTTPException(status_code=404, detail="Promo not found")


@app.get("/posts/{post_id}/stats")
def post_stats(post_id: int):
    request = statistics_pb2.PostIdRequest(post_id=post_id)
    response = grpc_stub.GetPostStats(request)
    return {
        "views": response.views,
        "likes": response.likes,
        "comments": response.comments
    }