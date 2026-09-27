import os
import streamlit as st
import pandas as pd
import plotly.express as px
from huggingface_hub import InferenceClient
from dotenv import load_dotenv

# Load environment variables (supports both local .env and Streamlit Cloud secrets)
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
    page_title="StudyBot AI & Review Analytics",
    page_icon="🤖",
    layout="wide"
)

# Custom CSS Styling
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(135deg, #e0f2fe, #f8fafc, #dbeafe);
    }
    [data-testid="stChatMessage"] {
        background: transparent;
        border: none;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Header Section
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    header_left, header_right = st.columns([1, 4])
    with header_left:
        st.markdown(
            '<div style="width: 60px; height: 60px; background: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 30px; margin: 0 auto;">🤖</div>',
            unsafe_allow_html=True
        )
    with header_right:
        st.markdown(
            '<h1 style="color: #1e40af; margin-bottom: 2px; font-size: 26px;">StudyBot AI</h1>'
            '<p style="color: #64748b; margin: 0; font-size: 14px;">AI Study & Dataset Assistant</p>',
            unsafe_allow_html=True
        )
    st.markdown("<hr style='margin: 10px 0 20px 0; border-color: #93c5fd;'>", unsafe_allow_html=True)

# ---------------------------------------------------------
# STEPS 2 & 3: Load and Clean Dataset (Pandas)
# ---------------------------------------------------------
@st.cache_data
def load_dataset():
    try:
        df = pd.read_csv("data/reviews.csv")
        # Basic cleaning: handle missing values
        df.fillna("N/A", inplace=True)
        return df
    except Exception as e:
        st.error(f"Error loading dataset from 'data/reviews.csv': {e}")
        return pd.DataFrame()

df = load_dataset()

if df.empty:
    st.warning("Please make sure 'data/reviews.csv' contains valid CSV data.")
    st.stop()

# ---------------------------------------------------------
# STEP 5 & 9: Streamlit Filters & Dashboard Layout
# ---------------------------------------------------------
st.sidebar.header("🔍 Dataset Filters")

# Dynamically pick categorical columns for filtering
categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
if categorical_cols:
    filter_col = st.sidebar.selectbox("Filter by Column:", categorical_cols)
    selected_values = st.sidebar.multiselect(
        f"Select {filter_col}:", 
        options=df[filter_col].unique(), 
        default=df[filter_col].unique()
    )
    filtered_df = df[df[filter_col].isin(selected_values)]
else:
    filtered_df = df

st.subheader("📊 Dataset Overview")
st.dataframe(filtered_df, use_container_width=True)

# ---------------------------------------------------------
# STEPS 4 & 6: GenAI Analysis & Visualizations (Plotly)
# ---------------------------------------------------------
st.divider()
vis_col, ai_col = st.columns([1, 1])

with vis_col:
    st.subheader("📈 Visual Analytics")
    numeric_cols = filtered_df.select_dtypes(include=['number']).columns.tolist()
    
    if numeric_cols and categorical_cols:
        x_axis = st.selectbox("Chart X-Axis:", categorical_cols, index=0)
        y_axis = st.selectbox("Chart Y-Axis:", numeric_cols, index=0)
        
        fig = px.bar(
            filtered_df, 
            x=x_axis, 
            y=y_axis, 
            color=x_axis, 
            title=f"{y_axis} by {x_axis}",
            template="plotly_white"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Chart requires both numeric and text/category columns in the dataset.")

with ai_col:
    st.subheader("🤖 GenAI Dataset Insights")
    st.write("Click below to run automated AI sentiment and key-trend analysis on the current dataset view.")
    
    if st.button("Run AI Analysis"):
        with st.spinner("Analyzing dataset with Hugging Face AI..."):
            try:
                sample_text = filtered_df.head(20).to_string()
                analysis_prompt = [
                    {"role": "system", "content": "You are a data analyst. Analyze data trends and sentiment clearly."},
                    {"role": "user", "content": f"Summarize key insights, overall sentiment, and trends from this dataset sample:\n\n{sample_text}"}
                ]
                
                response = client.chat.completions.create(
                    model=MODEL,
                    messages=analysis_prompt,
                    max_tokens=400,
                    temperature=0.5
                )
                st.success("Analysis Complete!")
                st.markdown(response.choices[0].message.content)
            except Exception as e:
                st.error(f"Failed to generate analysis: {e}")

# ---------------------------------------------------------
# STEP 9: Dataset-Aware AI Chatbot
# ---------------------------------------------------------
st.divider()
st.subheader("💬 Ask StudyBot About This Data")

# Build system prompt grounding the bot with dataset context
dataset_context = f"Dataset Summary:\nRows: {len(filtered_df)}\nColumns: {list(filtered_df.columns)}\nSample Data:\n{filtered_df.head(5).to_string()}"

SYSTEM_PROMPT = f"""You are StudyBot, a helpful AI study assistant.
Answer user questions clearly and accurately using simple language.
You have access to the following dataset context:

{dataset_context}

If asked about the dataset or reviews, answer using the context provided above.
"""

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Hello! 👋 I'm StudyBot. Ask me anything about your studies or the loaded dataset!"
        }
    ]

for msg in st.session_state.messages:
    avatar = "👤" if msg["role"] == "user" else "🤖"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

prompt = st.chat_input("Ask StudyBot something...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="🤖"):
        message_placeholder = st.empty()
        full_response = ""
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