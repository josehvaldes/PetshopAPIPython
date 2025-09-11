import json
from pymilvus import connections, FieldSchema, CollectionSchema, DataType, Collection, utility
from pymilvus import model
from pymilvus import MilvusClient

def main():

    connections.connect(uri="http://localhost:19530")    

    fields = [
        FieldSchema(name="id", dtype=DataType.VARCHAR, is_primary=True, max_length=64),
        FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=768),
    ]
    
    collection_name = "dogs_breeds_collection3"

    schema = CollectionSchema(fields, description="Example collection with embedding field")
    
    collection = Collection(name=collection_name, schema=schema)

    if collection.is_empty and len(collection.indexes)==0:
        print("collection empty. End execution")
        return

    embedding_fn = model.DefaultEmbeddingFunction()
    
    query_vectors = embedding_fn.encode_queries(["nacionalidad: China", "China", "china"])

    search_params = {"metric_type": "L2", "params": {"nprobe": 32}}
    results = collection.search(query_vectors, "vector", 
                                param=search_params, 
                                limit=5,
                                output_fields=["id"])
    
    print(f"Search results: {len(results)} queries")
    for result in results:
        print(f"Top {len(result)} results:")
        for hit in result:
            print(f"ID: {hit.entity.get('id')}, Distance: {hit.distance}")
    
    print("Search completed")

if __name__ == "__main__":
    main()