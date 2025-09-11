import json
from pymilvus import connections, FieldSchema, CollectionSchema, DataType, Collection, utility
from pymilvus import model
from sentence_transformers import SentenceTransformer

def main():

    connections.connect(uri="http://localhost:19530")    

    fields = [
        FieldSchema(name="id", dtype=DataType.VARCHAR, is_primary=True, max_length=64),
        FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=768),
        FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=10000)
    ]
    
    collection_name = "Dogs_Info_Collection_6"

    schema = CollectionSchema(fields, description="ID and Text and Embeddings collection 6")
    
    collection = Collection(name=collection_name, schema=schema)

    if collection.is_empty and len(collection.indexes)==0:
        print("collection empty. End execution")
        return

    #embedding_fn = model.DefaultEmbeddingFunction()
    model = SentenceTransformer('paraphrase-multilingual-mpnet-base-v2')
    
    query_vectors = model.encode(["malta"])

    search_params = {"metric_type": "L2", "params": {"nprobe": 32}}
    results = collection.search(query_vectors, 
                                "embedding", 
                                param=search_params, 
                                limit=5,
                                output_fields=["id", "text"])
    
    print(f"Search results: {len(results)} queries")
    for result in results:
        print(f"Top {len(result)} results:")
        for hit in result:
            print(f"ID: {hit.entity.get('id')}, Distance: {hit.distance}")

    
    print("Search completed")

if __name__ == "__main__":
    main()