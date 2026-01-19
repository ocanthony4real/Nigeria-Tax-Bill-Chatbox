# from qdrant_client import QdrantClient

# from llm_engineering.application.networks import EmbeddingModelSingleton

# embedding_model = EmbeddingModelSingleton()

# QDRANT_URL = "https://ae706315-0257-4bfd-b767-47c7ba935a8e.us-east4-0.gcp.cloud.qdrant.io"
# QDRANT_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.s4H-g9hKhphYhkfuSRg-XWGtmCzC1W50GpeVxyGQDp4"
# COLLECTION_NAME = "embedded_tax_bill_chunks"

# client = QdrantClient(
#     url=QDRANT_URL,
#     api_key=QDRANT_API_KEY,
# )

# # 1️⃣ Fetch ONE point with vectors
# points, _ = client.scroll(
#     collection_name=COLLECTION_NAME,
#     limit=1,
#     with_vectors=True,
# )

# point = points[0]

# print("ID:", point.id)



# query = "tax rate on personal income"

# hits = client.search(
#     collection_name=COLLECTION_NAME,
#     query_vector=embedding_model.encode(query).tolist(),
#     limit=5,
# )

# for hit in hits:
#     print(hit.score, hit.payload["file_name"], hit.payload["page_number"])

import torch
print(f'PyTorch CUDA version: {torch.version.cuda}')