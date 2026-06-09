import streamlit as st
from google import genai
from google.genai import types

# ----------------------------
# 페이지 설정
# ----------------------------
st.set_page_config(
    page_title="연애상담 챗봇",
    page_icon="💕",
    layout="centered"
)

st.title("💕 연애상담 챗봇")
st.caption("Gemini 2.5 Flash Lite 기반")

# ----------------------------
# API 키 불러오기
# ----------------------------
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    st.error("Secrets에 GEMINI_API_KEY가 설정되지 않았습니다.")
    st.stop()

# ----------------------------
# Gemini Client
# ----------------------------
try:
    client = genai.Client(api_key=api_key)
except Exception as e:
    st.error(f"Gemini 초기화 실패: {e}")
    st.stop()

# ----------------------------
# 시스템 프롬프트
# ----------------------------
SYSTEM_PROMPT = """
당신은 전문 연애상담 코치입니다.

규칙:
1. 공감적으로 답변한다.
2. 상대방 입장도 균형 있게 고려한다.
3. 현실적이고 구체적인 조언을 제공한다.
4. 사용자를 비난하지 않는다.
5. 위험한 행동을 권장하지 않는다.
6. 답변은 한국어로 한다.
"""

# ----------------------------
# 채팅 기록 초기화
# ----------------------------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "안녕하세요 😊 연애 고민이 있다면 편하게 이야기해주세요."
        }
    ]

# ----------------------------
# 이전 대화 표시
# ----------------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ----------------------------
# 사용자 입력
# ----------------------------
user_input = st.chat_input("연애 고민을 입력하세요...")

if user_input:

    # 사용자 메시지 저장
    st.session_state.messages.append(
        {"role": "user", "content": user_input}
    )

    with st.chat_message("user"):
        st.markdown(user_input)

    try:
        # 대화 기록 생성
        history_text = ""

        for msg in st.session_state.messages:
            role = "사용자" if msg["role"] == "user" else "상담사"
            history_text += f"{role}: {msg['content']}\n"

        prompt = f"""
{SYSTEM_PROMPT}

다음은 지금까지의 대화입니다.

{history_text}

상담사 답변:
"""

        with st.chat_message("assistant"):
            with st.spinner("생각 중..."):

                response = client.models.generate_content(
                    model="gemini-2.5-flash-lite",
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=0.8,
                        max_output_tokens=1000,
                    ),
                )

                answer = response.text

                st.markdown(answer)

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": answer
            }
        )

    except Exception as e:
        error_msg = f"오류가 발생했습니다.\n\n{str(e)}"

        with st.chat_message("assistant"):
            st.error(error_msg)

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": error_msg
            }
        )

# ----------------------------
# 사이드바
# ----------------------------
with st.sidebar:

    st.header("설정")

    if st.button("대화 초기화"):
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "안녕하세요 😊 연애 고민이 있다면 편하게 이야기해주세요."
            }
        ]
        st.rerun()

    st.info(
        """
        Gemini 2.5 Flash Lite
        Streamlit Community Cloud 배포용 예제
        """
    )
