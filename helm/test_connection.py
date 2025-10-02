from pymilvus import connections, utility

import argparse

parser = argparse.ArgumentParser(description="Test Connection to AKS cluster")
parser.add_argument("clusterIP", type=str, help="Cluster IP Address in AKS")

args = parser.parse_args()

print(f"Testing connection to AKS cluster: {args.clusterIP}")
connections.connect("default", host=args.clusterIP, port="19530")
print("Milvus connected:", utility.get_server_version())
