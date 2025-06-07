import streamlit as st
import os

def developer():
    if not st.session_state.get('authenticated', False):
        st.warning("⚠️ Vui lòng đăng nhập trước.")
        return

    st.markdown("<h1 style='color: darkblue;'>👩‍💻 Khu vực dành cho Nhà phát triển</h1>", unsafe_allow_html=True)

    st.markdown("""
    - **Thông tin mô hình YOLO đang sử dụng**:  
        + Đường dẫn: `yolov11-custom3/weights/last.pt`  
        + Framework: `Ultralytics YOLO`
    - **Chức năng có thể kiểm tra**:
        + Tải lại mô hình
        + Kiểm tra trạng thái file
        + Hiển thị thông tin tệp trọng số
    """)

    if st.button("Kiểm tra tệp trọng số"):
        model_path = "C:\\Users\\house\\Desktop\\project\\project\\my_model (1)\\yolov11-custom3\\weights\\last.pt"
        if os.path.exists(model_path):
            size = os.path.getsize(model_path) / 1024 / 1024
            st.success(f"✔ File tồn tại, dung lượng: {size:.2f} MB")
        else:
            st.error("❌ Không tìm thấy tệp mô hình.")

    if st.button("Đăng xuất"):
        st.session_state['authenticated'] = False
        st.success("Đã đăng xuất.")
