import streamlit as st
import base64
from db import create_order
@st.cache_data
def get_base64_image(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

def show_payment():
    st.title("💳 Trang Thanh Toán")

    package = st.session_state.get("payment_package")
    if not package:
        st.error("Không có thông tin gói thanh toán, vui lòng quay lại trang mua gói.")
        if st.button("🔙 Quay lại mua gói"):
            st.session_state["page"] = "main"
        return

    st.markdown(f"""
    <div style="border:1px solid #ccc; padding:20px; border-radius:10px; max-width:500px; margin:auto;">
        <h3>Gói: {package['name']}</h3>
        <p>⏱️ Thời hạn: <b>{package['days']} ngày</b></p>
        <p>💰 Giá: <b>{package['price']:,} VNĐ</b></p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("## 🔌 Chọn phương thức thanh toán:")

    tab1, tab2 = st.tabs(["📱 Momo", "🏦 Chuyển khoản ngân hàng"])

    # Momo
    with tab1:
        momo_qr_base64 = get_base64_image("assets/momo_qr.jpg")
        st.markdown("### Quét mã Momo:")
        st.image(f"data:image/png;base64,{momo_qr_base64}", width=300)
        st.info(f"""
        ➤ Nội dung chuyển khoản: **{st.session_state['user']['username']} - {package['name']}**

        ➤ SĐT Momo: **0335526732**

        ➤ Tên: **Ngô Chử Tịch**
        """)

    #Ngan hang
    with tab2:
        bank_qr_base64 = get_base64_image("assets/bank_qr.jpg")
        st.markdown("### Quét mã ngân hàng:")
        st.image(f"data:image/png;base64,{bank_qr_base64}", width=300)
        st.info(f"""
        ➤ Nội dung chuyển khoản: **{st.session_state['user']['username']} - {package['name']}**

        ➤ STK: **63562914666**

        ➤ Ngân hàng: **TPBank**

        ➤ Chủ tài khoản: **Ngô Chử Tịch **
        """)

        st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✔ Tôi đã thanh toán"):
            user_id = st.session_state.get("user_id")
            package = st.session_state.get("payment_package")

            if not user_id or not package:
                st.error("Thiếu thông tin người dùng hoặc gói dịch vụ")
                st.stop()

            # Goi ham tao don hang 
            create_order(
                user_id=user_id,
                package_name=package["name"],
                days=package["days"],
                price=package["price"]
            )

            st.success("🎉 Thanh toán thành công! Đơn hàng đã được tạo.")
            st.session_state["page"] = "main"
            st.session_state["payment_package"] = None

            st.rerun()
            st.stop()

    with col2:
        if st.button("⬅ Quay lại trang chủ"):
            st.session_state["page"] = "main"
            st.rerun()

