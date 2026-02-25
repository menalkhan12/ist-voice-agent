import os
import asyncio
from livekit import api
from dotenv import load_dotenv

load_dotenv(".env.local")

async def main():
    api_key = os.getenv("LIVEKIT_API_KEY")
    api_secret = os.getenv("LIVEKIT_API_SECRET")

    if not api_key or not api_secret:
        print("Error: LIVEKIT_API_KEY or LIVEKIT_API_SECRET not found in .env.local")
        return

    token = api.AccessToken(api_key, api_secret) \
        .with_identity("user-identity") \
        .with_name("User") \
        .with_grants(api.VideoGrants(
            room_join=True,
            room="my-room",
        ))
    
    print("\n=== Generated Token ===")
    print(token.to_jwt())
    print("========================\n")

if __name__ == "__main__":
    asyncio.run(main())
