import json
import traceback

# Default path to JSONL file
#TODO move to parameters
jsonl_path_default = "h:/ML_Models/_gemma/customdocs/converted/dogs_dataset_english.jsonl"

def get_files_as_dict(jsonl_path=None) -> dict:
    jsonl_path = jsonl_path or jsonl_path_default
    print("path")
    print(jsonl_path)
    files_dict = {}
    try:
        with open(jsonl_path, 'r', encoding='utf-8') as file:
            data = [json.loads(line) for line in file]
            print(f"Loaded {len(data)} records from JSONL file.")
            for i, record in enumerate(data):
                text = record.get("input","")
                index = text.find(" Nationality: ") # find first space
                if index != -1:
                    id = text[:index] # take first word as id
                else:
                    id = text
                id = id.replace(' ','_').replace('/','_')
                files_dict[id] = text
        
    except FileNotFoundError:
        print(f"File not found: {jsonl_path}")
    except Exception as e:
        print(f"Error loading JSON file: {e} ")
        traceback.print_exc()
    
    return files_dict


if __name__ == "__main__":
    files_dict = get_files_as_dict()
    print(f"Total files processed: {len(files_dict)}")
    for id, text in list(files_dict.items())[:2]:  # Print first 5 entries
        print(f"ID: {id}, Text snippet: {text[:100]}...")  # Print first 100 characters of text
