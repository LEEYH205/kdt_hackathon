from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

# 1. 모델 및 토크나이저 로드
model_name = "skt/kogpt2-base-v2"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name, torch_dtype="auto", device_map="auto"
)

# 2. 프롬프트 구성 함수
def make_swot_prompt(biz_metrics):
    return f"""
비즈니스 지표:
- 생존율: {biz_metrics['survival']}
- 성장률: {biz_metrics['growth']}
- 경쟁 밀집도: {biz_metrics['competition']}

위 수치를 바탕으로, 강점 3가지와 약점 3가지를 한글로 자연스럽게 설명해 주세요.
"""

# 3. SWOT 생성 함수
def generate_swot(biz_metrics):
    prompt = make_swot_prompt(biz_metrics)
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    outputs = model.generate(**inputs, max_new_tokens=200)
    return tokenizer.decode(outputs[0], skip_special_tokens=True)

# 4. 예시 입력
biz_metrics = {
    "survival": 0.85,
    "growth": 0.12,
    "competition": 0.45
}

# 5. 실행
swot_text = generate_swot(biz_metrics)
print(swot_text)