import spacy
from keybert import KeyBERT
from transformers import pipeline
import streamlit as st  # add this at the top
import logging
import pymupdf as fitz
import docx
from docx import Document

@st.cache_resource
def load_models():
    
    try:
        
        kw_model = KeyBERT('distilbert-base-nli-mean-tokens')
        summarizer = pipeline(
            "summarization", 
            model="facebook/bart-large-cnn",
            tokenizer="facebook/bart-large-cnn"
        )
        
        # Load spaCy model
        nlp = spacy.load("en_core_web_sm")
        
        return kw_model, summarizer, nlp
    except Exception as e:
        f"Error loading models: {e}"
        # Fallback to simpler models
        kw_model = KeyBERT()
        summarizer = pipeline("summarization", model="t5-small")
        nlp = spacy.load("en_core_web_sm")
        return kw_model, summarizer, nlp

    
kw_model, summarizer ,nlp= load_models()

def extract_keywords(text, top_n=10):
    keywords = kw_model.extract_keywords(text, keyphrase_ngram_range=(1, 3), stop_words='english', use_maxsum=True, nr_candidates=25)
    return [kw for kw, score in keywords]

def generate_summary(text, sentence_count=3,max_length: int = 150, min_length: int = 30):
    word_count = len(text.split())

    try:
        # If very short text, return it directly
        if word_count < 20:
            return text.strip()

        
        if word_count < 80:
            sentences = list(nlp(text).sents)
            return ' '.join(sent.text for sent in sentences[:min(sentence_count, len(sentences))])
        
        # For longer text, use BART summarizer
        summary_output = summarizer(
            text,
            max_length,
            min_length,
            do_sample=False
        )
        return summary_output[0]['summary_text']

    except Exception as e:
        return "Summary generation failed: " + str(e)
def genrate_entities(text:str):
    if not text:
        return []
    
    try:
        doc = nlp(text)
        
        # Filter out low-confidence or irrelevant entities
        entities = []
        seen_entities = set()
        
        for ent in doc.ents:
            # Skip very short entities or those with only digits
            if len(ent.text.strip()) < 2 or ent.text.strip().isdigit():
                continue
            
            # Avoid duplicates 
            entity_lower = ent.text.strip().lower()
            if entity_lower not in seen_entities:
                entities.append((ent.text.strip(), ent.label_))
                seen_entities.add(entity_lower)
        
        return entities[:20]  
    
    except Exception as e:
        (f"Entity extraction failed: {e}")
        return []

def pdf_auth(file_path):
    doc = fitz.open(file_path)
    metadata = doc.metadata
    return metadata.get("author") or metadata.get("Author")
def docx_auth(file_path):
    doc = Document(file_path)
    core_props = docx.core_properties
    return core_props.author
import re

def guess_auth(text):
    lines = text.lower().split('\n')[:20]

    # Common patterns to search
    patterns = [
        r"(?:written|created|authored|by)\s+(mr\.?\s*)?([a-z]\.?\s*){0,3}[a-z]+",  # initials + surname
        r"(?:written|created|authored|by)\s+[a-z]+(?:\s+[a-z]+){0,3}"              # full name with up to 3 words
    ]

    for line in lines:
        for pattern in patterns:
            match = re.search(pattern, line)
            if match:
                raw = match.group()
                # Clean and format result
                author = raw.replace("written", "").replace("created", "").replace("authored", "").replace("by", "")
                author = author.strip(" ,:\n\t")
                return author.title()

    # Fallback to NER
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ == "PERSON" and ent.start_char < 200:
            return ent.text

    return None
import os

# File size

def extract_title(text):
    doc = nlp(text)

    for sent in list(doc.sents)[:5]:
        cleaned = sent.text.strip()
        if 5 <= len(cleaned.split()) <= 15:
            return cleaned

    noun_chunks = [chunk.text.strip() for chunk in doc.noun_chunks if 3 <= len(chunk.text.split()) <= 10]
    if noun_chunks:
        return max(noun_chunks, key=len)

    
    return list(doc.sents)[0].text.strip() if doc.sents else "Untitled Document"

def file_info(file_path=None):
    if file_path:
        try:
            size_bytes = os.path.getsize(file_path)
            file_size = f"{size_bytes / (1024 * 1024):.2f} MB"
            file_format = os.path.splitext(file_path)[-1].lower()
        except:
            file_size = "Unknown"
            file_format = "Unknown"
    else:
        file_size = "Unknown"
        file_format = "Unknown"

    return file_size, file_format



def extract_metadata(text,file_path=None):
    doc = nlp(text)

    # Heuristic title: first sentence or longest noun chunk
    title = list(doc.sents)[0].text if doc.sents else "Untitled Document"
    #author
    author = None
    if file_path:
        if file_path.endswith(".pdf"):
            author = pdf_auth(file_path)
        elif file_path.endswith(".docx"):
            author = docx_auth(file_path)
    if not author:
        author = guess_auth(text)

    # Keywords: extract unique lowercased noun chunks (1-3 words)
    keywords = extract_keywords(text)

    # Named Entities: extract entities with labels
    entities=genrate_entities(text)
    #title
    title = extract_title(text)


   #summary
    summary_adv= generate_summary(text)
    # Return metadata dictionary
    file_size, file_format = file_info(file_path)
    metadata = {
        "title": title.strip(),
        "Author":author if author else "Unknown",
        "keywords": keywords,
        "entities": entities,
        "summary":summary_adv.strip(),
        "file_format": file_format,
        "file_size": file_size,
       
    }
    

    return metadata
