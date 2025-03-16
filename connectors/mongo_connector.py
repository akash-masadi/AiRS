import datetime
import os
import json
import threading
from typing import Any, Dict, List, Optional, Union
from dotenv import load_dotenv
import streamlit as st
import pymongo
from pymongo import MongoClient, WriteConcern
from bson import ObjectId
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.errors import ConnectionFailure, OperationFailure
import logging
from functools import wraps
from models.openai_model import get_openai_model

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("MongoConnector")

# Load environment variables
load_dotenv()

def connection_required(func):
    """Decorator to ensure MongoDB connection exists before operations"""
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if not self.client:
            self.connect()
        return func(self, *args, **kwargs)
    return wrapper
    

class MongoConnector:
    """Singleton class for MongoDB connections and CRUD operations"""

    _instance = None
    _lock = threading.Lock()  # Thread safety for singleton

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(MongoConnector, cls).__new__(cls)
                cls._instance.client = None
                cls._instance.db = None
                cls._instance.connection_string = None
                cls._instance.db_name = None
                cls._instance._load_config()
                cls._instance.ai_model = get_openai_model()
        return cls._instance

    def _load_config(self) -> None:
        """Load MongoDB configuration from environment variables"""
        mongodb_username = os.getenv("MONGODB_USERNAME")
        mongodb_password = os.getenv("MONGODB_PASSWORD")
        mongodb_cluster = os.getenv("MONGODB_CLUSTER")
        self.db_name = os.getenv("MONGODB_DATABASE")
        
        if not all([mongodb_username, mongodb_password, mongodb_cluster, self.db_name]):
            logger.warning("Missing MongoDB configuration in environment variables. Using default values for development.")
            self.connection_string = "mongodb://localhost:27017/"
            self.db_name = "main"
        else:
            self.connection_string = (
                f"mongodb+srv://{mongodb_username}:{mongodb_password}@{mongodb_cluster}.mongodb.net/{self.db_name}"
                "?retryWrites=true&w=majority&appName=AiRS"
            )
        self.connect()

    def connect(self, retries: int = 5) -> None:
        """Establish connection to MongoDB Atlas with retry logic"""
        for attempt in range(retries):
            try:
                self.client = MongoClient(
                    self.connection_string,
                    serverSelectionTimeoutMS=5000,
                    connectTimeoutMS=5000,
                    socketTimeoutMS=30000,
                    maxPoolSize=100,
                    waitQueueTimeoutMS=1000,
                )

                self.client.admin.command("ping")  # Check connection
                self.db = self.client[self.db_name]
                logger.info(f"Connected to MongoDB - Database: {self.db_name}")
                return
            except ConnectionFailure as e:
                logger.error(f"Connection attempt {attempt + 1} failed")
                if attempt == retries - 1:
                    logger.error("Failde to Connect to Mongodb")
                    st.stop()

    def disconnect(self) -> None:
        """Close MongoDB connection and reset singleton"""
        if self.client:
            self.client.close()
            self.client = None
            self.db = None
            MongoConnector._instance = None  # Reset the singleton
            logger.info("Disconnected from MongoDB")

    @connection_required
    def get_collection(self, collection_name: str) -> Collection:
        """Get a MongoDB collection object"""
        try:
            return self.db[collection_name]
        except:
            st.stop()

    @connection_required
    def create_document(self, collection_name: str, document: Dict[str, Any]) -> str:
        """Create a new document in the specified collection"""
        try:
            # # Get structured data from AI model
            # structured_document = self.ai_model.get_applicant_details(document)
            # logger.info(structured_document,type(structured_document))
            
            # Validate the document structure before insertion
            if not isinstance(document, dict):
                raise ValueError("AI model returned invalid document format")
                
            # Add system-generated metadata
            # structured_document.setdefault("system_metadata", {
            #     "created_at": datetime.datetime.utcnow(),
            #     "updated_at": datetime.datetime.utcnow(),
            #     "processing_version": "1.2.0"
            # })
            # document.setdefault()
            document = {
                "system_metadata": {
                    "created_at": datetime.datetime.utcnow(),
                    "updated_at": datetime.datetime.utcnow(),
                    "processing_version": "1.2.0"
                },
                'document' : document
            }
            collection = self.get_collection(collection_name)
            
            # Validate document against basic schema
            if "_id" not in document:
                document["_id"] = ObjectId()

            # Insert document with write concern
            result = collection.insert_one(document)
            
            logger.info(f"Document created in {collection_name} with ID: {result.inserted_id}")
            return str(result.inserted_id)
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON from AI model: {e}")
            raise
        except pymongo.errors.InvalidDocument as e:
            logger.error(f"Invalid document structure: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to create document: {str(e)}")
            raise

    @connection_required
    def create_many_documents(self, collection_name: str, documents: List[Dict[str, Any]]) -> List[str]:
        """Create multiple documents in the specified collection"""
        try:
            collection = self.get_collection(collection_name)
            result = collection.insert_many(documents)
            return [str(id) for id in result.inserted_ids]
        except OperationFailure as e:
            logger.error(f"Failed to create documents in {collection_name}: {e}")
            raise

    @connection_required
    def read_document(self, collection_name: str, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Find a single document matching the query"""
        try:
            collection = self.get_collection(collection_name)
            return collection.find_one(query)
        except OperationFailure as e:
            logger.error(f"Failed to read document from {collection_name}: {e}")
            raise

    @connection_required
    def read_documents(
        self, collection_name: str, query: Dict[str, Any] = None, projection: Dict[str, Any] = None,
        sort: List[tuple] = None, limit: int = 0, skip: int = 0
    ) -> List[Dict[str, Any]]:
        """Find multiple documents matching the query with advanced options"""
        try:
            collection = self.get_collection(collection_name)
            cursor = collection.find(query or {}, projection).batch_size(100)

            if sort:
                cursor = cursor.sort(sort)
            if skip:
                cursor = cursor.skip(skip)
            if limit:
                cursor = cursor.limit(limit)

            return list(cursor)
        except OperationFailure as e:
            logger.error(f"Failed to read documents from {collection_name}: {e}")
            raise

    @connection_required
    def update_document(self, collection_name: str, query: Dict[str, Any], update_data: Dict[str, Any], upsert: bool = False) -> int:
        """Update a single document matching the query"""
        try:
            collection = self.get_collection(collection_name)
            result = collection.update_one(query, update_data, upsert=upsert)
            return result.modified_count
        except OperationFailure as e:
            logger.error(f"Failed to update document in {collection_name}: {e}")
            raise

    @connection_required
    def delete_document(self, collection_name: str, query: Dict[str, Any]) -> int:
        """Delete a single document matching the query"""
        try:
            collection = self.get_collection(collection_name)
            result = collection.delete_one(query)
            return result.deleted_count
        except OperationFailure as e:
            logger.error(f"Failed to delete document from {collection_name}: {e}")
            raise

    @connection_required
    def aggregate(self, collection_name: str, pipeline: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Perform an aggregation pipeline operation"""
        try:
            collection = self.get_collection(collection_name)
            return list(collection.aggregate(pipeline, allowDiskUse=True))
        except OperationFailure as e:
            logger.error(f"Failed to perform aggregation on {collection_name}: {e}")
            raise

    @connection_required
    def count_documents(self, collection_name: str, query: Dict[str, Any] = None) -> int:
        """Count documents matching the query"""
        try:
            collection = self.get_collection(collection_name)
            return collection.count_documents(query or {})
        except OperationFailure as e:
            logger.error(f"Failed to count documents in {collection_name}: {e}")
            raise

    @connection_required
    def create_index(self, collection_name: str, keys: Union[str, List[tuple]], **kwargs) -> str:
        """Create an index on the collection"""
        try:
            collection = self.get_collection(collection_name)
            return collection.create_index(keys, **kwargs)
        except OperationFailure as e:
            logger.error(f"Failed to create index on {collection_name}: {e}")
            raise

