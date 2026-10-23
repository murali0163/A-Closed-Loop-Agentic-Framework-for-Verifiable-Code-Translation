"""Gemini LLM client with SDK/HTTP support and an offline fallback."""
import json
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from backend.config import DEFAULT_MODEL, get_api_key


def call_llm(prompt: str, system_instruction: str = "") -> str:
    """Call Gemini when configured; otherwise return a deterministic local fallback."""
    api_key = get_api_key()
    contents = f"{system_instruction}\n\n{prompt}" if system_instruction else prompt

    if api_key:
        try:
            from google import genai
            response = genai.Client(api_key=api_key).models.generate_content(
                model=DEFAULT_MODEL, contents=contents
            )
            if response and response.text:
                return response.text.strip()
        except Exception:
            pass
        try:
            url = (
                f"https://generativelanguage.googleapis.com/v1beta/models/"
                f"{DEFAULT_MODEL}:generateContent?{urlencode({'key': api_key})}"
            )
            request = Request(
                url,
                data=json.dumps({"contents": [{"parts": [{"text": contents}]}]}).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urlopen(request, timeout=20) as response:
                data = json.loads(response.read().decode("utf-8"))
            return data["candidates"][0]["content"]["parts"][0]["text"].strip()
        except (HTTPError, URLError, TimeoutError, KeyError, ValueError) as exc:
            print(f"[LLM Client] API unavailable; using offline fallback: {exc}")

    return _offline_fallback(prompt)


def _offline_fallback(prompt: str) -> str:
    """Provide simple example translations for local development without API access."""
    print("[LLM Client] Operating in heuristic fallback mode (no API key set).")
    source = prompt.lower()
    if "binary_search" in source:
        return '''fn binary_search(arr: &[i32], target: i32) -> Option<usize> {
    let mut left = 0;
    let mut right = arr.len();
    while left < right {
        let mid = left + (right - left) / 2;
        if arr[mid] == target { return Some(mid); }
        if arr[mid] < target { left = mid + 1; } else { right = mid; }
    }
    None
}'''
    if "two_sum" in source:
        return '''use std::collections::HashMap;
fn two_sum(nums: Vec<i32>, target: i32) -> Vec<i32> {
    let mut map = HashMap::new();
    for (i, &num) in nums.iter().enumerate() {
        let complement = target - num;
        if let Some(&prev_idx) = map.get(&complement) { return vec![prev_idx as i32, i as i32]; }
        map.insert(num, i);
    }
    vec![]
}'''
    if "fibonacci" in source:
        return '''fn fibonacci(n: u32) -> u64 {
    if n == 0 { return 0; }
    if n == 1 { return 1; }
    let (mut a, mut b) = (0, 1);
    for _ in 2..=n { (a, b) = (b, a + b); }
    b
}'''
    return '''fn add(a: i32, b: i32) -> i32 {
    a + b
}'''
