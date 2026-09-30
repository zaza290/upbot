# 🎓 StudyBot AI & Review Analytics

An interactive, AI-powered educational analytics dashboard that transforms unstructured student course evaluations into real-time visual insights, executive sentiment summaries, and interactive natural-language Q&A.

![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Hugging Face](https://img.shields.io/badge/Hugging%20Face-FFD21E?style=for-the-badge&logo=huggingface&logoColor=black)
![Plotly](https://img.shields.io/badge/Plotly-3F4F75?style=for-the-badge&logo=plotly&logoColor=white)

---

## 🌟 Key Features

* **⚡ Real-Time Macro KPIs:** Dynamic tracking of overall average ratings, total feedback entries, and critical complaint counts (1–2 stars).
* **📊 Interactive Filtering & Data Engine:** Filter evaluations on the fly by rating ranges, course subjects, and metadata with instant chart updates.
* **🧠 LLM Executive Summaries:** One-click qualitative sentiment synthesis powered by Llama 3.2 via Hugging Face Inference API.
* **🏷️ Tagged Feedback Explorer:** Color-coded student feedback reader (Green = 5★ Praise, Amber = 3★ Neutral, Red = 1–2★ Critical Issues) for rapid triage.
* **💬 Ask StudyBot Assistant:** Context-aware chat assistant grounded directly in the live filtered dataset.
* **🎨 Adaptive Dual-Theme UI:** Custom styled interface supporting Light and Dark modes for optimal viewing environments.

---

## 🛠️ Tech Stack

* **Frontend / Framework:** [Streamlit](https://streamlit.io/) (Python) with custom CSS styling and state management.
* **Data Layer:** [Pandas](https://pandas.pydata.org/) & [Plotly Express](https://plotly.com/python/) for high-performance data manipulation and interactive charts.
* **AI Model Pipeline:** [Hugging Face Inference API](https://huggingface.co/docs/api-inference/index) running `meta-llama/Llama-3.2-3B-Instruct`.
* **Deployment:** Hosted live on [Streamlit Community Cloud](https://streamlit.app/).

---

## 📁 Repository Structure

```text
chatbot/
├── app.py                # Main Streamlit application entry point
├── frontend.py           # Custom UI layout components & CSS themes
├── config.toml           # Streamlit theme & configuration
├── requirements.txt      # Python dependencies
├── .env.example          # Example environment variables template
├── .gitignore            # Git ignore rules (protecting secrets & cache)
└── README.md             # Project documentation