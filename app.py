from flask import Flask, request
import requests

app = Flask(__name__)

# আপনার সিক্রেট কী (লিংকে ব্যবহারের জন্য)
SECRET_KEY = "YASIN-BHAI"

# আপনার দেওয়া দুটি Mistral API Key
MISTRAL_API_KEYS = [
    "bGii560p6iI48Fxc0HzC15MwAMTDKslZ",
    "fouNackNRth0YUUBXv8aM4hiSbKbuKBS"
]

# মডেল লিস্ট (একটার পর একটা ট্রাই করবে যাতে লিমিট না লাগে)
MISTRAL_MODELS = [
    "open-mistral-7b",      # সবচেয়ে ফাস্ট এবং ফ্রি
    "open-mixtral-8x7b",    # বড় এবং স্মার্ট
    "mistral-small-latest", # স্মার্ট এবং ব্যালেন্সড
    "mistral-tiny"          # ব্যাকআপ
]

MISTRAL_URL = "https://api.mistral.ai/v1/chat/completions"

# এখানে AI-এর সিস্টেম প্রম্পট বা পরিচয় সেট করা হলো
SYSTEM_PROMPT = (
    "You are 'Free Fire AI Bot', an advanced AI assistant. "
    "If the user asks your name in Bengali, you must reply in Bengali saying: 'আমার নাম Free Fire AI Bot।' "
    "If the user asks your name in English, you must reply in English saying: 'My name is Free Fire AI Bot.' "
    "Always reply in the same language the user uses to ask the question. Keep your answers beautiful, helpful, and well-formatted."
)

@app.route('/ask', methods=['GET'])
def ask():
    # ১. URL থেকে key এবং message নেওয়া
    user_key = request.args.get('key')
    user_message = request.args.get('message')

    # ২. Key চেক করা
    if user_key != SECRET_KEY:
        return "Unauthorized! Invalid Key.", 401

    if not user_message:
        return "Message is required!", 400

    # ৩. লুপ তৈরি করা: প্রথমে সব মডেল চেক করবে, প্রতিটা মডেলের জন্য সব Key চেক করবে
    for model in MISTRAL_MODELS:
        for api_key in MISTRAL_API_KEYS:
            payload = {
                "model": model,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT}, # এখানে সিস্টেম প্রম্পট যুক্ত হলো
                    {"role": "user", "content": user_message}
                ],
                "temperature": 0.7,
                "max_tokens": 500
            }
            
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            try:
                response = requests.post(MISTRAL_URL, headers=headers, json=payload, timeout=20)
                
                if response.status_code == 200:
                    data = response.json()
                    answer = data.get('choices', [{}])[0].get('message', {}).get('content', 'No content')
                    return answer.strip(), 200
                else:
                    # যদি রেট লিমিট (429) বা অন্য কোনো এরর আসে, তবে পরের Key বা মডেলে চলে যাবে
                    print(f"Model {model} with Key ending in ...{api_key[-4:]} failed. Status: {response.status_code}")
                    continue

            except Exception as e:
                print(f"Exception with Model {model} and Key ...{api_key[-4:]}: {str(e)}")
                continue

    # যদি সব মডেল এবং সব Key ফেইল করে (খুব কম ক্ষেত্রে হয়)
    return "System Error: All AI models and API keys failed or rate limited. Please try again later.", 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)