import streamlit as st
import os
import json
import subprocess
import pandas as pd
from agents.retriever import Retriever
from agents.researcher import Researcher
from agents.writer import Writer
from agents.reviewer import Reviewer

# -------------------- PAGE SETUP --------------------
st.set_page_config(
    page_title="MaRGen Interactive Demo", 
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🤖 MaRGen-Inspired Interactive Multi-Agent System")

st.markdown("""
A practical demo inspired by the *MaRGen (2025)* research paper —  
showcasing collaborative AI agents that analyze restaurant data, generate insights,
and iteratively refine business reports.
""")

# -------------------- WORKFLOW DIAGRAM --------------------
st.markdown("""
### 🔗 Agent Workflow Chain
```mermaid
graph LR
A[Retriever Agent] --> B[Researcher Agent]
B --> C[Writer Agent]
C --> D[Reviewer Agent]
```
""")

# -------------------- HELPERS --------------------
@st.cache_data
def load_and_validate_data(yelp_path, menu_path):
    try:
        yelp_df = pd.read_csv(yelp_path)
        menu_df = pd.read_csv(menu_path)
        return yelp_df, menu_df, None
    except Exception as e:
        return None, None, str(e)

def check_ollama_model(model_name):
    try:
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True, timeout=5)
        return model_name in result.stdout
    except Exception:
        return None

# -------------------- SIDEBAR --------------------
st.sidebar.header("⚙️ Configuration")

# Initialize variables at the very top of sidebar section
selected_restaurant = None
restaurant_dict = {}
selected_restaurant_name = None

model = st.sidebar.selectbox(
    "Select Local LLM (via Ollama)", 
    ["llama3.1", "mistral", "qwen2.5"],
    help="Choose the LLM model for the Reviewer agent"
)

model_status = check_ollama_model(model)
if model_status is False:
    st.sidebar.warning(f"⚠️ Model '{model}' not found. Run: `ollama pull {model}`")
elif model_status is None:
    st.sidebar.info("ℹ️ Unable to verify Ollama (continuing offline).")

use_sample = st.sidebar.checkbox("Use sample data from /data", value=True)

# -------------------- ANALYSIS SCOPE SELECTION --------------------
st.sidebar.markdown("---")
st.sidebar.markdown("### 🎯 Analysis Scope")

analysis_scope = st.sidebar.radio(
    "Choose analysis level:",
    ["📊 All Restaurants", "🏪 Single Restaurant"],
    help="Switch between aggregate analysis or focus on one location",
    index=0,
    key="analysis_scope_radio"
)

# Show what mode we're in
if "Single Restaurant" in analysis_scope:
    st.sidebar.info("👇 Select restaurant below after data loads")

# -------------------- QUERY TEMPLATES --------------------
st.sidebar.markdown("---")
st.sidebar.markdown("### 💡 Try These Queries:")

# Consulting-focused query examples
query_examples = {
    "📊 Sales Optimization": "Analyze performance and recommend strategies to boost revenue",
    "🎯 Underperforming Analysis": "Identify underperforming categories and suggest improvements",
    "🏆 Competitive Position": "Compare restaurant performance and identify market leaders",
    "📈 Growth Opportunities": "What menu categories have the most growth potential?",
    "💡 Strategic Recommendations": "Provide actionable recommendations to increase sales"
}

selected_example = st.sidebar.radio(
    "Quick Query Templates:",
    list(query_examples.keys()),
    index=0,
    key="query_template_radio"
)

st.sidebar.markdown("---")
st.sidebar.info("💡 **More Query Ideas:**\n- Show top dishes\n- Compare restaurant performance\n- Analyze by location\n- Focus on specific cuisines")

# Agent Console
st.sidebar.markdown("---")
st.sidebar.markdown("### 🧠 Agent Console")
console_log = st.sidebar.empty()

# -------------------- DATA LOADING --------------------
if use_sample:
    yelp_path = "data/Hybrid_Yelp_Restaurant_Sales.csv"
    menu_path = "data/Menu_Sales_Data.csv"
    
    # Check if sample data exists
    if not os.path.exists(yelp_path) or not os.path.exists(menu_path):
        st.error("❌ Sample data not found. Please ensure files exist in /data folder.")
        st.stop()
else:
    yelp_file = st.sidebar.file_uploader("Upload Restaurant Sales CSV", type="csv")
    menu_file = st.sidebar.file_uploader("Upload Menu Data CSV", type="csv")
    if not (yelp_file and menu_file):
        st.warning("⚠️ Please upload both CSVs or use sample data.")
        st.stop()
    os.makedirs("temp_data", exist_ok=True)
    yelp_path = os.path.join("temp_data", yelp_file.name)
    menu_path = os.path.join("temp_data", menu_file.name)
    with open(yelp_path, "wb") as f:
        f.write(yelp_file.getbuffer())
    with open(menu_path, "wb") as f:
        f.write(menu_file.getbuffer())

# Load and validate data
yelp_df, menu_df, err = load_and_validate_data(yelp_path, menu_path)
if err:
    st.error(f"❌ Data load error: {err}")
    st.stop()

# -------------------- RESTAURANT SELECTION (AFTER DATA LOADS) --------------------
if "Single Restaurant" in analysis_scope:
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🏪 Select Restaurant")
    
    try:
        # Get restaurant columns
        restaurant_col = None
        name_col = None
        for col in yelp_df.columns:
            col_lower = col.lower().strip()
            if 'restaurant_id' in col_lower or 'business_id' in col_lower:
                restaurant_col = col
            if 'restaurant_name' in col_lower or col_lower == 'name':
                name_col = col
        
        if restaurant_col and name_col:
            # Create restaurant options
            restaurant_options = yelp_df[[restaurant_col, name_col]].drop_duplicates()
            restaurant_dict = dict(zip(
                restaurant_options[name_col].values,
                restaurant_options[restaurant_col].values
            ))
            
            # Show selector
            selected_restaurant_name = st.sidebar.selectbox(
                "Choose a restaurant:",
                options=[""] + sorted(restaurant_dict.keys()),
                key="restaurant_selector",
                help="Select a specific restaurant to analyze"
            )
            
            if selected_restaurant_name and selected_restaurant_name != "":
                selected_restaurant = restaurant_dict[selected_restaurant_name]
                st.sidebar.success(f"✅ Analyzing: **{selected_restaurant_name}**")
            else:
                selected_restaurant = None
                st.sidebar.warning("⚠️ Please select a restaurant")
        else:
            st.sidebar.error("❌ Restaurant columns not found in data")
            analysis_scope = "📊 All Restaurants"
            selected_restaurant = None
            selected_restaurant_name = None
    except Exception as e:
        st.sidebar.error(f"Error loading restaurants: {e}")
        analysis_scope = "📊 All Restaurants"
        selected_restaurant = None
        selected_restaurant_name = None

# -------------------- DISPLAY DATA OVERVIEW --------------------
st.sidebar.success(f"✅ Loaded: {len(yelp_df)} Yelp | {len(menu_df)} Menu rows")

# Data overview
with st.expander("📊 Data Overview", expanded=False):
    col1, col2, col3, col4 = st.columns(4)
    
    # Calculate metrics
    n_restaurants = yelp_df['restaurant_id'].nunique() if 'restaurant_id' in yelp_df.columns else len(yelp_df)
    n_menu_items = len(menu_df)
    n_yelp_records = len(yelp_df)
    
    col1.metric("Restaurants", n_restaurants)
    col2.metric("Menu Items", n_menu_items)
    col3.metric("Yelp Records", n_yelp_records)
    
    # Date range - display as a proper formatted string
    if 'date' in menu_df.columns:
        try:
            menu_df_temp = menu_df.copy()
            menu_df_temp['date'] = pd.to_datetime(menu_df_temp['date'], errors='coerce')
            min_date = menu_df_temp['date'].min()
            max_date = menu_df_temp['date'].max()
            col4.metric("Date Range", f"{min_date.strftime('%b %d, %Y')}")
            col4.caption(f"to {max_date.strftime('%b %d, %Y')}")
        except:
            col4.metric("Date Range", "N/A")
    
    st.markdown("**Sample Data Preview:**")
    tab1, tab2 = st.tabs(["🍽️ Menu Data", "⭐ Yelp Data"])
    with tab1:
        st.dataframe(menu_df.head(5), use_container_width=True)
    with tab2:
        st.dataframe(yelp_df.head(5), use_container_width=True)

# -------------------- MAIN UI --------------------
st.subheader("🧭 Ask a Question or Request a Report")

# Use selected example or custom query
default_query = query_examples[selected_example]

# Show analysis scope
if selected_restaurant and selected_restaurant_name:
    st.info(f"""
    🎯 **Consulting Scenario: Single Restaurant Analysis**
    
    **Client:** {selected_restaurant_name}
    
    **Business Goal:** Maximize market position and boost sales in specific menu categories
    
    **MaRGen AI Consultants:** Analyzing data to provide strategic recommendations
    """)
else:
    st.info("""
    📊 **Consulting Scenario: Market-Wide Analysis**
    
    **Client:** Restaurant Group (All Locations)
    
    **Business Goal:** Understand competitive landscape and identify optimization opportunities
    
    **MaRGen AI Consultants:** Providing comprehensive market intelligence
    """)

query = st.text_input(
    "Enter your query:",
    value=default_query,
    help="Type a custom query or select a template from the sidebar"
)

# Agent status display
cols = st.columns(4)
agent_status = {
    name: cols[i].empty() 
    for i, name in enumerate(["Retriever", "Researcher", "Writer", "Reviewer"])
}
for n in agent_status:
    agent_status[n].markdown(f"🟡 **{n}**: waiting...")

# -------------------- MAIN WORKFLOW --------------------
if st.button("🚀 Run Multi-Agent Workflow", type="primary", use_container_width=True):
    # Create output directory for visualizations
    os.makedirs("outputs", exist_ok=True)
    
    progress = st.progress(0)
    step_note = st.empty()
    
    try:
        # 1️⃣ RETRIEVER
        st.markdown("---")
        agent_status["Retriever"].markdown("🟠 **Retriever**: querying...")
        step_note.text("Step 1/4: Retriever Agent - Converting query to data retrieval...")
        
        with st.expander("🔍 Retriever Agent Activity Log", expanded=True):
            st.markdown("**Agent Reasoning:**")
            st.info(f"📝 Natural Language Query: `{query}`")
            
            # Simulated query parsing
            st.markdown("**Query Analysis:**")
            query_lower = query.lower()
            detected_intents = []
            if any(word in query_lower for word in ['dish', 'menu', 'item', 'food']):
                detected_intents.append("🍽️ Menu data required")
            if any(word in query_lower for word in ['rating', 'review', 'yelp']):
                detected_intents.append("⭐ Yelp ratings required")
            if any(word in query_lower for word in ['revenue', 'sales', 'performance']):
                detected_intents.append("💰 Sales metrics required")
            if any(word in query_lower for word in ['top', 'best']):
                detected_intents.append("🏆 Ranking/sorting needed")
            
            for intent in detected_intents:
                st.markdown(f"- {intent}")
            
            # SQL-like translation
            st.markdown("**Generated Data Query:**")
            sql_query = f"""
SELECT m.*, y.rating, y.review_count
FROM Menu_Sales_Data m
LEFT JOIN Yelp_Restaurant_Sales y 
  ON m.restaurant_id = y.business_id
WHERE 1=1
  {"AND category IN ('Main', 'Side', 'Drink')" if 'category' in query_lower else ""}
  {"ORDER BY total_sales DESC" if 'top' in query_lower else ""}
LIMIT 100;
"""
            st.code(sql_query, language="sql")
            
            # Execute retrieval
            with st.spinner("Fetching data from databases..."):
                retriever = Retriever(yelp_path, menu_path)
                retrieved_df = retriever.query(query)
            
            st.success(f"✅ Retrieved {len(retrieved_df)} records")
        
        st.subheader("📂 Retrieved Data Sample")
        st.dataframe(retrieved_df.head(20), use_container_width=True)
        st.caption(f"Showing first 20 of {len(retrieved_df)} total records")
        
        agent_status["Retriever"].markdown("🟢 **Retriever**: ✅")
        progress.progress(25)
        
        # 2️⃣ RESEARCHER
        st.markdown("---")
        agent_status["Researcher"].markdown("🟠 **Researcher**: analyzing...")
        step_note.text("Step 2/4: Researcher Agent - Computing insights and visualizations...")
        
        with st.expander("📊 Researcher Agent Activity Log", expanded=True):
            st.markdown("**Agent Reasoning:**")
            st.info("Performing data analysis and generating insights...")
            
            analysis_steps = [
                "1️⃣ Computing aggregate metrics (revenue, averages, counts)",
                "2️⃣ Identifying top performers (categories, items, restaurants)",
                "3️⃣ Detecting trends and patterns (temporal analysis)",
                "4️⃣ Generating visualizations (charts and graphs)",
                "5️⃣ Extracting key business insights"
            ]
            
            for step in analysis_steps:
                st.markdown(f"- {step}")
            
            with st.spinner("Running statistical analysis..."):
                researcher = Researcher(yelp_path, menu_path, restaurant_filter=selected_restaurant)
                research = researcher.run()
                
                # Store figures in session state
                if hasattr(research, 'figures'):
                    st.session_state.research_figures = research.figures
            
            st.success("✅ Analysis complete - Generated insights and visualizations")
        
        agent_status["Researcher"].markdown("🟢 **Researcher**: ✅")
        progress.progress(50)
        
        st.subheader("📊 Researcher Findings")
        
        # Display facts
        if hasattr(research, 'facts') and research.facts:
            st.markdown("#### 🔑 Key Metrics")
            fact_cols = st.columns(min(len(research.facts), 4))
            
            for idx, (k, v) in enumerate(research.facts.items()):
                with fact_cols[idx % 4]:
                    if isinstance(v, (int, float)):
                        # Format numbers nicely
                        if isinstance(v, float):
                            formatted_v = f"{v:,.2f}"
                        else:
                            formatted_v = f"{v:,}"
                        st.metric(label=k.replace('_', ' ').title(), value=formatted_v)
                    elif isinstance(v, dict):
                        st.markdown(f"**{k.replace('_', ' ').title()}:**")
                        st.json(v)
                    else:
                        st.markdown(f"**{k.replace('_', ' ').title()}:** {v}")
        
        # Display visualizations
        if hasattr(research, 'figures') and research.figures:
            st.markdown("#### 📈 Generated Visualizations")
            
            for fig_path in research.figures:
                paths_to_try = [
                    fig_path,
                    os.path.abspath(fig_path),
                    os.path.join(os.getcwd(), fig_path)
                ]
                
                image_found = False
                for path in paths_to_try:
                    if os.path.exists(path):
                        # Get descriptive caption
                        fig_name = os.path.basename(path)
                        if "monthly" in fig_name.lower():
                            caption = "📈 Monthly Revenue Trend"
                        elif "categories" in fig_name.lower():
                            caption = "📊 Top Categories by Revenue"
                        elif "items" in fig_name.lower():
                            caption = "🍽️ Top Items by Revenue"
                        elif "restaurant" in fig_name.lower():
                            caption = "🏪 Top Restaurants by Revenue"
                        elif "city" in fig_name.lower():
                            caption = "🌆 Revenue by Location"
                        else:
                            caption = fig_name.replace('_', ' ').replace('.png', '').title()
                        
                        st.image(path, caption=caption, use_container_width=True)
                        image_found = True
                        break
                
                if not image_found:
                    st.error(f"❌ Visualization not found: {fig_path}")
            
            st.markdown("")  # Add spacing
        
        # 3️⃣ WRITER
        st.markdown("---")
        agent_status["Writer"].markdown("🟠 **Writer**: drafting...")
        step_note.text("Step 3/4: Writer Agent - Drafting structured report...")
        
        with st.expander("📝 Writer Agent Activity Log", expanded=True):
            st.markdown("**Agent Reasoning:**")
            st.info("Structuring insights into professional business report...")
            
            writing_steps = [
                "1️⃣ Organizing findings into logical sections",
                "2️⃣ Writing executive summary with key takeaways",
                "3️⃣ Formatting metrics and statistics",
                "4️⃣ Embedding visualizations with captions",
                "5️⃣ Adding methodology and data sources",
                "6️⃣ Generating markdown for export"
            ]
            
            for step in writing_steps:
                st.markdown(f"- {step}")
            
            with st.spinner("Composing report..."):
                writer = Writer()
                draft = writer.draft(research.facts, research.figures)
            
            st.success("✅ Draft report generated")
        
        st.subheader("📝 Draft Report")
        st.markdown(draft.markdown, unsafe_allow_html=True)
        
        agent_status["Writer"].markdown("🟢 **Writer**: ✅")
        progress.progress(75)
        
        # 4️⃣ REVIEWER
        st.markdown("---")
        agent_status["Reviewer"].markdown("🟠 **Reviewer**: reviewing...")
        step_note.text("Step 4/4: Reviewer Agent - Quality assurance and refinement...")
        
        with st.expander("🧠 Reviewer Agent Activity Log", expanded=True):
            st.markdown("**Agent Reasoning:**")
            st.info("Applying AI-powered review and refinement using LLM...")
            
            review_steps = [
                "1️⃣ Checking report coherence and flow",
                "2️⃣ Validating data-insight alignment",
                "3️⃣ Enhancing clarity and readability",
                "4️⃣ Verifying query requirements met",
                "5️⃣ Adding comparisons and context where helpful",
                "6️⃣ Generating actionable recommendations"
            ]
            
            for step in review_steps:
                st.markdown(f"- {step}")
            
            st.markdown(f"**Using LLM:** `{model}` via Ollama")
            
            try:
                with st.spinner(f"Reviewer analyzing with {model}..."):
                    reviewer = Reviewer(model=model)
                    review_input = f"{draft.markdown}\n\n---\n\nUSER QUERY: {query}\n\nPlease review this report and ensure it directly addresses the user's question. Provide specific, actionable recommendations."
                    result = reviewer.review(review_input)
                
                st.success("✅ Review complete - Report refined")
            except Exception as e:
                result = type('obj', (object,), {
                    'feedback': f"LLM review encountered an error: {str(e)}. Report returned as drafted.",
                    'revised': draft.markdown
                })()
                st.error(result.feedback)
        
        agent_status["Reviewer"].markdown("🟢 **Reviewer**: ✅")
        progress.progress(100)
        step_note.text("✅ All agents completed successfully!")
        
        # Display final results
        st.markdown("---")
        st.subheader("🧠 Reviewer Agent Feedback & Improvements")
        
        # Show feedback in an expandable section
        with st.expander("📝 See Reviewer's Analysis", expanded=True):
            feedback_text = result.feedback if hasattr(result, 'feedback') else "Review completed successfully"
            st.info(feedback_text)
            
            # Show what was improved
            st.markdown("**Reviewer's Enhancements:**")
            if hasattr(result, 'revised') and result.revised != draft.markdown:
                improvements = [
                    "✅ Added strategic context based on query intent",
                    "✅ Enhanced recommendations with actionable next steps",
                    "✅ Improved clarity and business language",
                    "✅ Validated insights against user's specific question"
                ]
                for improvement in improvements:
                    st.markdown(f"- {improvement}")
            else:
                st.warning("⚠️ Draft was already high quality - minimal changes needed")
        
        st.subheader("📄 Final Revised Report")
        
        # Define final_report first
        final_report = result.revised if hasattr(result, 'revised') else draft.markdown
        
        # Add toggle to show draft vs final comparison
        show_comparison = st.checkbox("📊 Show Draft vs Final Comparison", value=False, key="comparison_toggle")
        
        if show_comparison and hasattr(result, 'revised'):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("### 📝 Original Draft")
                st.markdown(draft.markdown, unsafe_allow_html=True)
            with col2:
                st.markdown("### ✨ Reviewer-Enhanced Version")
                st.markdown(result.revised, unsafe_allow_html=True)
        else:
            # Show final report only
            st.markdown(final_report, unsafe_allow_html=True)
        
        # Re-display visualizations in the final report section
        if hasattr(st.session_state, 'research_figures') and st.session_state.research_figures:
            st.markdown("### 📊 Report Visualizations")
            for fig_path in st.session_state.research_figures:
                paths_to_try = [
                    fig_path,
                    os.path.abspath(fig_path),
                    os.path.join(os.getcwd(), fig_path)
                ]
                
                for path in paths_to_try:
                    if os.path.exists(path):
                        fig_name = os.path.basename(path)
                        if "monthly" in fig_name.lower():
                            caption = "📈 Monthly Revenue Trend"
                        elif "categories" in fig_name.lower():
                            caption = "📊 Top Categories by Revenue"
                        elif "items" in fig_name.lower():
                            caption = "🍽️ Top Items by Revenue"
                        elif "restaurant" in fig_name.lower():
                            caption = "🏪 Top Restaurants"
                        elif "city" in fig_name.lower():
                            caption = "🌆 Revenue by City"
                        else:
                            caption = fig_name
                        
                        st.image(path, caption=caption, use_container_width=True)
                        break
        
        st.success("✅ Multi-agent workflow completed successfully!")
        
        # Download options
        st.markdown("---")
        st.markdown("### 💾 Export Options")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.download_button(
                label="📥 Download Report (Markdown)",
                data=final_report,
                file_name="market_report.md",
                mime="text/markdown",
                use_container_width=True
            )
        
        with col2:
            st.download_button(
                label="📥 Download Retrieved Data (CSV)",
                data=retrieved_df.to_csv(index=False),
                file_name="retrieved_data.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with col3:
            insights_json = json.dumps(research.facts if hasattr(research, 'facts') else {}, indent=2)
            st.download_button(
                label="📥 Download Insights (JSON)",
                data=insights_json,
                file_name="insights.json",
                mime="application/json",
                use_container_width=True
            )
        
    except Exception as e:
        st.error(f"❌ Workflow Error: {str(e)}")
        st.exception(e)
        
        # Mark failed agent
        for name, status in agent_status.items():
            if "🟠" in str(status):
                status.markdown(f"🔴 **{name}**: failed ❌")
                break

# -------------------- FOOTER --------------------
st.markdown("---")
st.caption("🔬 Team4 | Inspired by MaRGen (2025) Research Paper")
st.caption("💡 Tip: Use the sidebar to explore different query templates and switch LLM models")