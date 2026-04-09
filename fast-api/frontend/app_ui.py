import streamlit as st
import requests

# 1. Cấu hình trang
st.set_page_config(page_title="EduChatbot - Tư vấn học tập", page_icon="🎓")

st.title("🎓 EduChatbot")
st.subheader("Cố vấn học tập thông minh cho sinh viên")

# 2. Khởi tạo lịch sử chat (để tin nhắn không bị mất khi load lại trang)
if "messages" not in st.session_state:
    st.session_state.messages = []

# 3. Hiển thị các tin nhắn cũ trong lịch sử
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 4. Ô nhập câu hỏi
if prompt := st.chat_input("Hỏi tôi về lộ trình môn học, tín chỉ..."):
    # Hiển thị câu hỏi của người dùng
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 5. Gọi đến Backend FastAPI để lấy câu trả lời
    with st.chat_message("assistant"):
        with st.spinner("Đang lục tìm trong Đồ thị tri thức..."):
            try:
                # Địa chỉ API FastAPI của ông đang chạy
                response = requests.get(f"http://127.0.0.1:8000/chat?q={prompt}")
                if response.status_code == 200:
                    answer = response.json().get("Tra_Loi", "Bot không có câu trả lời.")
                    st.markdown(answer)
                    # Lưu vào lịch sử
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                else:
                    st.error("Lỗi kết nối đến Server FastAPI!")
            except Exception as e:
                st.error(f"Đã xảy ra lỗi: {str(e)}")