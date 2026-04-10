import streamlit as st
import requests

# 1. Cấu hình trang
st.set_page_config(page_title="EduChatbot - Tư vấn học tập", page_icon="🎓")

st.title("🎓 EduChatbot")
st.subheader("Trợ lý cố vấn học tập thông minh cho học sinh")

# --- BẮT ĐẦU PHẦN DISCLAIMER (SIDEBAR) ---
with st.sidebar:
    st.markdown("### ℹ️ Thông tin hệ thống")
    st.info(
        "**Nguồn dữ liệu:**\n"
        "Toàn bộ thông tin môn học, tín chỉ và lộ trình được trích xuất từ Chương trình đào tạo chính thức của trường Đại học Sài Gòn cập nhật năm 2025-2026."
    )
    st.warning(
        "**⚠️ Lưu ý (Disclaimer):**\n"
        "EduChatbot là trợ lý AI mang tính chất tư vấn và tham khảo nhanh."
        "Sinh viên vui lòng luôn đối chiếu lại với Cổng thông tin đào tạo hoặc liên hệ trực tiếp Phòng Giáo vụ tại chính trường bản thân theo học để có quyết định chính thức."
    )
# --- KẾT THÚC PHẦN DISCLAIMER ---

st.caption(
    "💡 **Nguồn dữ liệu:** Cập nhật từ Chương trình đào tạo chính thức của trường Đại học Sài Gòn cập nhật năm 2025-2026.\n"
    "*(Lưu ý: Edu-Mentor là AI tư vấn, thông tin chỉ mang tính tham khảo. Vui lòng đối chiếu với Phòng Giáo vụ trước khi đăng ký môn học).* "
)

# 2. Khởi tạo lịch sử chat và Lời chào đầu tiên
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": """
👋 Chào bạn! Mình là **Edu-Mentor**, trợ lý học vụ thông minh được xây dựng bằng công nghệ **Đồ thị Tri thức (Knowledge Graph)** kết hợp với AI.

Mình có thể giúp bạn giải đáp các thông tin về chương trình đào tạo của trường Đại học, bao gồm:
* 📚 **Chương trình đào tạo:** Môn học của từng học kỳ, môn tiên quyết, môn song hành.
* ⏱️ **Tín chỉ:** Tổng số tín chỉ của ngành, số tín chỉ từng môn học.
* 🧩 **Phân loại môn học:** Khối kiến thức (Đại cương, Cơ sở ngành...), Loại học phần (Bắt buộc, Tự chọn).

Bạn cần tư vấn về ngành học nào và mình có thể giúp gì cho bạn hôm nay?
"""
        }
    ]

# 3. Hiển thị các tin nhắn cũ trong lịch sử
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 4. Ô nhập câu hỏi
if prompt := st.chat_input("Ví dụ: Học kỳ 1 học những môn gì?"):
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
                
                # Sửa lại đoạn check lỗi một chút (requests trả về response object, phải parse sang json() trước khi dùng 'in')
                data = response.json() 
                
                if "Loi" in data:
                    # Nếu có chữ "Loi" trong JSON thì in ra câu thông báo thân thiện màu đỏ
                    st.error(data["Loi"])
                else:
                    if response.status_code == 200:
                        answer = data.get("Tra_Loi", "Dạ, hiện tại mình chưa có thông tin về vấn đề này.")
                        st.markdown(answer)
                        # Lưu vào lịch sử
                        st.session_state.messages.append({"role": "assistant", "content": answer})
                    else:
                        st.error("Lỗi kết nối đến Server FastAPI!")
            except Exception as e:
                st.error(f"Đã xảy ra lỗi hệ thống: {str(e)}")