# -*- coding: utf-8 -*-
"""classification_using_transformer.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/167AcL1Jue_AXE426UluRfvVdJ1wdmrmK
"""

!pip install PyPDF2 pdfplumber transformers torch sentence-transformers pandas

# Import libraries
import PyPDF2
import pdfplumber
import pandas as pd
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import io
from google.colab import files

# @title PDF Text Extraction (Improved)
def extract_text_from_pdf(pdf_path):
    """Robust text extraction with error handling"""
    full_text = []

    try:
        # First try pdfplumber for better accuracy
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                full_text.append(text if text else "")

        # Fallback to PyPDF2 if pdfplumber fails
        if not any(full_text):
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                full_text = [page.extract_text() or "" for page in pdf_reader.pages]

    except Exception as e:
        print(f"Error extracting text: {e}")
        return []

    return full_text

# @title Load LLM Models
def load_models():
    """Load transformer models for classification"""
    # Load a financial NLP model for consolidation detection
    consolidation_tokenizer = AutoTokenizer.from_pretrained("yiyanghkust/finbert-tone")
    consolidation_model = AutoModelForSequenceClassification.from_pretrained("yiyanghkust/finbert-tone")

    # Load sentence transformer for semantic similarity
    st_model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

    # Define our statement type categories
    statement_types = {
        'balance_sheet': [
            "balance sheet",
            "statement of financial position",
            "assets and liabilities"
        ],
        'profit_loss': [
            "income statement",
            "profit and loss",
            "statement of operations"
        ],
        'cash_flow': [
            "cash flow statement",
            "statement of cash flows"
        ]
    }

    # Pre-compute embeddings for our categories
    category_embeddings = {}
    for st_type, phrases in statement_types.items():
        category_embeddings[st_type] = st_model.encode(phrases)

    return {
        'consolidation': {
            'tokenizer': consolidation_tokenizer,
            'model': consolidation_model
        },
        'statement': {
            'model': st_model,
            'categories': category_embeddings
        }
    }

# @title Classification with Transformers
def classify_with_llm(text, models):
    """Classify text using transformer models"""
    # Consolidation detection
    consolidation_inputs = models['consolidation']['tokenizer'](
        text,
        return_tensors="pt",
        truncation=True,
        max_length=512
    )

    with torch.no_grad():
        consolidation_logits = models['consolidation']['model'](**consolidation_inputs).logits

    # Simple heuristic: look for "consolidated" in text as FinBERT isn't trained for this specific task
    text_lower = text.lower()
    if 'consolidated' in text_lower:
        consolidation = 'consolidated'
    elif 'standalone' in text_lower or 'individual' in text_lower:
        consolidation = 'standalone'
    else:
        # Default to consolidated if no clear signal
        consolidation = 'consolidated'

    # Statement type detection using semantic similarity
    text_embedding = models['statement']['model'].encode(text)

    best_score = -1
    best_type = 'balance_sheet'  # default

    for st_type, embeddings in models['statement']['categories'].items():
        similarities = cosine_similarity(
            [text_embedding],
            embeddings
        )
        max_similarity = np.max(similarities)
        if max_similarity > best_score:
            best_score = max_similarity
            best_type = st_type

    # Confidence threshold
    if best_score < 0.3:  # Low confidence
        # Fallback to keyword matching
        if 'cash flow' in text_lower:
            best_type = 'cash_flow'
        elif 'profit' in text_lower or 'income' in text_lower:
            best_type = 'profit_loss'
        else:
            best_type = 'balance_sheet'

    return consolidation, best_type

# @title Processing Pipeline with LLMs
def process_pdf_with_llm(pdf_path, models):
    """Process PDF using LLM classification"""
    pages = extract_text_from_pdf(pdf_path)

    results = {
        'standalone': {'balance_sheet': [], 'profit_loss': [], 'cash_flow': []},
        'consolidated': {'balance_sheet': [], 'profit_loss': [], 'cash_flow': []}
    }

    for i, page_text in enumerate(pages):
        if len(page_text.strip()) < 50:  # Skip empty pages
            continue

        try:
            consolidation, stmt_type = classify_with_llm(page_text, models)
            results[consolidation][stmt_type].append(i+1)  # 1-based page numbers
        except Exception as e:
            print(f"Error processing page {i+1}: {e}")
            continue

    return results

# @title Main Execution
def main():
    # Upload PDF file
    print("Please upload your financial PDF file:")
    uploaded = files.upload()
    pdf_filename = next(iter(uploaded))

    # Load models (this may take a few minutes first time)
    print("\nLoading transformer models...")
    models = load_models()

    # Process PDF
    print("\nProcessing PDF with LLM classification...")
    results = process_pdf_with_llm(pdf_filename, models)

    # Display results
    print("\nClassification Results:")
    print("="*40)
    for consolidation_type in results:
        print(f"\n{consolidation_type.upper()} STATEMENTS:")
        for stmt_type, pages in results[consolidation_type].items():
            if pages:
                print(f"- {stmt_type.replace('_', ' ').title()}: Pages {', '.join(map(str, pages))}")

    # Save results to CSV
    result_data = []
    for consolidation in results:
        for stmt_type in results[consolidation]:
            for page in results[consolidation][stmt_type]:
                result_data.append({
                    'Consolidation': consolidation,
                    'Statement Type': stmt_type,
                    'Page Number': page,
                    'Text Excerpt': pages[page-1][:100] + "..." if len(pages) > page-1 else ""
                })

    result_df = pd.DataFrame(result_data)
    csv_filename = pdf_filename.replace('.pdf', '_results.csv')
    result_df.to_csv(csv_filename, index=False)
    print(f"\nResults saved to {csv_filename}")
    files.download(csv_filename)

if __name__ == "__main__":
    main()