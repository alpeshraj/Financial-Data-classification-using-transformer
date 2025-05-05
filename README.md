# Financial-Data-classification-using-transformer

# Overview
This project provides an AI-powered solution for automatically identifying the page numbers containing Standalone and Consolidated sections of financial statements within PDF documents.

It focuses on the following statement types:

Balance Sheet

Profit & Loss (P&L) Statement

Cash Flow Statement

The solution is robust to different layouts and scalable to large multi-page PDFs.

# 🔍 Key Features
✅ Text Extraction using pdfplumber and PyPDF2

🤖 LLM-based Classification using FinBERT and SentenceTransformer

📄 Statement Type Detection (Balance Sheet, P&L, Cash Flow)

📊 Consolidation Type Detection (Standalone or Consolidated)

📈 CSV Export of classified page numbers and summaries

# 📁 Dataset
You can collect financial reports (Annual Reports, Financial Statements) from publicly listed companies (e.g., company websites, stock exchanges like NSE, BSE, EDGAR). The dataset should:

Include both Standalone and Consolidated versions.

Vary in structure, length, and formatting for generalization.

# 🧰 Dependencies
Install required packages using:

bash
Copy
Edit
pip install torch transformers pdfplumber PyPDF2 sentence-transformers scikit-learn pandas
# 🚀 How It Works
1. Text Extraction
Each page of the uploaded PDF is parsed using pdfplumber (fallback to PyPDF2 if needed).

pages = extract_text_from_pdf("report.pdf")
2. Model Loading
Two models are used:

FinBERT (for sentiment but heuristically used to detect "consolidated"/"standalone")

Sentence-BERT (semantic similarity for detecting statement types)

models = load_models()
3. Classification
Each page is classified by:

Consolidation Type: using heuristics and keyword presence (e.g., “consolidated” or “standalone”)

Statement Type: using sentence embeddings and cosine similarity against known statement descriptions

consolidation, stmt_type = classify_with_llm(page_text, models)
4. Output Results
The final result is a dictionary of page numbers organized by statement and consolidation types. This is exported as a CSV.

report_results.csv
# 📊 Sample Output
Consolidation,Statement Type,Page Number,Text Excerpt
consolidated,balance_sheet,3,"Statement of Financial Position as at..."
standalone,profit_loss,7,"Standalone Profit and Loss Statement..."
# 📈 Performance Metrics
You can evaluate model performance by manually labeling a test set and computing:

Accuracy

Precision/Recall

Confusion Matrix

Since the consolidation classifier uses heuristics, this can be improved in future by fine-tuning a custom transformer classifier.

# 📦 Scalability
The pipeline is designed to:

Handle large PDF files efficiently

Skip empty pages

Minimize classification errors using fallback logic

# 📝 Instructions to Run
Clone the repo:
git clone https://github.com/yourusername/financial-statement-classifier.git
cd financial-statement-classifier
Run the script:
python classify_financials.py
Upload the PDF when prompted.

The results will be printed and saved as a .csv.

# 📄 Future Improvements
Fine-tune a custom transformer for consolidation classification.

Add support for multilingual PDFs.

Build a Streamlit UI for easy use.

Integrate with cloud storage APIs.

