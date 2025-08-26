import chromadb
client = chromadb.Client() # Can be set to save to disk
collection = client.create_collection("sales_reports")

collection.upsert(
    # documents=["Sales for week 1 were $500...", "Week 2 sales were $650..."],
    # metadatas=[{"week": 1}, {"week": 2}],
    # ids=["week1", "week2"]
    documents=[
        "This is a document about pineapple",
        "This is a document about oranges"
    ],
    ids=["id1", "id2"]
)

results = collection.query(
    #query_texts=["What were the weekly sales?"],
    query_texts=["This is a query document about florida"], # Chroma will embed this for you
    n_results=2 # how many results to return
)
print("Results:")
print(results)