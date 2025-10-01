from pymilvus import connections, utility

connections.connect("default", host="127.0.0.1", port="19530")
print("Milvus connected:", utility.get_server_version())
