import requests, pandas as pd, html, re, json

URL = "https://www.bizinfo.go.kr/uss/rss/bizinfoApi.do"
params = {
    "crtfcKey": "FFxycB",           # ← 발급받으신 키
    "dataType": "json",
    "searchCnt": 30,
    "hashtags": "소상공인,경기",
}
def clean_html(text):
    text = re.sub(r'(<br\s*/?>|</?p>)', '\n', text)
    text = re.sub(r'<[^>]*>', '', text)
    return html.unescape(re.sub(r'\s+', ' ', text)).strip()

items = requests.get(URL, params=params, timeout=30).json()['jsonArray']['item']
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
pd.DataFrame(rows).to_csv("gyeonggi_smallbiz_policies.csv", index=False, encoding="utf-8-sig")
print("✔ CSV 저장 완료!")