import os
import requests
from flask import Flask, request, jsonify
from datetime import datetime, timedelta

app = Flask(__name__)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

users = {}
FREE_LIMIT = 15
FREE_DAYS = 7

def check_limit(user_id):
    now = datetime.now()

    if user_id not in users:
        users[user_id] = {
            "count": 0,
            "start_date": now
        }

    user = users[user_id]

    if now > user["start_date"] + timedelta(days=FREE_DAYS):
        return False, "체험 기간(7일)이 종료되었습니다."

    if user["count"] >= FREE_LIMIT:
        return False, "무료 생성 15회를 모두 사용하셨습니다."

    user["count"] += 1
    return True, None


@app.route("/generate-novel", methods=["POST"])
def generate_novel():
    try:
        data = request.json
        topic = data.get("topic")
        user_id = data.get("user_id")

        allowed, message = check_limit(user_id)
        if not allowed:
            return jsonify({"error": message})

        prompt = f"""
        당신은 뛰어난 문학가입니다.
        다음 주제로 감동적인 소설을 작성하세요.

        주제: {topic}
        """

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent?key={GEMINI_API_KEY}"

        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }]
        }

        response = requests.post(url, json=payload)
        result = response.json()

        # 🔥 핵심 안전장치
        if "candidates" not in result:
            return jsonify({
                "error": "Gemini API 오류",
                "detail": result
            })

        text = result["candidates"][0]["content"]["parts"][0]["text"]

        return jsonify({"result": text})

    except Exception as e:
        return jsonify({"error": str(e)})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
