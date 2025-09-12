# %%
import json
from pymilvus import connections, FieldSchema, CollectionSchema, DataType, Collection, utility
from pymilvus import Index
from sentence_transformers import SentenceTransformer

jsonl_path = "c:/personal/_gemma/customdocs/converted/dogs_dataset_english.jsonl"


def load_jsonl(path):
    try:
        with open(jsonl_path, 'r', encoding='utf-8') as file:
            print("Loading JSONL file...")
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
        index = input_text.find(" Nationality: ") # find first space
        if index != -1:
            id = input_text[:index] # take first word as id
        else:
            id = input_text
        breed_ids.append(id)

        index_nationality = input_text.find(". Origin") # find first space
        nationality = ""
        if index_nationality != -1:
            nationality = input_text[ index + len(" Nationality: ") : index_nationality].strip() # take text between "Nacionalidad" and ". Origen"
            metadatas.append({"source": "dogs_dataset.jsonl", "Nationality": nationality})
        else:
            metadatas.append({"source": "dogs_dataset.jsonl", "Nationality": "unknown: " + input_text[:index]})
    return breed_documents, breed_ids, metadatas


# %%
connections.connect(host='127.0.0.1', port='19530')

collection_name = "Dogs_Info_Collection_en_3"

fields = [
    FieldSchema(name="id", dtype=DataType.VARCHAR, is_primary=True, max_length=64),
    FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=768), #384 for HNSW # Adjust the embedding dimension
    FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=10000)
]
    

# Create a collection schema
schema = CollectionSchema(fields, description="ID and Text and Embeddings collection 6")

# Create the collection
collection = Collection(collection_name, schema=schema)

if utility.has_collection(collection_name):
    print("Milvus has the collection")
    collection.release()
    collection.drop_index()
else:
    print("Milvus doesn't have the collection")


index_params = {"index_type": "HNSW", "params": {"M": 16, "efConstruction": 200}, "metric_type": "COSINE"}
#index_params = {"index_type": "IVF_PQ", "params": {"nlist": 128, "m":32, "nbits":8}, "metric_type": "L2"}
#index_params = { "index_type": "IVF_FLAT", "params": {"nlist": 128}, "metric_type": "L2"}

index = Index(collection, "embedding", index_params)
print("Index created:", index.params)



# %%
# Load a pre-trained model to generate embeddings
model = SentenceTransformer('multi-qa-mpnet-base-dot-v1')

data = load_jsonl(jsonl_path)
texts , breed_ids, metadatas = extract_documents_and_ids(data)
print(f"Loaded {len(texts)} documents.")
# Generate embeddings for the texts
embeddings = model.encode(texts)

# Insert the data (texts and embeddings) into the collection
data = [breed_ids, embeddings, texts]  # Milvus requires data as a list of columns
collection.insert(data)

# Load the collection (helps optimize query performance)
collection.load()
print("Collection loaded.")



# %%
#Example text query
query_text = "rescue dog"

# Generate embedding for the query text
query_embedding = model.encode([query_text])

# Type HNSW
results = collection.search(
    data=query_embedding,  # The query embedding
    anns_field="embedding",  # Field that contains the embeddings
    param={"metric_type": "COSINE", "params": {"ef": 128}},  # Search parameters
    limit=3,  # Number of results to return
    expr=None  # Optional filtering expression
)

# Print the results
for result in results[0]:
    print(f"ID: {result.entity.get('id')} Matched text: {result.entity.get('text')}, similarity score: {result.distance}")

# Type IVF_PQ or IVF_FLAT
# search_params = {"metric_type": "L2", "params": {"nprobe": 64}}
# results = collection.search(query_embedding, 
#                         "embedding", 
#                         param=search_params, 
#                         limit=4,
#                         output_fields=["id"])
