# # from langchain.embeddings import HuggingFaceEmbeddings/
# from langchain_community.embeddings import HuggingFaceEmbeddings
# from langchain_community.vectorstores import FAISS
# from langchain_core.documents import Document
# import os, re, json

# input_dir = "data/cleaned"
# os.makedirs("vector_store", exist_ok=True)

# docs = []
# metadata = []

# for file in os.listdir(input_dir):
#     if file.endswith(".txt"):
#         visa_type = file.split("_")[1]
#         country = file.split("_")[0]
#         text = open(os.path.join(input_dir, file), encoding="utf-8").read().split("### Chunk ")
#         for i, chunk in enumerate(text[1:]):
#             content = re.sub(r'\s+', ' ', chunk.strip())
#             docs.append(Document(page_content=content, metadata={
#                 "id": f"{file}_chunk{i+1}",
#                 "country": country.upper(),
#                 "visa_type": visa_type.title()
#             }))
#             metadata.append({
#                 "id": f"{file}_chunk{i+1}",
#                 "country": country.upper(),
#                 "visa_type": visa_type.title(),
#                 "file": file
#             })

# embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# vectorstore = FAISS.from_documents(docs, embedding_model)

# vectorstore.save_local("vector_store")
# with open("vector_store/metadata.json", "w", encoding="utf-8") as f:
#     json.dump(metadata, f, indent=4)

# print("Vector store created and saved successfully!")


# Use the new langchain_huggingface embeddings
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
import os, re, json

input_dir = "../data/cleaned_policies"
os.makedirs("vector_store", exist_ok=True)

docs = []
metadata = []

# Load text chunks from cleaned files
for file in os.listdir(input_dir):
    if file.endswith(".txt"):
        try:
            country, visa_type = file.split("_")[0], file.split("_")[1]
        except IndexError:
            # fallback in case filename format is unexpected
            country, visa_type = "UNKNOWN", "UNKNOWN"

        with open(os.path.join(input_dir, file), encoding="utf-8") as f:
            text_chunks = f.read().split("### Chunk ")
        
        for i, chunk in enumerate(text_chunks[1:]):  # skip the first split as it's empty
            content = re.sub(r'\s+', ' ', chunk.strip())
            if content:  # skip empty chunks
                docs.append(Document(page_content=content, metadata={
                    "id": f"{file}_chunk{i+1}",
                    "country": country.upper(),
                    "visa_type": visa_type.title()
                }))
                metadata.append({
                    "id": f"{file}_chunk{i+1}",
                    "country": country.upper(),
                    "visa_type": visa_type.title(),
                    "file": file
                })

# Check if we have documents
if not docs:
    raise ValueError("No valid text chunks found. Make sure your cleaned files are not empty!")

# Initialize embedding model
embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# Create FAISS vector store
vectorstore = FAISS.from_documents(docs, embedding_model)

# Save vector store locally
vectorstore.save_local("vector_store")

# Save metadata
with open("vector_store/metadata.json", "w", encoding="utf-8") as f:
    json.dump(metadata, f, indent=4)

print("✅ Vector store created and saved successfully!")
