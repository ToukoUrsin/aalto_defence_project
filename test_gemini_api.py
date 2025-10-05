import google.generativeai as genai

# Configure API
API_KEY = "AIzaSyB2LVUXt2a9nMCpJwGJWen4_EECudv9u_c"
genai.configure(api_key=API_KEY)

# Create model
model = genai.GenerativeModel('gemini-2.5-flash')

# Test request
print("Testing Gemini API...")
response = model.generate_content('Say hello in exactly 5 words')

print("\n✅ SUCCESS! API is working!")
print(f"Response: {response.text}")
