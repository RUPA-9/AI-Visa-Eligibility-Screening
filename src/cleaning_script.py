# import os, re
# from langchain_text_splitters import RecursiveCharacterTextSplitter

# input_dir = "../data/policies"
# output_dir = "../data/cleaned_policies"

# os.makedirs(output_dir, exist_ok=True)
# splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)

# for file in os.listdir(input_dir):
#     if file.endswith(".txt"):
#         text = open(os.path.join(input_dir, file), encoding="utf-8").read()
#         cleaned = re.sub(r'\s+', ' ', text)
#         chunks = splitter.split_text(cleaned)
#         with open(os.path.join(output_dir, file), "w", encoding="utf-8") as f:
#             for i, chunk in enumerate(chunks):
#                 f.write(f"### Chunk {i+1}\n{chunk}\n\n")


import os, re
import pdfplumber
from langchain_text_splitters import RecursiveCharacterTextSplitter

input_dir = "../data/policies"
output_dir = "../data/cleaned_policies"
os.makedirs(output_dir, exist_ok=True)

splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,  # Slightly larger chunks
    chunk_overlap=200,  # More overlap for better context
    separators=["\n## ", "\n### ", "\n\n", "\n", ". "]  # Custom separators
)

def process_file(file_path, output_path):
    """Process a single file and save chunks"""
    # Read the file
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()
    
    # Clean text while preserving important whitespace
    cleaned = re.sub(r'[ \t]+', ' ', text)
    cleaned = re.sub(r'\n\s*\n', '\n\n', cleaned)
    
    # Split into chunks
    chunks = splitter.split_text(cleaned)
    
    # Save chunks
    with open(output_path, "w", encoding="utf-8") as f:
        for i, chunk in enumerate(chunks, 1):
            f.write(f"### Chunk {i}\n{chunk.strip()}\n\n")

# Process all files
for file in os.listdir(input_dir):
    file_path = os.path.join(input_dir, file)
    if file.lower().endswith('.pdf'):
        # Handle PDFs
        text = ""
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() + "\n"
        
        # Save extracted text first
        txt_path = os.path.join(input_dir, file.replace('.pdf', '.txt'))
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(text)
        
        # Process the text file
        out_file = os.path.join(output_dir, file.replace('.pdf', '.txt'))
        process_file(txt_path, out_file)
        
    elif file.lower().endswith('.txt'):
        # Process text files directly
        out_file = os.path.join(output_dir, file)
        process_file(file_path, out_file)

print("PDF cleaning and chunking done!")
