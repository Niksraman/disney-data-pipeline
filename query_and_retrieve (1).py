# -*- coding: utf-8 -*-
"""Query and Retrieve.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/18MlOqc2peim4203rgfVq-Q8fbyB6UfOd
"""

import faiss
import numpy as np
import pandas as pd
from flask import Flask, request, jsonify
from sqlalchemy import create_engine
from sentence_transformers import SentenceTransformer

# Configurations
DB_URL = "sqlite:///data_storage.db"  # Database connection URL
TABLE_NAME = "preprocessed_table"  # Table name in the database
INDEX_PATH = "vector_index.index"  # Path to FAISS index
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"  # Pre-trained model for embeddings

# Load FAISS index and model
index = faiss.read_index(INDEX_PATH)
model = SentenceTransformer(MODEL_NAME)

# Initialize Flask app
app = Flask(__name__)

# Database connection
engine = create_engine(DB_URL)

# 1. Retrieve Records from Database
def retrieve_records(ids):
    """
    Retrieve records from the database corresponding to the given IDs.
    """
    with engine.connect() as conn:
        query = f"SELECT * FROM {TABLE_NAME} WHERE id IN ({','.join(map(str, ids))})"
        results = pd.read_sql(query, conn)
    return results.to_dict(orient="records")

# 2. Perform Similarity Search
def query_vector_store(prompt, top_k=5):
    """
    Query the FAISS index to find the most similar embeddings to the given prompt.
    """
    # Generate embedding for the query prompt
    query_embedding = model.encode([prompt])

    # Search for top_k similar embeddings
    distances, indices = index.search(query_embedding, top_k)
    return indices[0], distances[0]

# 3. Generate Response using RAG
def generate_rag_response(prompt, retrieved_data):
    """
    Generate a response based on the query and retrieved data using a language model.
    """
    # Simulate a response generation (replace with an actual LLM call for production)
    retrieved_text = "\n".join([record["description"] for record in retrieved_data])
    response = (
        f"Query: {prompt}\n\n"
        f"Retrieved Information:\n{retrieved_text}\n\n"
        f"Summary: Based on the retrieved data, here are the relevant insights."
    )
    return response

# 4. API Endpoint
@app.route("/query", methods=["POST"])
def query():
    """
    API endpoint to perform similarity search and RAG-based response generation.
    """
    data = request.json
    prompt = data.get("prompt")
    top_k = data.get("top_k", 5)

    if not prompt:
        return jsonify({"error": "Prompt is required"}), 400

    # Query FAISS and retrieve records
    indices, distances = query_vector_store(prompt, top_k=top_k)
    retrieved_data = retrieve_records(indices)

    # Generate RAG-based response
    response = generate_rag_response(prompt, retrieved_data)

    return jsonify({
        "query": prompt,
        "retrieved": retrieved_data,
        "response": response
    })

# Run the app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)