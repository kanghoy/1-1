import streamlit as st
import google.generativeai as genai

# 1. 페이지 설정 및 제목
st.set_page_config(page_title="연애상담소 챗봇", page_icon="💖", layout="centered")
st.title("💖 달콤살벌 연애상담소")
st.write("말 못 할 연애 고민, 속 시원하게 털어놓으세요. 당신의 편에서 들어드릴게요.")

# 2. Streamlit Secrets에서 API 키 불러오기 및 설정
try:
    # Streamlit Cloud 배포 환경 및 로컬 .streamlit/secrets.toml 대응
    gemini_api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=gemini_api_key)
except KeyError:
    st.error("⚠️ API 키를 찾을 수 없습니다. Streamlit Secrets에 'GEMINI_API_KEY'를 설정해주세요.")
    st.stop()

# 3. 세션 상태(Session State)로 채팅 기록 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []

# 4. 기존 채팅 기록 화면에 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# 5. 사용자 입력 받기
if user_input := st.chat_input("고민을 이야기해주세요... (예: 남친이 연락을 잘 안 해요)"):
    
    # 사용자 메시지 저장 및 화면 표시
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    # 6. 챗봇 답변 생성 및 오류 처리
    with st.chat_message("assistant"):
        message_placeholder = st.empty() # 실시간 텍스트 출력을 위한 프레임
        
        try:
            with st.spinner("당신의 고민을 신중하게 생각하는 중... 🤔"):
                # gemini-2.5-flash-lite 모델 설정
                # 연애상담사 페르소나 부여를 위한 system_instruction 추가
                model = genai.GenerativeModel(
                    model_name="gemini-2.5-flash-lite",
                    system_instruction=(
                        "당신은 공감 능력이 뛰어나고 때로는 뼈 때리는 조언도 아끼지 않는 전문 연애상담사입니다. "
                        "사용자의 연애 고민을 경청하고, 친근하고 따뜻한 말투(반말과 존댓말 중 다정한 어조 선택)로 "
                        "실질적이고 위로가 되는 답변을 제공해주세요. 이모지도 적절히 섞어 써주세요."
                    )
                )
                
                # 대화 맥락을 유지하기 위해 기존 대화 기록을 Gemini 형식으로 변환
                # (Gemini API는 user와 model 역할을 사용합니다)
                history = []
                for msg in st.session_state.messages[:-1]: # 현재 입력 직전까지의 기록
                    role = "user" if msg["role"] == "user" else "model"
                    history.append({"role": role, "parts": [msg["content"]]})
                
                # 멀티턴 대화 시작
                chat = model.start_chat(history=history)
                
                # 답변 생성
                response = chat.send_message(user_input)
                ai_response = response.text
                
                # 화면에 결과 출력 및 세션 저장
                message_placeholder.write(ai_response)
                st.session_state.messages.append({"role": "assistant", "content": ai_response})
                
        except Exception as e:
            # API 오류, 네트워크 단절 등 예외 처리
            error_msg = f"죄송합니다. 답변을 생성하는 중에 오류가 발생했습니다. 다시 시도해주세요. 😢 (오류 내용: {str(e)})"
            message_placeholder.error(error_msg)
