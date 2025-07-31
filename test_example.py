import json
import csv
import requests
import os
import time

TOGETHER_API_KEY = "51fbbac4573aaa3239b7ee5a4f97416c923882bad2b1de029a142bf337e29899"  # 🔑 Replace with your actual key

JUDGE_SYSTEM_PROMPT = """
You are a strict programming evaluator. Score the student's answer on a scale of 1 to 5 based on correctness, clarity, and completeness.
Respond with ONLY a number between 1 and 5. Do not explain.
"""

def call_model(prompt):
    headers = {
        "Authorization": f"Bearer {TOGETHER_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "mistralai/Mixtral-8x7B-Instruct-v0.1",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 300,
        "temperature": 0.7
    }

    try:
        response = requests.post("https://api.together.xyz/v1/chat/completions", headers=headers, json=data)
        response.raise_for_status()
        raw = response.json()
        return raw["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print("❌ Error:", e)
        return "ERROR"

def auto_score(test_input, expected, actual):
    score_prompt = (
        f"{JUDGE_SYSTEM_PROMPT}\n\n"
        f"Question: {test_input}\n"
        f"Expected Answer: {expected}\n"
        f"Student Answer: {actual}"
    )
    score = call_model(score_prompt)

    try:
        score = int(score.strip())
        return max(1, min(score, 5))  # clamp between 1–5
    except:
        return 1  # fallback score

# === Load Test Cases ===
with open("test_cases.json", "r") as f:
    test_cases = json.load(f)

results = []

# === Run Tests ===
for case in test_cases:
    prompt = case["input"]
    expected = case["ideal"]

    print(f"\n=== Testing: {prompt} ===")
    actual = call_model(prompt)
    score = auto_score(prompt, expected, actual)

    results.append({
        "input": prompt,
        "expected": expected,
        "actual": actual,
        "score": score
    })

    time.sleep(1)  # be kind to the API

# === Save Results ===
with open("results.csv", "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=["input", "expected", "actual", "score"])
    writer.writeheader()
    writer.writerows(results)

print("✅ Results saved to results.csv")
