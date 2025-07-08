# SWOT 자동 생성기 (Streamlit + 최신 LLM)

이 프로젝트는 최신 오픈소스 LLM(Mistral-7B-Instruct-v0.2)을 활용하여, 비즈니스 주요 지표(생존율, 성장률, 경쟁 밀집도 등)를 입력하면 자동으로 SWOT(강점, 약점, 기회, 위협) 분석을 생성하고, Streamlit 웹앱에서 시각화해주는 도구입니다.

---

## 주요 기능
- **지표 입력 폼**: 생존율, 성장률, 경쟁 밀집도 등 주요 수치를 직접 입력
- **최신 LLM 기반 SWOT 자동 생성**: 입력값을 바탕으로 LLM이 한글로 SWOT 분석을 생성
- **카드형 시각화**: Streamlit에서 강점/약점/기회/위협을 보기 쉽게 카드 형태로 표시
- **LLM 원본 출력 확인**: LLM이 실제로 생성한 원본 텍스트도 확인 가능
- **모델 캐시 경로 커스텀**: 대용량 모델 파일을 원하는 경로(`hf_cache/`)에 저장하여 하드 용량 관리 용이

---

## 환경설정 및 설치

1. **필수 패키지 설치**
   ```bash
   pip install streamlit transformers torch
   ```

2. **(선택) 모델 캐시 경로 변경**
   - `swot_app.py` 상단에서 아래 코드로 캐시 경로를 프로젝트 폴더 내로 지정합니다:
     ```python
     import os
     os.environ["HF_HOME"] = os.path.abspath(os.path.join(os.path.dirname(__file__), "hf_cache"))
     ```
   - 모델 파일은 `kdt_hackathon/05_swot_llm/hf_cache/` 아래에 저장됩니다.

3. **HuggingFace 로그인 및 모델 접근 권한**
   - [HuggingFace](https://huggingface.co/) 계정이 필요합니다.
   - 터미널에서 로그인:
     ```bash
     huggingface-cli login
     ```
   - [mistralai/Mistral-7B-Instruct-v0.2 모델 페이지](https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.2)에서 "Access repository" 버튼을 눌러 사용 승인 요청

---

## 실행 방법

1. 터미널에서 프로젝트 폴더로 이동:
   ```bash
   cd kdt_hackathon/05_swot_llm
   ```
2. Streamlit 앱 실행:
   ```bash
   streamlit run swot_app.py
   ```
3. 웹 브라우저에서 안내된 주소(기본: http://localhost:8501)로 접속

---

## 사용법
1. **생존율, 성장률, 경쟁 밀집도** 값을 입력
2. **[SWOT 자동 생성]** 버튼 클릭
3. LLM이 자동으로 SWOT 분석을 생성하여 카드 형태로 시각화
4. 하단의 "LLM 원본 출력"에서 실제 생성된 텍스트도 확인 가능

---

## 참고/주의사항
- **모델 용량**: Mistral-7B-Instruct-v0.2는 약 13~14GB의 디스크 용량을 사용합니다.
- **최초 실행 시 다운로드 시간**이 오래 걸릴 수 있습니다.
- **VRAM 8GB 이상**(최소) 필요, 16GB 이상 권장
- **모델 접근 권한**이 없으면 실행이 안 됩니다(위의 승인 절차 참고).
- **한글 생성 품질**은 최신 LLM이 KoGPT2 등보다 훨씬 우수합니다.

---

## 확장 아이디어
- 다양한 지표 입력/분석 자동화
- 파일 업로드(엑셀/CSV) → 다수 사업장 일괄 SWOT 분석
- 결과 다운로드(PDF, 엑셀 등)
- 더 다양한 LLM 지원 및 비교

---

## 문의/기여
- 개선 아이디어, 버그 제보, 코드 기여는 언제든 환영합니다! 