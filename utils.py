import streamlit as st
import requests
import base64
import json
import os
import fitz
import io
import re
from PIL import Image
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

# FastAPI endpoint URLs
API_URL = "http://localhost:8000"

def get_response_from_api(prompt, context=None):
    try:
        if 'mistral_api_key' not in st.session_state:
            return "Please enter your Mistral API key in the sidebar settings"
            
        response = requests.post(
            f"{API_URL}/chat",
            json={
                "prompt": prompt,
                "context": context,
                "api_key": st.session_state['mistral_api_key']})

        response.raise_for_status()
        return response.json()["response"]
    except Exception as e:
        return f"Error: {str(e)}"


def get_vision_response(image_path, prompt="What's in this image?"):
    try:
        if 'mistral_api_key' not in st.session_state:
            return "Please enter your Mistral API key in the sidebar settings"   
        with open(image_path, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode('utf-8')
        
        response = requests.post(
            f"{API_URL}/vision",
            json={"image": base64_image,
                "prompt": prompt,
                "api_key": st.session_state['mistral_api_key']})
        response.raise_for_status()
        return response.json()["response"]
    except Exception as e:
        return f"Error: {str(e)}"
        
# def handle_extracted_images(img_data, idx):    
#     # with st.expander(f"📄 Page {img_data['page']} - Image {idx + 1}"):
#         st.image(img_data['image'], 
#                 caption=f"Image {idx + 1} from page {img_data['page']}", 
#                 use_column_width=True)

def extract_text_and_images_with_mapping(pdf_path, embeddings=None, vector_store=None):
    text_image_mappings = []
    image_texts = []
    image_metadatas = []
    try:
        pdf_document = fitz.open(pdf_path)
        for page_num in range(len(pdf_document)):
            page = pdf_document[page_num]
            text_blocks = page.get_text("blocks")
            for img_index, img in enumerate(page.get_images(full=True)):
                try:
                    xref = img[0]
                    base_image = pdf_document.extract_image(xref)
                    image_bytes = base_image["image"]
                    image = Image.open(io.BytesIO(image_bytes))
                    img_rect = page.get_image_bbox(img)
                    nearby_text = ""
                    for block in text_blocks:
                        block_rect = fitz.Rect(block[:4])
                        if abs(block_rect.y0 - img_rect.y1) < 100 or abs(img_rect.y0 - block_rect.y1) < 100:
                            nearby_text += block[4] + " "
                    image_id = f"page_{page_num + 1}_img_{img_index}"
                    clean_text = re.sub(r'<image:[^>]+>', '', nearby_text)
                    clean_text = re.sub(r'\s+', ' ', clean_text.strip().replace('\n', ' '))
                    # Store mapping in memory
                    mapping = {
                        "image_id": image_id,
                        "page_number": page_num + 1,
                        "nearby_text": clean_text,
                        "location": {
                            "top": img_rect.y0,
                            "bottom": img_rect.y1,
                            "left": img_rect.x0,
                            "right": img_rect.x1},
                        "image_base64": base64.b64encode(image_bytes).decode('utf-8')
                    }
                    text_image_mappings.append(mapping)
                    image_texts.append(clean_text)
                    image_metadatas.append(mapping)
                    image.close()
                except Exception as e:
                    print(f"Error processing image {img_index} on page {page_num + 1}: {e}")
    except Exception as e:
        print(f"Error opening or reading the PDF: {e}")
    finally:
        if 'pdf_document' in locals():
            pdf_document.close()
    # Store in vector DB if embeddings and vector_store are provided
    if embeddings is not None:
        if vector_store is None:
            vector_store = FAISS.from_texts(image_texts, embeddings, metadatas=image_metadatas)
        else:
            vector_store.add_texts(image_texts, metadatas=image_metadatas)
    return text_image_mappings, vector_store


def save_text_image_mappings(mappings, output_file="text_image_mappings.json"):
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(mappings, f, indent=4)


def find_relevant_images_vector(query_text, vector_store, similarity_threshold=0.5, top_k=3):
    # Use the vector store to search for relevant images
    results = vector_store.similarity_search_with_score(query_text, k=top_k)
    relevant_images = []
    for doc, score in results:
        if score >= similarity_threshold:
            meta = doc.metadata
            relevant_images.append({
                'image_base64': meta.get('image_base64'),
                'similarity': float(score),
                'nearby_text': meta.get('nearby_text'),
                'page_number': meta.get('page_number'),
                'location': meta.get('location'),
                'image_id': meta.get('image_id'),
            })
    return relevant_images
