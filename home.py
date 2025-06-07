import streamlit as st

def home():
    st.title("🧫 Ứng dụng Nhận diện và Phân loại Vi khuẩn")
    
    st.markdown("""
    ## 🎯 Mục tiêu
    Ứng dụng này giúp người dùng:
    - Nhận diện các loại vi khuẩn trong ảnh.
    - Hỗ trợ phân tích hình ảnh phòng thí nghiệm.
    - Giao diện thân thiện, dễ sử dụng cho y sĩ và nhà nghiên cứu.

    ## ⚙️ Công nghệ sử dụng
    - Python, Streamlit, Roboflow 
    - YOLOv11 (mô hình nhận diện ảnh)
    - MongoDB Atlas (cơ sở dữ liệu)
    
    ---
    👉 Vui lòng đăng nhập để sử dụng tính năng chính của hệ thống.
    """)
