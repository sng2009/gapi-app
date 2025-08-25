import streamlit as st
from openai import OpenAI
import random

# --- 페이지 설정 ---
st.set_page_config(
    page_title="AI 끝말잇기 (규칙 선택)",
    page_icon="👑"
)

# --- 앱 제목 및 설명 ---
st.title("👑 AI 끝말잇기 게임 (규칙 선택 가능)")
st.markdown("""
플레이하고 싶은 끝말잇기 규칙을 직접 선택하고 AI와 대결해 보세요!  
**왼쪽 사이드바에서 규칙을 선택하고 OpenAI API 키를 입력**하면 게임이 시작됩니다.
""")

# --- 규칙 설명 ---
rule_details = {
    "기본 규칙": "이전 단어의 마지막 글자로만 시작해야 하는 가장 기본적인 규칙입니다. (예: 사과 -> 과자)",
    "표준 두음법칙": "가장 일반적인 규칙입니다. 'ㄴ' 또는 'ㄹ'으로 시작하는 단어를 'ㅇ'으로 시작하는 단어로 바꿀 수 있습니다. (예: 전략 -> 역사, 은닉 -> 익명)",
    "변칙 규칙 ('ㄹ', 'ㄴ' -> 'ㅇ')": "이 게임만의 특별 규칙입니다. 'ㄹ'이나 'ㄴ'으로 끝나는 단어 뒤에 'ㅇ'으로 시작하는 단어를 사용할 수 있습니다. (예: 미사일 -> 역사, 라면 -> 연필)"
}

# --- 시스템 프롬프트 (AI의 두뇌 역할) ---
system_prompts = {
    "기본 규칙": (
        "당신은 '기본 규칙'을 따르는 한국어 끝말잇기 전문가입니다. 다음 규칙을 매우 엄격하게 준수해주세요:\n\n"
        "1. **규칙**: 이전 단어의 마지막 글자로 시작하는 단어만 사용해야 합니다. 두음법칙이나 어떠한 변칙 규칙도 허용되지 않습니다.\n"
        "2. **단어 검증**: 당신과 사용자 모두 실제로 사전에 등재된 유효한 한국어 명사만 사용해야 합니다. (두 글자 이상, 신조어/고유명사 금지)\n"
        "3. **게임 진행**: 응답은 오직 '다음 단어' 또는 '패배/승리 선언'만 간결하게 해야 합니다. 규칙 설명 등 불필요한 말은 절대 하지 마세요.\n"
        "4. **패배 판정**: 사용자가 규칙을 어기면(없는 단어, 잘못된 시작 글자 등) 즉시 패배를 선언하고 명확한 이유를 설명해주세요."
    ),
    "표준 두음법칙": (
        "당신은 '표준 두음법칙'을 따르는 한국어 끝말잇기 전문가입니다. 다음 규칙을 매우 엄격하게 준수해주세요:\n\n"
        "1. **표준 두음법칙**: 한자음 '냐, 녀, 뇨, 뉴, 니' 또는 '랴, 려, 례, 료, 류, 리'로 끝나는 단어 뒤에는 각각 '야, 여, 요, 유, 이'로 시작하는 단어를 사용할 수 있습니다. (예: 전략 -> 역사, 은닉 -> 익명) 당신도 이 규칙을 활용할 수 있습니다.\n"
        "2. **단어 검증**: 당신과 사용자 모두 실제로 사전에 등재된 유효한 한국어 명사만 사용해야 합니다. (두 글자 이상, 신조어/고유명사 금지)\n"
        "3. **게임 진행**: 응답은 오직 '다음 단어' 또는 '패배/승리 선언'만 간결하게 해야 합니다. 규칙 설명 등 불필요한 말은 절대 하지 마세요.\n"
        "4. **패배 판정**: 사용자가 규칙을 어기면(없는 단어, 잘못된 시작 글자 등) 즉시 패배를 선언하고 명확한 이유를 설명해주세요."
    ),
    "변칙 규칙 ('ㄹ', 'ㄴ' -> 'ㅇ')": (
        "당신은 '변칙 규칙'을 따르는 한국어 끝말잇기 전문가입니다. 다음 규칙을 매우 엄격하게 준수해주세요:\n\n"
        "1. **매우 중요한 변칙 규칙**: 이전 단어가 'ㄹ' 또는 'ㄴ'으로 끝나는 경우, 다음 단어는 원래 글자 또는 'ㅇ' 둘 중 하나로 시작할 수 있습니다. (예: '미사일' 뒤에는 '일요일' 또는 '역사' 모두 정답 / '라면' 뒤에는 '면도기' 또는 '연필' 모두 정답) 이것은 이 게임만의 특별 규칙입니다.\n"
        "2. **단어 검증**: 당신과 사용자 모두 실제로 사전에 등재된 유효한 한국어 명사만 사용해야 합니다. (두 글자 이상, 신조어/고유명사 금지)\n"
        "3. **게임 진행**: 응답은 오직 '다음 단어' 또는 '패배/승리 선언'만 간결하게 해야 합니다. 규칙 설명 등 불필요한 말은 절대 하지 마세요.\n"
        "4. **패배 판정**: 사용자가 규칙을 어기면(없는 단어, 잘못된 시작 글자 등) 즉시 패배를 선언하고 명확한 이유를 설명해주세요."
    )
}


# --- 사이드바 ---
with st.sidebar:
    st.header("⚙️ 게임 설정")
    
    # 규칙 선택 라디오 버튼
    selected_rule = st.radio(
        "규칙을 선택하세요:",
        options=list(rule_details.keys()),
        captions=list(rule_details.values())
    )

    # API 키 입력
    openai_api_key = st.text_input("OpenAI API 키를 입력해주세요", type="password")
    st.markdown("[API 키 발급받는 방법 알아보기](https://platform.openai.com/account/api-keys)")

    # 새 게임 시작 버튼
    if st.button("새 게임 시작하기"):
        start_words = ["바나나", "사과", "기차", "나무", "학교", "컴퓨터", "강아지", "사랑", "우유", "라면", "로켓", "장난감"]
        random_word = random.choice(start_words)
        
        # 선택된 규칙과 시작 단어로 세션 상태 초기화
        st.session_state.selected_rule = selected_rule
        st.session_state.messages = [
            {"role": "assistant", "content": f"안녕하세요! [{selected_rule}]으로 끝말잇기 게임을 시작합니다. 저부터 시작할게요. **{random_word}**"}
        ]
        st.rerun()

# --- 세션 상태 초기화 ---
if "messages" not in st.session_state:
    st.session_state.selected_rule = "기본 규칙"
    st.session_state.messages = [
        {"role": "assistant", "content": f"안녕하세요! 왼쪽 사이드바에서 규칙을 선택하고 API 키를 입력한 뒤 '새 게임 시작하기'를 눌러주세요."}
    ]

# --- 메인 화면 ---
st.info(f"현재 적용 중인 규칙: **{st.session_state.selected_rule}**")

# API 키가 입력되지 않았을 경우 안내
if not openai_api_key:
    st.warning("왼쪽 사이드바에서 OpenAI API 키를 입력하시면 게임이 시작됩니다.")
else:
    # 대화 기록 표시
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # 사용자 입력 처리
    prompt = st.chat_input("단어를 입력하세요...")
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        try:
            client = OpenAI(api_key=openai_api_key)
            
            # 현재 선택된 규칙에 맞는 시스템 프롬프트를 가져옴
            system_prompt = system_prompts[st.session_state.selected_rule]
            
            with st.chat_message("assistant"):
                with st.spinner("AI가 단어를 검증하고 생각하고 있어요..."):
                    
                    messages_for_api = [{"role": "system", "content": system_prompt}] + st.session_state.messages
                    
                    stream = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=messages_for_api,
                        stream=True,
                    )
                    response = st.write_stream(stream)
            
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun() # AI 응답 후 즉시 새로고침하여 깔끔하게 표시

        except Exception as e:
            st.error(f"오류가 발생했습니다: {e}")
            st.session_state.messages.pop() # 오류 발생 시 마지막 사용자 메시지 제거