# ResTech.io 🎯

Welcome to **ResTech.io** — an all-in-one AI-powered Career Companion! ✨  
This Streamlit app helps you **build**, **optimize**, and **apply** for jobs using the latest GenAI technologies! 💼🤖

---

## 📂 Project Structure

- **`generators.py`** 📝  
  Functions to **generate resumes** and **cover letters** automatically based on your profile and job description.

- **`data/`** 📊  
  Contains datasets for **fine-tuning** the resume scoring model.

- **`guardrails.py`** 🚧  
  Input validation rules to ensure clean and consistent data entry.

- **`training/`** 📚  
  Contains **train** and **validation** sets used for model fine-tuning.

- **`job_apply.py`** 🌐  
  Automates **real-time job applications** using **Selenium** on the **Handshake App** —  
  🚀 Scrapes live job descriptions, generates a **custom resume + cover letter** on the fly, and applies!

- **`ai_agents.py`** 🧠  
  Houses four powerful AI agents:
  - **Resume Rater Agent** 🏆
  - **ResTech Agent** 🛠️
  - **Cover Letter Agent** 💌
  - **Resume Tailor Agent** ✂️  
  These agents collaborate to enhance your documents and boost your chances!

- **`app.py`** 🧠  
  Main Streamlit App consisting of all the features  

---

## 🖥️ App Features

🌟 **Upload Section**:  
- Upload your **existing resume** and/or a **job description**.

🌟 **Resume & Cover Letter Generators**:  
- Auto-generate **custom resumes** and **cover letters** directly from your inputs!

🌟 **Job Application Automation**:  
- Input your details once and **apply to real jobs** across the Handshake platform instantly.

🌟 **Resume Evaluation Tools**:  
Four powerful features:
- **General Summary** 📃
- **Skill Improvement Suggestions** 🚀
- **Interview Prep Assistance** 🎤
- **Bar Graph Visualization** 📈 for resume scoring!

🌟 **Profile Filling**:
- Fill out your personal and professional details directly through the sidebar.

---

## 🚀 Tech Stack

- **Streamlit** - UI Framework
- **Selenium** - Web Scraping and Automation
- **OpenAI / Custom LLM Agents** - AI Logic
- **Python** - Core backend
- **Pandas, Numpy, Matplotlib** - Data handling and visualization

---

## 🎯 How It Works

1. **Fill in your profile** 📋 or **upload existing documents** 📄
2. **Generate resume and cover letters** or **get real-time evaluation** 🛠️
3. **Scrape live job postings** and **apply instantly** 🔥
4. **Use AI suggestions** to **improve and tailor your applications** 💡
5. **Visualize resume quality** with charts 📊

---

## 🌟 Why ResTech.io?

✅ Save time writing resumes and cover letters  
✅ Tailor documents **for every job**  
✅ Apply **faster** and **smarter**  
✅ Get **interview-ready** with AI-driven prep  
✅ Evaluate and **boost your resume score** instantly

---

## 🛠️ Setup Instructions

```bash
# Clone the repository
git clone https://github.com/yourusername/ResTech.io.git

# Navigate to the project folder
cd ResTech.io

# Install required libraries
pip install -r requirements.txt

# Add your school email (like @edu) , password and OPENAI Api Key in the .env file

# Run the Streamlit app
streamlit run web_page.py
