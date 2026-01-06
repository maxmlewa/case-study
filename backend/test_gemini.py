from google import genai

client = genai.Client()  # reads GEMINI_API_KEY / GOOGLE_API_KEY

resp = client.models.generate_content(
    model="gemini-2.0-flash",
    contents="Say hello in one sentence."
)

print(resp.text)
