import json
import google.generativeai as genai

genai.configure(api_key="AIzaSyATQut1CZVFBGjPewlRMckCda4yhISMgmE")

model = genai.GenerativeModel("gemini-2.5-flash-preview-04-17")

with open("emails.json","r") as f:
    emails = json.load(f)

results = []

for email in emails:
    prompt = f"""
Email:
From:{email["from"]}
Subject:{email["subject"]}
Body:{email["body"]}

Please perform the following tasks:

1. Summarize the email in one sentence.
2. Suggest a short category (1 to 2 words maximum) that best represents the content of the email.

Return your answer in this JSON format:
{{"summary":"...","category","..."}}"""
    
    try:
        response = model.generate_content(prompt)
        content = response.text.strip()
        cleaned = content.replace("```json","").replace("```","").strip()

        parsed = json.loads(cleaned)

        email["summary"] = parsed["summary"]
        email["category"] = parsed["category"]

        results.append(email)

        print(f"✓ Processed: {email['subject']}")

    except Exception as e:
        print(f"⚠️ Error with: {email['subject']}")
        print(e)

with open("processed_emails.json","w") as f:
    json.dump(results,f,indent=2)

print("✅ All emails processed and saved to processed_emails.json") 
