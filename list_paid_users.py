import streamlit as st
from db import get_users, get_orders
from datetime import datetime, date

def safe_date(date_obj):
    """Trả về đối tượng datetime.date hợp lệ"""
    if isinstance(date_obj, datetime):
        return date_obj.date()
    elif isinstance(date_obj, date):
        return date_obj
    else:
        return datetime.utcnow().date()

def list_paid_users():
    st.header("💳 Người dùng đã mua gói")

    users = get_users()
    orders = get_orders()

    if not orders:
        st.info("Không có người dùng nào mua gói.")
        return

    user_map = {str(u["_id"]): u for u in users}

    for order in orders:
        user_id = str(order.get("user_id"))
        user = user_map.get(user_id)
        if not user:
            continue

        with st.expander(f"🧾 {user['username']} - {order.get('package')}"):
            st.text_input(
                "Tên gói",
                value=order.get("package", ""),
                key=f"pkg_{order['_id']}",
                disabled=True
            )

            st.number_input(
                "Giá (VNĐ)",
                value=int(order.get("price", 0)),
                key=f"price_{order['_id']}",
                disabled=True
            )

            st.date_input(
                "Ngày mua",
                value=safe_date(order.get("start_date")),
                key=f"start_{order['_id']}",
                disabled=True
            )

            st.date_input(
                "Ngày hết hạn",
                value=safe_date(order.get("end_date")),
                key=f"end_{order['_id']}",
                disabled=True
            )
