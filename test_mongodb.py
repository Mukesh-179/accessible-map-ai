#!/usr/bin/env python3
"""Test MongoDB Connection"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def test_mongodb():
    """Test MongoDB connection"""
    mongodb_url = "mongodb://localhost:27017"
    db_name = "accessible_map"
    
    print(f"Attempting to connect to MongoDB at {mongodb_url}...")
    print(f"Database: {db_name}\n")
    
    try:
        # Create client with timeout
        client = AsyncIOMotorClient(mongodb_url, serverSelectionTimeoutMS=3000)
        
        # Try to connect and ping
        await client.admin.command('ping')
        print("✅ MongoDB Connection Successful!")
        
        # Get database
        db = client[db_name]
        
        # List collections
        collections = await db.list_collection_names()
        print(f"\nCollections in '{db_name}':")
        if collections:
            for collection in collections:
                count = await db[collection].count_documents({})
                print(f"  - {collection}: {count} documents")
        else:
            print("  (no collections yet)")
        
        # Close connection
        client.close()
        print("\n✅ Connection closed successfully")
        
    except Exception as e:
        print(f"❌ MongoDB Connection Failed!")
        print(f"Error: {type(e).__name__}: {e}")
        print("\nPossible solutions:")
        print("1. Install MongoDB (Windows: https://www.mongodb.com/try/download/community)")
        print("2. Start MongoDB service: mongod")
        print("3. Check MongoDB connection string: mongodb://localhost:27017")
        print("4. Use MongoDB Atlas: https://www.mongodb.com/cloud/atlas")

if __name__ == "__main__":
    asyncio.run(test_mongodb())
