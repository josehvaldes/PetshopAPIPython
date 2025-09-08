import json
import chromadb

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
        breed_documents.append(input_text);
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
    data = load_jsonl(jsonl_path)
    print(f"Loaded {len(data)} records from {jsonl_path}")

    breed_documents, breed_ids, metadatas = extract_documents_and_ids(data)
    print("Metadatas:")
    print(metadatas[:])
    
    client = chromadb.Client() # Can be set to save to disk
    collection = client.create_collection("sales_reports")

    collection.upsert(
        documents=breed_documents,
        ids=breed_ids,
        metadatas=metadatas
    )

    results = collection.query(
        query_texts=["Nacionalidad China"],
        n_results=5, # how many results to return
    )
    print("Results:")
    print(results["ids"])


if __name__ == "__main__":
    main()