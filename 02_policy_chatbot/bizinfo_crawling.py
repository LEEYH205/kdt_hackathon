import requests, pandas as pd, html, re, json
from datetime import datetime

URL = "https://www.bizinfo.go.kr/uss/rss/bizinfoApi.do"
params = {
    "crtfcKey": "FFxycB",           # ← 발급받으신 키
    "dataType": "json",
    "searchCnt": 500,
    "hashtags": "소상공인,경기",
}
def clean_html(text):
    text = re.sub(r'(<br\s*/?>|</?p>)', '\n', text)
    text = re.sub(r'<[^>]*>', '', text)
    return html.unescape(re.sub(r'\s+', ' ', text)).strip()

try:
    response = requests.get(URL, params=params, timeout=60)
    response.raise_for_status()
    data = response.json()
    print("API 응답 구조:", data.keys())
    json_array = data.get('jsonArray', [])
    if isinstance(json_array, list):
        items = json_array
    else:
        items = json_array.get('item', [])
    if not items:
        print("응답 내용:", data)
        items = []
except requests.exceptions.Timeout:
    print("API 요청 타임아웃. 서버가 응답하지 않습니다.")
    items = []
except requests.exceptions.RequestException as e:
    print(f"API 요청 실패: {e}")
    items = []
except json.JSONDecodeError as e:
    print(f"JSON 파싱 실패: {e}")
    print("응답 내용:", response.text[:500])
    items = []
rows = []
for it in items:
    rows.append({
        "title": it.get("pblancNm"),
        "body text": clean_html(it.get("bsnsSumryCn", "")),
        "지원대상": it.get("trgetNm"),
        "소관기관": it.get("jrsdInsttNm"),
        "지원분야(대)": it.get("pldirSportRealmLclasCodeNm"),
        "지원분야(중)": it.get("pldirSportRealmMlsfcCodeNm"),
        "사업수행기관": it.get("excInsttNm"),
        "문의처": clean_html(it.get("refrncNm", "")),
        "신청기간": it.get("reqstBeginEndDe"),
        "사업신청방법설명": clean_html(it.get("reqstMthPapersCn", "")),
    })
pd.DataFrame(rows).to_csv(f"gyeonggi_smallbiz_policies_{params['searchCnt']}_{params['hashtags']}_{datetime.now().strftime('%Y%m%d')}.csv", index=False, encoding="utf-8-sig")
print("✔ CSV 저장 완료!")