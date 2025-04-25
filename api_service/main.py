from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
import httpx
import grpc
from generated.proto import promo_pb2, promo_pb2_grpc
from user_service.auth import get_current_user_id
from pydantic import BaseModel
from datetime import datetime

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
        data = {
            "username": credentials["username"],
            "password": credentials["password"]
        }
        response = await client.post(f"{USER_SERVICE_URL}/api/users/authenticate", data=data)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)
        return response.json()


@app.put("/api/users/profile")
async def update_profile(profile_data: dict):
    async with httpx.AsyncClient() as client:
        response = await client.put(f"{USER_SERVICE_URL}/api/users/profile", json=profile_data)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)
        return response.json()

@app.get("/api/users/profile")
async def get_profile():
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{USER_SERVICE_URL}/api/users/profile")
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)
        return response.json()

@app.post("/api/promos", response_model=PromoResponse)
def create_promo(promo: PromoCreateRequest, token: str = Depends(oauth2_scheme)):
    user_id = get_current_user_id(token)
    print(f"Types: name={type(promo.name)}, description={type(promo.description)}, creator_id={type(promo.creator_id)}, discount_amount={type(promo.discount)}, code={type(promo.code)}")
    grpc_request = promo_pb2.PromoCreateRequest(
        name=str(promo.name),
        description=str(promo.description),
        creator_id=str(user_id),
        discount=float(promo.discount),
        code=str(promo.code)
    )
    try:
        response = promo_stub.CreatePromo(grpc_request)
        return PromoResponse(
            id=str(response.id),
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
def get_promo(promo_id: str, token: str = Depends(oauth2_scheme)):
    _ = get_current_user_id(token)
    try:
        response = promo_stub.GetPromoById(promo_pb2.PromoIdRequest(id=str(promo_id)))
        return PromoResponse(
            id=str(response.id),
            name=response.name,
            description=response.description,
            creator_id=str(response.creator_id),
            discount=response.discount,
            code=response.code,
            created_at=response.created_at,
            updated_at=response.updated_at
        )
    except grpc.RpcError as e:
        raise HTTPException(status_code=404, detail="Promo not found")


@app.get("/api/promos", response_model=list[PromoResponse])
def list_promos(page: int = 1, page_size: int = 10, token: str = Depends(oauth2_scheme)):
    _ = get_current_user_id(token)
    try:
        response = promo_stub.ListPromos(promo_pb2.PromoListRequest(page=page, page_size=page_size))
        promos = [
            PromoResponse(
                id=str(p.id),
                name=p.name,
                description=p.description,
                creator_id=str(p.creator_id),
                discount=p.discount,
                code=p.code,
                created_at=p.created_at,
                updated_at=p.updated_at
            ) for p in response.promos
        ]
        return promos
    except grpc.RpcError as e:
        raise HTTPException(status_code=500, detail="Error fetching promo list")


@app.put("/api/promos/{promo_id}", response_model=PromoResponse)
def update_promo(promo_id: str, promo: PromoCreateRequest, token: str = Depends(oauth2_scheme)):
    user_id = get_current_user_id(token)
    grpc_request = promo_pb2.PromoUpdateRequest(
        id=str(promo_id),
        name=promo.name,
        description=promo.description,
        creator_id=str(user_id),
        discount=promo.discount,
        code=promo.code
    )
    try:
        response = promo_stub.UpdatePromo(grpc_request)
        return PromoResponse(
            id=str(response.id),
            name=response.name,
            description=response.description,
            creator_id=str(response.creator_id),
            discount=response.discount,
            code=response.code,
            created_at=response.created_at,
            updated_at=response.updated_at
        )
    except grpc.RpcError as e:
        print(f"gRPC Error: {e.code()} - {e.details()}")
        raise HTTPException(status_code=500, detail=e.details())



@app.delete("/api/promos/{promo_id}")
def delete_promo(promo_id: str, token: str = Depends(oauth2_scheme)):
    _ = get_current_user_id(token)
    try:
        promo_stub.DeletePromo(promo_pb2.PromoIdRequest(id=promo_id))
        return {"message": "Promo deleted"}
    except grpc.RpcError:
        raise HTTPException(status_code=404, detail="Promo not found")

class PromoInteraction(BaseModel):
    client_id: str

class PromoComment(BaseModel):
    client_id: str
    content: str

class PromoCommentResponse(BaseModel):
    client_id: str
    content: str
    timestamp: str

@app.get("/api/promos/{promo_id}/view")
def view_promo(promo_id: str, interaction: PromoInteraction):
    try:
        promo_stub.ViewPromoCode(promo_pb2.PromoInteractionRequest(
            promo_id=promo_id,
            client_id=interaction.client_id
        ))
        return {"message": "View registered"}
    except grpc.RpcError as e:
        raise HTTPException(status_code=500, detail=str(e.details()))

@app.post("/api/promos/{promo_id}/click")
def click_promo(promo_id: str, interaction: PromoInteraction):
    try:
        promo_stub.ClickPromoCode(promo_pb2.PromoInteractionRequest(
            promo_id=promo_id,
            client_id=interaction.client_id
        ))
        return {"message": "Click registered"}
    except grpc.RpcError as e:
        raise HTTPException(status_code=500, detail=str(e.details()))

@app.post("/api/promos/{promo_id}/comment")
def comment_promo(promo_id: str, comment: PromoComment):
    try:
        promo_stub.CommentPromoCode(promo_pb2.PromoCommentRequest(
            promo_id=promo_id,
            client_id=comment.client_id,
            content=comment.content
        ))
        return {"message": "Comment added"}
    except grpc.RpcError as e:
        raise HTTPException(status_code=500, detail=str(e.details()))

@app.get("/api/promos/{promo_id}/comments", response_model=list[PromoCommentResponse])
def get_comments(promo_id: str, page: int = 1, page_size: int = 10):
    try:
        response = promo_stub.GetPromoCodeComments(promo_pb2.PromoCommentListRequest(
            promo_id=promo_id,
            page=page,
            page_size=page_size
        ))
        return [
            PromoCommentResponse(
                client_id=comment.client_id,
                content=comment.content,
                timestamp=comment.timestamp
            )
            for comment in response.comments
        ]
    except grpc.RpcError as e:
        raise HTTPException(status_code=500, detail=str(e.details()))

