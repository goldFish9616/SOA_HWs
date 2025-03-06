from fastapi import FastAPI, HTTPException
import httpx

app = FastAPI()
USER_SERVICE_URL = "http://user_service:8001"

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
        response = await client.post(f"{USER_SERVICE_URL}/api/users/authenticate", json=credentials)
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