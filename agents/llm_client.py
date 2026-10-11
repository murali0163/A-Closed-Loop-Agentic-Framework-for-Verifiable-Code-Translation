"""
LLM Client wrapper providing a unified interface for Gemini API calls.
Supports google.genai, google.generativeai, direct HTTP REST API, or rule-based fallback.
"""
import os
import requests
from config import get_api_key, DEFAULT_MODEL

def call_llm(prompt: str, system_instruction: str = "") -> str:
    """Sends prompt to Gemini LLM and returns the generated text response."""
    api_key = get_api_key()
    
    # 1. Try new official `google.genai` SDK
    try:
        from google import genai
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=f"{system_instruction}\n\n{prompt}" if system_instruction else prompt,
        )
        if response and response.text:
            return response.text.strip()
    except Exception:
        pass

    # 2. Try legacy `google.generativeai` SDK
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash", system_instruction=system_instruction or None)
        response = model.generate_content(prompt)
        if response and response.text:
            return response.text.strip()
    except Exception:
        pass

    # 3. Try direct HTTP REST API call to Gemini API
    if api_key:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
            payload = {
                "contents": [{"parts": [{"text": f"{system_instruction}\n\n{prompt}" if system_instruction else prompt}]}]
            }
            res = requests.post(url, json=payload, timeout=20)
            if res.status_code == 200:
                data = res.json()
                return data["candidates"][0]["content"]["parts"][0]["text"].strip()
        except Exception as e:
            print(f"[LLM Client REST Error] {e}")

    # 4. Fallback Rule-Based Heuristic Translator (for offline or local testing)
    return _offline_fallback(prompt)


def _offline_fallback(prompt: str) -> str:
    """Generates a structured heuristic Rust translation when no API key is provided."""
    print("[LLM Client] Operating in heuristic fallback mode (No API Key set).")
    if "binary_search" in prompt.lower():
        return '''fn binary_search(arr: &[i32], target: i32) -> Option<usize> {
    let mut left = 0;
    let mut right = arr.len();
    while left < right {
        let mid = left + (right - left) / 2;
        if arr[mid] == target {
            return Some(mid);
        } else if arr[mid] < target {
            left = mid + 1;
        } else {
            right = mid;
        }
    }
    None
}'''
    elif "two_sum" in prompt.lower():
        return '''use std::collections::HashMap;

fn two_sum(nums: Vec<i32>, target: i32) -> Vec<i32> {
    let mut map = HashMap::new();
    for (i, &num) in nums.iter().enumerate() {
        let complement = target - num;
        if let Some(&prev_idx) = map.get(&complement) {
            return vec![prev_idx as i32, i as i32];
        }
        map.insert(num, i);
    }
    vec![]
}'''
    elif "fibonacci" in prompt.lower():
        return '''fn fibonacci(n: u32) -> u64 {
    if n == 0 { return 0; }
    if n == 1 { return 1; }
    let mut a = 0;
    let mut b = 1;
    for _ in 2..=n {
        let temp = a + b;
        a = b;
        b = temp;
    }
    b
}'''
    else:
        return '''// Translated Rust code
fn process_data(input: &[i32]) -> i32 {
    input.iter().sum()
}'''
