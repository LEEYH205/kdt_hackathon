import streamlit as st
import re
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

# 1. 모델 로드 (앱 시작 시 1회만)
@st.cache_resource
def load_model():
    model_name = "mistralai/Mistral-7B-Instruct-v0.2"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(
        model_name, torch_dtype="auto", device_map="auto"
    )
    return tokenizer, model

tokenizer, model = load_model()

# 2. 입력 폼
st.title("SWOT 분석 자동 생성기")
survival = st.number_input("생존율", min_value=0.0, max_value=1.0, value=0.85)
growth = st.number_input("성장률", min_value=0.0, max_value=1.0, value=0.12)
competition = st.number_input("경쟁 밀집도", min_value=0.0, max_value=1.0, value=0.45)

if st.button("SWOT 자동 생성"):
    # 3. 프롬프트 생성 (Mistral 스타일)
    prompt = f"""
[INST] 아래의 비즈니스 지표를 참고하여, 강점, 약점, 기회, 위협을 각각 3가지씩 한글로 자연스럽게 작성해 주세요. 각 항목은 반드시 입력된 수치와 관련된 내용이어야 합니다. 아래 형식으로 출력해 주세요:
비즈니스 지표:
- 생존율: {survival}
- 성장률: {growth}
- 경쟁 밀집도: {competition}

강점:
- 
[/INST]
"""
    # 4. LLM 호출
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    outputs = model.generate(**inputs, max_new_tokens=300, do_sample=True, temperature=0.7)
    llm_output = tokenizer.decode(outputs[0], skip_special_tokens=True)

    # LLM 원본 출력 항상 표시
    st.text_area("LLM 원본 출력", llm_output, height=300)

    # 5. SWOT 파싱 (중복/빈 항목 제거, 최대 5개)
    def parse_swot(text):
        swot = {}
        for section in ["강점", "약점", "기회", "위협"]:
            pattern = rf"{section}:\n((?:- .+\n)+)"
            match = re.search(pattern, text)
            if match:
                items = [line[2:] for line in match.group(1).strip().split('\n')]
                # 중복/빈 항목 제거, 최대 5개만
                swot[section] = [i for i in items if i and i != section][:5]
            else:
                swot[section] = []
        return swot

    # LLM 출력이 비어있으면 안내
    if not llm_output.strip():
        st.error("LLM 출력이 비어 있습니다. 모델이 아직 로딩 중이거나, 메모리 부족 등으로 실행이 실패했을 수 있습니다. 터미널 로그를 확인해 주세요.")
    else:
        swot = parse_swot(llm_output)
        # SWOT 4개 항목이 모두 비어있으면 파싱 실패 안내
        if all(len(swot[section]) == 0 for section in ["강점", "약점", "기회", "위협"]):
            st.warning("SWOT 항목을 추출하지 못했습니다. 아래 LLM 원본 출력을 참고해 프롬프트나 파싱 로직을 개선해 주세요.")
            st.write("LLM 원본 출력:")
            st.write(llm_output)
        else:
            # 6. 시각화
            cols = st.columns(2)
            with cols[0]:
                st.markdown("### 🟦 강점")
                for s in swot["강점"]:
                    st.markdown(f"- {s}")
            with cols[1]:
                st.markdown("### 🟥 약점")
                for w in swot["약점"]:
                    st.markdown(f"- {w}")
            cols2 = st.columns(2)
            with cols2[0]:
                st.markdown("### 🟩 기회")
                for o in swot["기회"]:
                    st.markdown(f"- {o}")
            with cols2[1]:
                st.markdown("### 🟧 위협")
                for t in swot["위협"]:
                    st.markdown(f"- {t}")