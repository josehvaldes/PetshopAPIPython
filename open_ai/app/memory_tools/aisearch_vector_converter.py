import math
from app.memory_tools.file_parser import get_files_as_dict
from app.memory_tools.vectorized_file import VectorizedFile
from langchain.text_splitter import TokenTextSplitter
from langchain.text_splitter import RecursiveCharacterTextSplitter
from semantic_text_splitter import TextSplitter
from tokenizers import Tokenizer
from tiktoken import get_encoding

#Configurable Model parameters
#Move to settings?
MODEL_DIM = 1536           # text-embedding-3-small
BYTES_PER_FLOAT = 4        # float32
VECTOR_SIZE_BYTES = MODEL_DIM * BYTES_PER_FLOAT  # = 6,144 bytes ≈ 6 KB per vector
VECTOR_QUOTA_MB = 25       # Free tier
TOKEN_LIMIT = 8000         # Model max input tokens 8191

#Adjust the ratio according to needs and documents sizes
AVG_CHUNK_TOKENS = 500     # You can tune this based on your chunking
CHUNK_OVERLAP_TOKENS = int(AVG_CHUNK_TOKENS * 0.125)  #Overlap between chunks. harcoded to 50 or use a %

#Text Splitter
token_splitter = TokenTextSplitter(
    chunk_size=AVG_CHUNK_TOKENS,
    chunk_overlap=CHUNK_OVERLAP_TOKENS,
    encoding_name="cl100k_base"  # same tokenizer as OpenAI
)

rec_text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=AVG_CHUNK_TOKENS,      # roughly token-based equivalent
    chunk_overlap=CHUNK_OVERLAP_TOKENS,
    length_function=len, # use len() or a token counter
    separators=["\n\n", "\n", ".", " "]  # prefer breaking at sentence/paragraph
)

tokenizer = Tokenizer.from_pretrained("bert-base-uncased")
semantic_splitter = TextSplitter.from_huggingface_tokenizer(
    tokenizer, #"thenlper/gte-small", 
    capacity=AVG_CHUNK_TOKENS, 
    overlap=CHUNK_OVERLAP_TOKENS
)

#Tokenizer
encoding = get_encoding("cl100k_base")

def combined_token_estimation( texts, avg_chunk_tokens=AVG_CHUNK_TOKENS):
   
    """Estimate how many vectors will be created and total vector storage (MB)."""

    total_tokens = sum(len(encoding.encode(t)) for t in texts)

    total_vectors = math.ceil(total_tokens / avg_chunk_tokens) if total_tokens > 0 else 0
    total_storage_mb = (total_vectors * VECTOR_SIZE_BYTES) / (1024 * 1024)
    return total_vectors, total_storage_mb

def tokens_estimation_per_text(texts_dict, avg_chunk_tokens=AVG_CHUNK_TOKENS):
    """Estimate tokens, vectors and storage per text."""
    for id, text in texts_dict.items():
        total_tokens = len(encoding.encode(text))
        total_vectors = math.ceil(total_tokens / avg_chunk_tokens) if total_tokens > 0 else 0
        total_storage_mb = (total_vectors * VECTOR_SIZE_BYTES) / (1024 * 1024)

        yield id, total_tokens, total_vectors, total_storage_mb

def semantic_text_splitter(text: str) -> list[str]:
    return semantic_splitter.chunks(text)


def text_splitter(text: str, chunk_size: int = AVG_CHUNK_TOKENS) -> list[str]:
    """Splits text into chunks of approximately chunk_size tokens."""
    tokens = encoding.encode(text)
    chunks = []
    for i in range(0, len(tokens), chunk_size):
        chunk_tokens = tokens[i:i + chunk_size]
        chunk_text = encoding.decode(chunk_tokens)
        chunks.append(chunk_text)
    return chunks

def langchain_text_splitter(text: str) -> list[str]:
    """Uses Langchain TokenTextSplitter to split text into chunks."""
    return token_splitter.split_text(text)

def recursive_char_splitter(text: str) -> list[str]:
    return rec_text_splitter.split_text(text)


def get_vectorized_files(texts_dict, splitter) -> list[VectorizedFile]:
    """Creates vectorized files with metadata."""
    vectorized_files = []
    for id, text in texts_dict.items():
        total_tokens = len(encoding.encode(text))
        total_vectors = math.ceil(total_tokens / AVG_CHUNK_TOKENS) if total_tokens > 0 else 0
        total_storage_mb = (total_vectors * VECTOR_SIZE_BYTES) / (1024 * 1024)

        if total_vectors == 1:
            # Simple case: one vector per text
            vectorized_file: VectorizedFile = {
                "file_name": id,
                "vectors": [],  # Placeholder for actual vectors
                "texts": [text],
                "metadata": {
                    "total_tokens": total_tokens,
                    "total_vectors": total_vectors,
                    "estimated_storage_mb": total_storage_mb
                }
            }
            vectorized_files.append(vectorized_file)
        else:
            # Complex case: multiple vectors per text, needs chunking
            chunks = splitter(text) 
            # Recalculate totals based on chunks
            total_tokens = 0
            chunk_vectors = 0
            chunk_storage_mb = 0.0
            for chunk_text in chunks:
                chunk_tokens = len(encoding.encode(chunk_text))
                total_tokens += chunk_tokens
                chunk_vectors += 1 if chunk_tokens > 0 else 0
                chunk_storage_mb += (chunk_vectors * VECTOR_SIZE_BYTES) / (1024 * 1024)

            vectorized_file: VectorizedFile = {
                "file_name": id,
                "vectors": [],  # Placeholder for actual vectors
                "texts": chunks,
                "metadata": {
                    "total_tokens": total_tokens,
                    "total_vectors": chunk_vectors,
                    "estimated_storage_mb": chunk_storage_mb
                }
            }

            vectorized_files.append(vectorized_file)

    return vectorized_files


if __name__ == "__main__":
    files_dict = get_files_as_dict()
    texts = [ text for  text in files_dict.values()] 
    vectors, storage_mb =  combined_token_estimation(texts)
    print("Combined files calculation(just for fun):")
    print(f"Estimated vectors to be created: {vectors}")
    print(f"Estimated vector storage (MB): {storage_mb:.2f} MB")
    print(f"Free tier quota: {VECTOR_QUOTA_MB} MB → usage: {storage_mb/VECTOR_QUOTA_MB:.1%}")

    print("\nTokens per text calculation.:")
    counter = tokens_estimation_per_text(files_dict)
    sum_vectors = 0
    sum_storage = 0
    for id, tokens, vectors, storage_mb in list(counter):  # Print first 10 entries
        sum_vectors += vectors
        sum_storage += storage_mb
        if vectors > 1:
            print(f"ID: {id}, Tokens: {tokens}, Vectors: {vectors}, Estimated storage (MB): {storage_mb:.2f} MB")
            splited_text = text_splitter(files_dict[id])
            for i, chunk in enumerate(splited_text):
                chunk_tokens = len(encoding.encode(chunk))
                print(f"    Chunk {i+1}: {chunk_tokens} tokens - {chunk[:100]}...")
        else:
            print(f"ID: {id}, Tokens: {tokens}, Vectors: {vectors}, Estimated storage (MB): {storage_mb:.2f} MB")

    print(f"\nTotal tokens across all texts: {sum_vectors}")
    print(f"Total estimated storage (MB): {sum_storage:.2f} MB")    
    
    print("\nVectorialize files with langchain_text_splitter:")
    vectorized_files = get_vectorized_files(files_dict, langchain_text_splitter)
    print(f"    Total vectorized files created: {len(vectorized_files)}")
    total_memory_mb = 0
    total_vectors = 0
    for vf in vectorized_files[3:4]:  # Print 2 vectorized files
        print(f"    File: {vf['file_name']}, Vectors: {len(vf['vectors'])}, Text chunks: {len(vf['texts'])}, Metadata: {vf['metadata']}")

    for vf in vectorized_files:
        meta = vf['metadata']
        total_memory_mb += meta.get("estimated_storage_mb", 0)
        total_vectors += meta.get("total_vectors", 0)
    
    print(F"\n    Total estimated vectors: {total_vectors}")
    print(F"    Total estimated memory usage: {total_memory_mb:.2f} MB")
    print(f"    Free tier quota: {VECTOR_QUOTA_MB} MB → usage: {total_memory_mb/VECTOR_QUOTA_MB:.1%}")    


    print("\nVectorialize files with recursive_char_splitter:")
    vectorized_files = get_vectorized_files(files_dict, recursive_char_splitter)
    print(f"    Total vectorized files created: {len(vectorized_files)}")
    total_memory_mb = 0
    total_vectors = 0
    for vf in vectorized_files[3:4]:  # Print 2 vectorized files
        print(f"    File: {vf['file_name']}, Vectors: {len(vf['vectors'])}, Text chunks: {len(vf['texts'])}, Metadata: {vf['metadata']}")

    for vf in vectorized_files:
        meta = vf['metadata']
        total_memory_mb += meta.get("estimated_storage_mb", 0)
        total_vectors += meta.get("total_vectors", 0)
    
    print(F"\n    Total estimated vectors: {total_vectors}")
    print(F"    Total estimated memory usage: {total_memory_mb:.2f} MB")
    print(f"    Free tier quota: {VECTOR_QUOTA_MB} MB → usage: {total_memory_mb/VECTOR_QUOTA_MB:.1%}")    


    #Expected behavior:
    #semantic_text_splitter returns  one text with 512 tokens. higher than the 500 limits.
    print("\nVectorialize files with semantic_text_splitter:")
    vectorized_files = get_vectorized_files(files_dict, semantic_text_splitter)
    print(f"    Total vectorized files created: {len(vectorized_files)}")
    total_memory_mb = 0
    total_vectors = 0
    for vf in vectorized_files[3:4]:  # Print 2 vectorized files
        print(f"    File: {vf['file_name']}, Vectors: {len(vf['vectors'])}, Text chunks: {len(vf['texts'])}, Metadata: {vf['metadata']}")

    for vf in vectorized_files:
        meta = vf['metadata']
        total_memory_mb += meta.get("estimated_storage_mb", 0)
        total_vectors += meta.get("total_vectors", 0)
    
    print(F"\n    Total estimated vectors: {total_vectors}")
    print(F"    Total estimated memory usage: {total_memory_mb:.2f} MB")
    print(f"    Free tier quota: {VECTOR_QUOTA_MB} MB → usage: {total_memory_mb/VECTOR_QUOTA_MB:.1%}")    



