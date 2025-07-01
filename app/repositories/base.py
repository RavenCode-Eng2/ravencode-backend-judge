from typing import Generic, TypeVar, Type, Optional, List
from motor.motor_asyncio import AsyncIOMotorCollection
from app.core.mongodb import get_database
from bson import ObjectId

T = TypeVar('T')

class BaseRepository(Generic[T]):
    def __init__(self, collection_name: str, model_class: Type[T]):
        self.collection_name = collection_name
        self.model_class = model_class
        self.database = get_database()
        self.collection: AsyncIOMotorCollection = self.database[collection_name]

    async def create(self, data: dict) -> T:
        """Crear un nuevo documento"""
        result = await self.collection.insert_one(data)
        data['_id'] = result.inserted_id
        return self.model_class(**data)

    async def get_by_id(self, id: str) -> Optional[T]:
        """Obtener documento por ID"""
        document = await self.collection.find_one({"_id": ObjectId(id)})
        if document:
            return self.model_class(**document)
        return None

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        """Obtener todos los documentos"""
        cursor = self.collection.find().skip(skip).limit(limit)
        documents = await cursor.to_list(length=limit)
        return [self.model_class(**doc) for doc in documents]

    async def update(self, id: str, data: dict) -> Optional[T]:
        """Actualizar documento"""
        result = await self.collection.update_one(
            {"_id": ObjectId(id)},
            {"$set": data}
        )
        if result.modified_count:
            return await self.get_by_id(id)
        return None

    async def delete(self, id: str) -> bool:
        """Eliminar documento"""
        result = await self.collection.delete_one({"_id": ObjectId(id)})
        return result.deleted_count > 0 