import json
from pymilvus import connections, FieldSchema, CollectionSchema, DataType, Collection, utility
from pymilvus import model

from sentence_transformers import SentenceTransformer

jsonl_path = "c:/personal/_gemma/customdocs/converted/dogs_dataset.jsonl"

def load_jsonl(path):
    try:
        with open(jsonl_path, 'r', encoding='utf-8') as file:
            data = [json.loads(line) for line in file]
        return data
    except FileNotFoundError:
        print(f"File not found: {jsonl_path}")
        data = []
    except Exception as e:
        print(f"Error loading JSONL file: {e}")
        data = []

def extract_documents_and_ids(data):
    breed_documents = []
    breed_ids = []
    metadatas = []
    for record in data: 
        input_text = record.get("input", "")
        breed_documents.append(input_text)
        index = input_text.find(" Nacionalidad: ") # find first space
        if index != -1:
            id = input_text[:index] # take first word as id
        else:
            id = input_text
        breed_ids.append(id)

        index_nationality = input_text.find(". Origen") # find first space
        nationality = ""
        if index_nationality != -1:
            nationality = input_text[ index + len(" Nacionalidad: ") : index_nationality].strip() # take text between "Nacionalidad" and ". Origen"
            metadatas.append({"source": "dogs_dataset.jsonl", "nacionalidad": nationality})
        else:
            metadatas.append({"source": "dogs_dataset.jsonl", "nacionalidad": "unknown: " + input_text[:index]})
    return breed_documents, breed_ids, metadatas


def main():

    connections.connect(host='127.0.0.1', port='19530')

    fields = [
        FieldSchema(name="id", dtype=DataType.VARCHAR, is_primary=True, max_length=64),
        FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=768),
    ]
    
    collection_name = "dogs_breeds_collection3"

    schema = CollectionSchema(fields, description="Example collection with embedding field")
    
    collection = Collection(name=collection_name, schema=schema)

    
    data = load_jsonl(jsonl_path)
    breed_documents, breed_ids, metadatas = extract_documents_and_ids(data)

    embedding_fn = model.DefaultEmbeddingFunction()
    vectors = embedding_fn.encode_documents(breed_documents)

    data = [
        {"id": breed_ids[i], "vector": vectors[i], "text": breed_documents[i], 
         "metadata": metadatas[i], "subject": "dog_breed"} 
        for i in range(len(breed_ids))    
    ]

    
    res = collection.insert([breed_ids, vectors])
    
    print(f"Inserted {len(res.primary_keys)} entities")  

    collection.release()
    collection.drop_index()

    # Alternative index
    # index_params = {"index_type": "IVF_PQ", 
    #                         "params": {"nlist": 128, "m":32, "nbits":8}, 
    #                         "metric_type": "L2"}
    
    index_params = {
        "index_type": "IVF_FLAT",
        "params": {"nlist": 128},
        "metric_type": "L2"
    }
    
    collection.create_index("vector", index_params)
    print("Index created:", [index.params for index in collection.indexes])
    collection.load()

    print("Collection loaded")

    query_vectors = embedding_fn.encode_queries(["nacionalidad china"])

    search_params = {"metric_type": "L2", "params": {"nprobe": 64}}
    results = collection.search(query_vectors, "vector", 
                                param=search_params, 
                                limit=4,
                                output_fields=["id"])
    print(f"Search results: {len(results)} queries")
    for result in results:
        print(f"Top {len(result)} results:")
        for hit in result:
            print(f"ID: {hit.entity.get('id')}, Distance: {hit.distance}")
    
    print("Search completed")

if __name__ == "__main__":
    main()