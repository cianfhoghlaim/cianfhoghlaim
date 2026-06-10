from elasticsearch import Elasticsearch
import json

# Connect to Elasticsearch
es = Elasticsearch(
    ['https://elastic.cairogenizah.ai'],
    basic_auth=('cairo_user', 'cairo_secure_123')
)

# Backup index
index_name = 'rylands_testing_v4.3_0'
output_file = f'{index_name}_backup.json'

print(f"Backing up {index_name}...")

with open(output_file, 'w') as f:
    # Use scan helper to get all documents
    from elasticsearch.helpers import scan
    
    docs = scan(es, index=index_name, query={"query": {"match_all": {}}})
    
    count = 0
    for doc in docs:
        f.write(json.dumps(doc) + '\n')
        count += 1
        if count % 1000 == 0:
            print(f"Backed up {count} documents...")
    
    print(f"Complete! Backed up {count} documents to {output_file}")

