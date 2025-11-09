# MaRGen-MultiAgent-Restaurant-Analysis  
_MaRGen-inspired multi-agent system for automated restaurant market research & sales optimization_

## 📋 Team & Contributors  
- Ganesh Paparaju  
- Vaibhavi Shinde  
- Deepak Reddy  

## 🎯 Project Overview  
This project implements a workflow inspired by the :contentReference[oaicite:0]{index=0} research paper.  
Rather than focusing on e-commerce, we apply the approach to the restaurant industry:  
- **Data sources**: Yelp restaurant sales data + menu-item sales data.  
- **Goal**: Serve as an AI consulting system — analyze restaurant performance, identify optimization opportunities (e.g., promotions, weather, menu categories), and generate actionable reports.

## 🧠 System Workflow  
1. **User Query / Business Goal**  
   - Example: “Analyze cuisine performance, promotion impact, and weather effects to recommend strategies for boosting restaurant sales.”  
2. **Retriever Agent**  
   - Parses the natural-language query, filters relevant data (restaurant level or full market).  
3. **Researcher Agent**  
   - Conducts statistical analysis, generates key metrics and visual charts.  
   - Insights include: top-categories, promotion effect, weather impact, monthly trends.  
4. **Writer Agent**  
   - Builds a structured markdown report in “consulting style” summarizing findings and recommendations.  
5. **Reviewer Agent**  
   - Uses LLM (or fallback logic) to refine the draft report: clarity, coherence, actionability.  
6. **Streamlit UI**  
   - Interactive demo showing step-by-step how the agents collaborate.  
   - Data preview, retrieved results, visualizations, draft vs final report, export buttons.

## 🔧 Getting Started  
### Prerequisites  
- Python 3.x  
- [Streamlit](https://streamlit.io/)  
- Other dependencies listed in `requirements.txt`  
- (Optional) Local LLM via [:contentReference[oaicite:1]{index=1} for full functionality  

### Installation  
```bash
git clone https://github.com/GaneshPaparaju/MaRGen-MultiAgent-Restaurant-Analysis.git
cd MaRGen-MultiAgent-Restaurant-Analysis
pip install -r requirements.txt
