# 🍽️ MaRGen-Inspired Multi-Agent Restaurant Market Analysis

This project is a **MaRGen-inspired multi-agent system** that performs **automated market research and sales optimization** for restaurant businesses.

The system demonstrates how **multiple LLM agents** can collaborate just like a consulting workflow — retrieving data, analyzing trends, writing insights, and refining recommendations — **with minimal human input**.

---

## 👥 Team Members (Team 4)
| Name | Role |
|-----|------|
| **Vaibhavi Shinde** | Research & Presentation |
| **Deepak Reddy** | Model + Demo Integration |
| **Ganesh Paparaju** | Agent Pipeline + UI Development |

---

## 🎯 Project Goal

Traditional market research is **slow, expensive, and requires human analysts**.  
Inspired by the **MaRGen (2025)** research paper (Amazon Science), this project aims to:

✅ Automate data analysis  
✅ Generate professional market insight reports  
✅ Provide strategy recommendations for sales optimization  
✅ Reduce time and cost of analysis  

---

## 🧠 System Architecture

User Query
↓
[Retriever Agent] → Retrieves relevant data from restaurant + menu datasets
↓
[Researcher Agent] → Analyzes trends, creates metrics, & generates charts
↓
[Writer Agent] → Drafts structured business insights report (Markdown)
↓
[Reviewer Agent] → Refines report for clarity, strategy depth & narrative quality

---

## 📂 Tech Stack

| Component | Tool |
|---------|------|
| UI | **Streamlit** |
| Agents | Local LLMs via **Ollama** (llama3.1 / mistral / qwen) |
| Data Processing | **Pandas**, **NumPy** |
| Visualization | **Matplotlib**, **Seaborn** |
| Environment | Python 3.11+ |

---

## 📊 Dataset

The demo uses sample restaurant business + menu data:
data/
├── Hybrid_Yelp_Restaurant_Sales.csv → Ratings, reviews, location, identifiers
└── Menu_Sales_Data.csv → Menu items, revenue, categories, dates


---

## 🚀 Running the Demo

### 1️⃣ Install Requirements
```bash
pip install -r requirements.txt
ollama pull llama3.1
streamlit run app.py
