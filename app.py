import os
import streamlit as st
import pandas as pd
import plotly.express as px
from huggingface_hub import InferenceClient
from dotenv import load_dotenv

# Front-end layer (themes, CSS loader, HTML components)
from frontend import (
    get_theme,
    inject_css,
    render_header,
    render_kpis,
    render_comment_card,
)

# Load environment variables
load_dotenv()
HF_TOKEN = os.getenv("HF_TOKEN") or st.secrets.get("HF_TOKEN", "")
MODEL = os.getenv("HF_MODEL", "meta-llama/Llama-3.2-3B-Instruct")

if not HF_TOKEN:
    st.error("⚠️ HF_TOKEN is missing. Please set it in your .env file or Streamlit Secrets.")
    st.stop()

# Initialize Hugging Face Client
client = InferenceClient(api_key=HF_TOKEN)

# Page Configuration
st.set_page_config(
    page_title="StudyBot AI | Enterprise Review Analytics",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# THEME (single professional light theme, no toggle)
# ---------------------------------------------------------
st.session_state.theme = "Light Mode"

# Active theme colors + stylesheet (see frontend.py and static/style.css)
t = get_theme(st.session_state.theme)
inject_css(t)

# ---------------------------------------------------------
# EXECUTIVE HEADER
# ---------------------------------------------------------
render_header()

# ---------------------------------------------------------
# LOAD & FILTER DATASET
# ---------------------------------------------------------
st.sidebar.markdown("### 🔍 Dataset Controls")

uploaded_file = st.sidebar.file_uploader("Upload CSV Dataset", type=["csv"])

@st.cache_data
def load_default_dataset():
    try:
        df = pd.read_csv("data/reviews.csv")
        df.fillna("N/A", inplace=True)
        return df
    except Exception as e:
        st.error(f"Error loading default dataset: {e}")
        return pd.DataFrame()

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        df.fillna("N/A", inplace=True)
    except Exception as e:
        st.sidebar.error(f"Error reading uploaded CSV: {e}")
        df = load_default_dataset()
else:
    df = load_default_dataset()

if df.empty:
    st.warning("Please upload a CSV dataset or ensure 'data/reviews.csv' exists.")
    st.stop()

# Rating Filter Slider
if "rating" in df.columns and pd.api.types.is_numeric_dtype(df["rating"]):
    min_rating = float(df["rating"].min())
    max_rating = float(df["rating"].max())
    
    if min_rating < max_rating:
        selected_rating_range = st.sidebar.slider(
            "Filter by Rating Range:",
            min_value=min_rating,
            max_value=max_rating,
            value=(min_rating, max_rating),
            step=0.5
        )
        filtered_df = df[(df["rating"] >= selected_rating_range[0]) & (df["rating"] <= selected_rating_range[1])]
    else:
        filtered_df = df.copy()
else:
    filtered_df = df.copy()

# Column Filters
all_categorical = filtered_df.select_dtypes(include=['object', 'category']).columns.tolist()
categorical_cols = [col for col in all_categorical if col.lower() != 'comment']

filter_col = None
selected_values = []

if categorical_cols:
    filter_col = st.sidebar.selectbox("Filter by Column:", categorical_cols)
    selected_values = st.sidebar.multiselect(
        f"Select {filter_col.capitalize()}:", 
        options=df[filter_col].unique(), 
        default=df[filter_col].unique()
    )
    filtered_df = filtered_df[filtered_df[filter_col].isin(selected_values)]

# ---------------------------------------------------------
# EXECUTIVE KPI METRICS
# ---------------------------------------------------------
total_reviews = len(filtered_df)
avg_rating_val = round(filtered_df['rating'].mean(), 2) if 'rating' in filtered_df.columns and not filtered_df.empty else "N/A"
low_ratings_count = len(filtered_df[filtered_df['rating'] <= 2]) if 'rating' in filtered_df.columns else 0

render_kpis(total_reviews, avg_rating_val, low_ratings_count)

# ---------------------------------------------------------
# RAW DATASET OVERVIEW TABLE
# ---------------------------------------------------------
with st.expander("📋 View Raw Dataset Overview", expanded=False):
    st.dataframe(filtered_df, height=220, use_container_width=True)

# ---------------------------------------------------------
# VISUAL ANALYTICS & GENAI INSIGHTS
# ---------------------------------------------------------
vis_col, ai_col = st.columns([1, 1], gap="medium")

chart_metric = "Average Rating"
x_axis = categorical_cols[0] if categorical_cols else None
chart_summary_dict = {}

with vis_col:
    st.markdown("### 📈 Visual Analytics")
    
    chart_m_col, chart_x_col = st.columns([1, 1])
    with chart_m_col:
        chart_metric = st.selectbox("Chart Metric:", options=["Average Rating", "Review Count"], index=0)
    with chart_x_col:
        x_axis = st.selectbox("Chart Grouping (X-Axis):", options=categorical_cols, index=0 if categorical_cols else None)
    
    if x_axis:
        if chart_metric == "Average Rating" and "rating" in filtered_df.columns:
            chart_data = filtered_df.groupby(x_axis, as_index=False)["rating"].mean()
            chart_data["rating"] = chart_data["rating"].round(2)
            chart_summary_dict = dict(zip(chart_data[x_axis], chart_data["rating"]))
            
            fig = px.bar(
                chart_data, 
                x=x_axis, 
                y="rating", 
                color=x_axis, 
                title=f"Average Rating by {x_axis.capitalize()}",
                labels={"rating": "Avg Rating"},
                template=t["plotly_template"],
                color_discrete_sequence=t["chart_colors"]
            )
            fig.update_layout(
                yaxis_range=[0, 5],
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color=t["chart_text"]),
                title=dict(font=dict(color=t["chart_text"])),
                xaxis=dict(title=dict(font=dict(color=t["chart_text"])), tickfont=dict(color=t["chart_text"])),
                yaxis=dict(title=dict(font=dict(color=t["chart_text"])), tickfont=dict(color=t["chart_text"]), gridcolor=t["grid"]),
                legend=dict(font=dict(color=t["chart_text"])),
                margin=dict(l=20, r=20, t=40, b=20)
            )
        else:
            chart_data = filtered_df.groupby(x_axis, as_index=False).size().rename(columns={"size": "count"})
            chart_summary_dict = dict(zip(chart_data[x_axis], chart_data["count"]))
            
            fig = px.bar(
                chart_data, 
                x=x_axis, 
                y="count", 
                color=x_axis, 
                title=f"Total Reviews by {x_axis.capitalize()}",
                labels={"count": "Number of Reviews"},
                template=t["plotly_template"],
                color_discrete_sequence=t["chart_colors"]
            )
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color=t["chart_text"]),
                title=dict(font=dict(color=t["chart_text"])),
                xaxis=dict(title=dict(font=dict(color=t["chart_text"])), tickfont=dict(color=t["chart_text"])),
                yaxis=dict(title=dict(font=dict(color=t["chart_text"])), tickfont=dict(color=t["chart_text"]), gridcolor=t["grid"]),
                legend=dict(font=dict(color=t["chart_text"])),
                margin=dict(l=20, r=20, t=40, b=20)
            )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Chart requires categorical columns (Subject, Category) in the dataset.")

with ai_col:
    st.markdown("### 🤖 GenAI Executive Summary")
    st.caption("Generate automated AI sentiment and key trend summaries based on active filters.")
    
    if st.button("Run Executive AI Analysis", use_container_width=True):
        with st.spinner("Analyzing dataset trends with AI..."):
            try:
                sample_cols = [c for c in ['subject', 'category', 'rating', 'comment'] if c in filtered_df.columns]
                reviews_sample = filtered_df[sample_cols].head(25).to_dict(orient='records')
                
                analysis_prompt = [
                    {"role": "system", "content": "You are an executive educational data analyst. Provide concise, bulleted key findings and actionable insights."},
                    {"role": "user", "content": f"Analyze these student course reviews:\n1. Top Strengths\n2. Key Areas for Improvement\n3. Executive Summary\n\nData:\n{reviews_sample}"}
                ]
                
                response = client.chat.completions.create(
                    model=MODEL,
                    messages=analysis_prompt,
                    max_tokens=400,
                    temperature=0.5
                )
                st.success("Analysis Ready")
                st.markdown(f"<div style='background:{t['card_bg']}; padding:16px; border-radius:12px; border:1px solid {t['card_border']}; color:{t['text_main']};'>{response.choices[0].message.content}</div>", unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Failed to generate analysis: {e}")

    if {"subject", "category", "rating"}.issubset(filtered_df.columns):
        st.markdown("##### Category Breakdown Snapshot")
        snapshot = filtered_df.groupby(["subject", "category"]).agg(
            Avg_Rating=("rating", "mean"),
            Reviews_Count=("rating", "count")
        ).reset_index()
        snapshot["Avg_Rating"] = snapshot["Avg_Rating"].round(1)
        st.dataframe(snapshot, use_container_width=True, height=180)

st.divider()

# ---------------------------------------------------------
# STUDENT FEEDBACK EXPLORER
# ---------------------------------------------------------
if "comment" in filtered_df.columns:
    st.markdown("### 🗣️ Student Feedback Explorer")
    st.caption("Filter and review direct qualitative comments from students.")
    
    ctrl_col1, ctrl_col2, ctrl_col3 = st.columns([2, 1, 1])
    
    with ctrl_col1:
        search_term = st.text_input("Search keyword:", "", placeholder="e.g. 'lab', 'syllabus', 'exam'...")
    
    with ctrl_col2:
        rating_filter = st.selectbox(
            "Filter Rating:",
            options=["All Ratings", "5 Stars Only", "4 Stars Only", "3 Stars Only", "1-2 Stars (Complaints)"]
        )
        
    with ctrl_col3:
        sort_order = st.selectbox(
            "Sort Order:",
            options=["Highest Rating First", "Lowest Rating First"]
        )

    display_df = filtered_df.copy()
    
    if search_term:
        display_df = display_df[display_df["comment"].str.contains(search_term, case=False, na=False)]
        
    if "rating" in display_df.columns:
        if rating_filter == "5 Stars Only":
            display_df = display_df[display_df["rating"] == 5]
        elif rating_filter == "4 Stars Only":
            display_df = display_df[display_df["rating"] == 4]
        elif rating_filter == "3 Stars Only":
            display_df = display_df[display_df["rating"] == 3]
        elif rating_filter == "1-2 Stars (Complaints)":
            display_df = display_df[display_df["rating"] <= 2]

        if sort_order == "Highest Rating First":
            display_df = display_df.sort_values(by="rating", ascending=False)
        else:
            display_df = display_df.sort_values(by="rating", ascending=True)

    total_results = len(display_df)
    st.caption(f"Showing top {min(total_results, 10)} of {total_results} matching feedback items")
    
    if display_df.empty:
        st.info("No student comments match the active filters.")
    else:
        for idx, row in display_df.head(10).iterrows():
            subj = row.get('subject', 'N/A')
            cat = row.get('category', 'N/A')
            rat = row.get('rating', 'N/A')
            cmnt = row.get('comment', 'No comment provided')
            
            render_comment_card(subj, cat, rat, cmnt)

st.divider()

# ---------------------------------------------------------
# DATASET & APP-AWARE CHATBOT
# ---------------------------------------------------------
st.markdown("### 💬 Ask StudyBot Assistant")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Hello! I'm StudyBot. Ask me anything about course trends, ratings, or dataset insights."
        }
    ]

for msg in st.session_state.messages:
    avatar = "👤" if msg["role"] == "user" else "🤖"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

prompt = st.chat_input("Ask StudyBot a question about this data...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="🤖"):
        message_placeholder = st.empty()
        full_response = ""
        
        active_dataset_name = uploaded_file.name if uploaded_file else "data/reviews.csv"
        sample_rows = filtered_df[['subject', 'category', 'rating', 'comment']].head(20).to_dict(orient='records') if {'subject', 'category', 'rating', 'comment'}.issubset(filtered_df.columns) else filtered_df.head(10).to_dict(orient='records')

        SYSTEM_PROMPT = f"""You are StudyBot, an embedded AI analyst inside the 'StudyBot AI & Review Analytics' application.

LIVE DASHBOARD CONTEXT:
- Active File: '{active_dataset_name}'
- Total Dataset Rows: {len(df)} | Currently Filtered View Rows: {len(filtered_df)}
- Active Filter Column: '{filter_col}' with selected values: {selected_values}
- Overall Average Rating in current view: {avg_rating_val} / 5.0
- DISPLAYED BAR CHART METRIC: '{chart_metric}' grouped by '{x_axis}'.
- CHART VALUES DISPLAYED: {chart_summary_dict}

CURRENT FILTERED DATASET SAMPLE:
{sample_rows}

RESPONSE INSTRUCTIONS:
1. Provide professional, direct, and factual answers based on the context above.
2. If asked about charts or data, reference the exact chart data values provided.
"""

        try:
            messages_for_api = [{"role": "system", "content": SYSTEM_PROMPT}]
            for msg in st.session_state.messages:
                messages_for_api.append({"role": msg["role"], "content": msg["content"]})

            completion = client.chat.completions.create(
                model=MODEL,
                messages=messages_for_api,
                max_tokens=512,
                temperature=0.7,
                stream=True
            )

            for chunk in completion:
                if chunk.choices and len(chunk.choices) > 0:
                    delta = chunk.choices[0].delta
                    if delta.content is not None:
                        full_response += delta.content
                        message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
        except Exception as e:
            error_msg = f"Error: AI request failed: {str(e)}"
            message_placeholder.error(error_msg)
            st.session_state.messages.append({"role": "assistant", "content": error_msg})