import streamlit as st
import base64
from PIL import Image
import io
from db import feedback_collection 

def list_feedback():
    st.subheader("📃 Danh sách phản hồi từ người dùng")

    feedbacks = feedback_collection.find().sort("timestamp", -1)
    for fb in feedbacks:
        with st.container():
            st.markdown(f"**👤 Người dùng:** {fb.get('user', 'unknown')}")
            st.markdown(f"**🕒 Thời gian:** {fb['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
            st.markdown(f"**📝 Nội dung:** {fb.get('message', '')}")
            if fb.get("wrong_labels"):
                st.markdown(f"**❌ Vi khuẩn sai:** {fb['wrong_labels']}")
            if fb.get("min_confidence"):
                st.markdown(f"**📉 Chỉ số tự tin thấp nhất:** {fb['min_confidence']}%")
            if fb.get("image_base64"):
                image_data = base64.b64decode(fb["image_base64"])
                image = Image.open(io.BytesIO(image_data))
                max_width = 150
                w_percent = (max_width / float(image.size[0]))
                h_size = int((float(image.size[1]) * float(w_percent)))
                image_resized = image.resize((max_width, h_size))
                st.image(image_resized, caption=None, use_container_width=False)
            st.markdown("---")
