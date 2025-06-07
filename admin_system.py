import streamlit as st
import os
import platform
import psutil
import datetime

def system_info():
    st.header("⚙ Thông số hệ thống")

    st.markdown("### 🖥 Thông tin hệ điều hành")
    st.write(f"Hệ điều hành: {platform.system()} {platform.release()}")
    st.write(f"Phiên bản Python: {platform.python_version()}")
    st.write(f"Máy chủ: {platform.node()}")

    st.markdown("### 📊 Tài nguyên hệ thống")
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage('/')

    st.write(f"RAM đang dùng: {mem.used // (1024 ** 2)} MB / {mem.total // (1024 ** 2)} MB")
    st.write(f"Ổ đĩa: {disk.used // (1024 ** 3)} GB / {disk.total // (1024 ** 3)} GB")
    st.write(f"CPU đang dùng: {psutil.cpu_percent()}%")

    st.markdown("### 💾 Cập nhật mô hình mới")

    uploaded_model = st.file_uploader("📁 Tải lên file mô hình (.pt)", type=["pt", "onnx"])

    if uploaded_model:
        save_path = os.path.join("models", uploaded_model.name)
        with open(save_path, "wb") as f:
            f.write(uploaded_model.read())

        st.success(f"✔ Mô hình mới đã được lưu tại: '{save_path}'")
        
