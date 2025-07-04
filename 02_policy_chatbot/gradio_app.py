import gradio as gr
from policy_chatbot import PolicyChatbot
import pandas as pd

# 챗봇 인스턴스 생성
chatbot = None

def initialize_chatbot():
    """챗봇 초기화"""
    global chatbot
    if chatbot is None:
        chatbot = PolicyChatbot()
    return "✅ 챗봇이 준비되었습니다!"

def search_policies(query, top_k=5):
    """정책 검색"""
    global chatbot
    if chatbot is None:
        return "❌ 챗봇이 초기화되지 않았습니다. 먼저 초기화해주세요."
    
    if not query.strip():
        return "❌ 검색어를 입력해주세요."
    
    try:
        results = chatbot.search_policies(query, top_k=int(top_k))
        
        if not results:
            return f"😔 '{query}'에 대한 관련 정책을 찾을 수 없습니다."
        
        # 결과 포맷팅
        output = f"🔍 '{query}'에 대한 {len(results)}개의 정책을 찾았습니다!\n\n"
        
        for i, result in enumerate(results, 1):
            output += f"**{i}. {result['title']}**\n"
            output += f"🎯 지원대상: {result['target']}\n"
            output += f"🏢 소관기관: {result['organization']}\n"
            output += f"📅 신청기간: {result['period']}\n"
            output += f"📞 문의처: {result['contact']}\n"
            output += f"📊 유사도: {result['similarity_score']:.3f}\n"
            output += f"📝 신청방법: {result['application_method'][:100]}...\n"
            output += "-" * 50 + "\n\n"
        
        return output
        
    except Exception as e:
        return f"❌ 검색 중 오류가 발생했습니다: {str(e)}"

def get_policy_summary(query):
    """정책 요약"""
    global chatbot
    if chatbot is None:
        return "❌ 챗봇이 초기화되지 않았습니다."
    
    return chatbot.get_policy_summary(query)

def get_statistics():
    """통계 정보"""
    global chatbot
    if chatbot is None:
        return "❌ 챗봇이 초기화되지 않았습니다."
    
    try:
        data = chatbot.data
        
        # 기본 통계
        total_policies = len(data)
        
        # 지원대상별 통계
        target_stats = data['지원대상'].value_counts().head(5)
        target_output = "\n".join([f"• {target}: {count}개" for target, count in target_stats.items()])
        
        # 지원분야별 통계
        field_stats = data['지원분야(대)'].value_counts().head(5)
        field_output = "\n".join([f"• {field}: {count}개" for field, count in field_stats.items()])
        
        # 소관기관별 통계
        org_stats = data['소관기관'].value_counts().head(5)
        org_output = "\n".join([f"• {org}: {count}개" for org, count in org_stats.items()])
        
        output = f"""
📊 **정책 통계**

**총 정책 수:** {total_policies}개

**지원대상별 분포 (상위 5개):**
{target_output}

**지원분야별 분포 (상위 5개):**
{field_output}

**소관기관별 분포 (상위 5개):**
{org_output}
        """
        
        return output
        
    except Exception as e:
        return f"❌ 통계 생성 중 오류가 발생했습니다: {str(e)}"

# Gradio 인터페이스 생성
with gr.Blocks(title="🏛️ 정책 챗봇", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🏛️ 정책 챗봇")
    gr.Markdown("### 💡 AI 기반 정책 검색 시스템")
    gr.Markdown("자연어로 원하는 정책을 쉽게 찾아보세요!")
    
    with gr.Tab("🔍 정책 검색"):
        with gr.Row():
            with gr.Column(scale=3):
                query_input = gr.Textbox(
                    label="검색어",
                    placeholder="예: 중소기업 기술지원, 창업 지원, 수출 진출 등",
                    lines=2
                )
                
                with gr.Row():
                    search_btn = gr.Button("🔍 검색", variant="primary")
                    clear_btn = gr.Button("🗑️ 초기화")
                
                top_k_slider = gr.Slider(
                    minimum=1,
                    maximum=10,
                    value=5,
                    step=1,
                    label="검색 결과 수"
                )
                
            with gr.Column(scale=1):
                init_btn = gr.Button("🚀 챗봇 초기화", variant="secondary")
                init_output = gr.Textbox(label="초기화 상태", interactive=False)
        
        search_output = gr.Textbox(
            label="검색 결과",
            lines=20,
            interactive=False
        )
        
        # 예시 쿼리 버튼들
        gr.Markdown("**💡 검색 예시:**")
        example_queries = [
            "중소기업 기술지원",
            "창업 지원", 
            "수출 진출",
            "청년 지원",
            "AI 기술 개발",
            "소상공인 지원"
        ]
        
        with gr.Row():
            for example in example_queries:
                gr.Button(example, size="sm").click(
                    lambda x=example: x,
                    outputs=query_input
                )
    
    with gr.Tab("📊 통계"):
        stats_btn = gr.Button("📈 통계 보기", variant="primary")
        stats_output = gr.Markdown()
    
    with gr.Tab("📋 정책 요약"):
        summary_input = gr.Textbox(
            label="검색어",
            placeholder="요약할 정책 키워드를 입력하세요"
        )
        summary_btn = gr.Button("📋 요약 생성", variant="primary")
        summary_output = gr.Textbox(
            label="정책 요약",
            lines=15,
            interactive=False
        )
    
    # 이벤트 연결
    init_btn.click(initialize_chatbot, outputs=init_output)
    
    search_btn.click(
        search_policies,
        inputs=[query_input, top_k_slider],
        outputs=search_output
    )
    
    clear_btn.click(
        lambda: ("", ""),
        outputs=[query_input, search_output]
    )
    
    stats_btn.click(get_statistics, outputs=stats_output)
    
    summary_btn.click(
        get_policy_summary,
        inputs=summary_input,
        outputs=summary_output
    )

# 실행
if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=True,
        show_error=True
    ) 