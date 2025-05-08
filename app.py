import streamlit as st
import json
import pandas as pd
import google.generativeai as genai

# 🔑 Gemini API anahtarını buraya gir
genai.configure(api_key="YOUR_GEMINI_API_KEY")  # kendi anahtarını gir
model = genai.GenerativeModel("gemini-2.5-flash-preview-04-17")

# 📄 Sayfa ayarları
st.set_page_config(page_title="AI Email Summarizer", layout="wide")
st.title("📧 AI-Powered Email Summarizer & Categorizer")

# ✅ JSON formatını kontrol eden fonksiyon
def validate_email_data(data):
    return all(
        "from" in email and "subject" in email and "body" in email
        for email in data
    )

# 🧠 E-postaları işleyen fonksiyon
def process_email(email):
    prompt = f"""
Email:
From: {email['from']}
Subject: {email['subject']}
Body: {email['body']}

Please perform the following tasks:
1. Summarize the email in one sentence.
2. Suggest a short category (1 to 2 words maximum) that best represents the content of the email.

Return your answer in this JSON format:
{{"summary": "...", "category": "..."}}"""
    
    try:
        response = model.generate_content(prompt)
        content = response.text.strip()
        cleaned = content.replace("```json", "").replace("```", "").strip()
        result = json.loads(cleaned)
        return {
            "from": email["from"],
            "subject": email["subject"],
            "body": email["body"],
            "summary": result["summary"],
            "category": result["category"]
        }
    except Exception as e:
        return {
            "from": email["from"],
            "subject": email["subject"],
            "body": email["body"],
            "summary": f"Error: {str(e)}",
            "category": "Error"
        }

# 📤 Dosya yükleme
uploaded_file = st.file_uploader("Upload a JSON file containing emails", type="json")

if uploaded_file:
    try:
        raw_data = json.load(uploaded_file)

        if not validate_email_data(raw_data):
            st.error("❌ JSON format is invalid. Each item must include 'from', 'subject', and 'body'.")
        
        else: 
            st.info("✅ File successfully loaded. Processing emails with Gemini...")

            # 🔄 İlerleme çubuğu
            progress_bar = st.progress(0)
            total = len(raw_data)
            processed_emails = []

            for i, email in enumerate(raw_data):
                result = process_email(email)  # 🔧 düzeltildi
                processed_emails.append(result)
                progress_bar.progress((i + 1) / total)

            df = pd.DataFrame(processed_emails)

            # 🔍 Kategori filtresi
            categories = df["category"].unique().tolist()
            selected = st.multiselect("Filter by Category", options=categories, default=categories)

            filtered_df = df[df["category"].isin(selected)]

            # 🗂️ Tablo görünümü
            st.dataframe(filtered_df[["from", "subject", "category", "summary"]], use_container_width=True)

            # 📥 İndirilebilir dosyalar
            st.subheader("📥 Download Results")
            st.download_button("⬇️ Download as CSV", filtered_df.to_csv(index=False), "emails.csv", "text/csv")
            st.download_button("⬇️ Download as JSON", json.dumps(processed_emails, indent=2), "emails.json", "application/json")

    except Exception as e:
        st.error(f"❌ Failed to read JSON: {str(e)}")
else:
    st.info("📄 Please upload a `.json` file in this format:\n\n[\n  {{\"from\": \"...\", \"subject\": \"...\", \"body\": \"...\"}},\n  ...\n]")
