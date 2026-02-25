import os
import asyncio
import json
from aiohttp import web
from livekit import api
from dotenv import load_dotenv

load_dotenv(".env.local")

async def get_token(request):
    api_key = os.getenv("LIVEKIT_API_KEY")
    api_secret = os.getenv("LIVEKIT_API_SECRET")
    
    if not api_key or not api_secret:
        return web.Response(status=500, text="Credentials not found")

    # Generate a random participant name
    user_identity = f"user_{os.urandom(4).hex()}"
    
    grant = api.VideoGrants(
        room_join=True,
        room="my-room",
    )
    
    token = api.AccessToken(api_key, api_secret) \
        .with_identity(user_identity) \
        .with_name("Human User") \
        .with_grants(grant)
    
    return web.json_response({
        "token": token.to_jwt(),
        "url": os.getenv("LIVEKIT_URL")
    })

async def serve_index(request):
    return web.FileResponse('./web/index.html')

app = web.Application()
app.router.add_get('/', serve_index)
app.router.add_get('/token', get_token)
app.router.add_static('/', path='./web')

if __name__ == "__main__":
    print("Starting Web/Token server on http://localhost:8080")
    web.run_app(app, port=8080)
