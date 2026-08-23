from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

_client: AsyncIOMotorClient | None = None


def get_client() -> AsyncIOMotorClient:
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(settings.mongodb_uri)
    return _client


def get_database():
    return get_client()[settings.mongodb_database]


async def close_database():
    global _client
    if _client:
        _client.close()
        _client = None


def get_collection(name: str):
    return get_database()[name]
