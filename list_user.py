import streamlit as st
import pandas as pd
from db import get_users, get_orders, update_user_role, delete_user
from datetime import datetime

def list_user():
    st.header("📋 Thông tin người dùng")

    # O tim kiem 
    search_name = st.text_input("🔍 Tìm kiếm theo tên", value="", key="search_name")

    users = get_users()  #lay toan bo nguoi dung 
    orders = get_orders()

    #Loc nguoi dung khong phai admin 
    users = [u for u in users if u.get("role") != "admin"]

    # Loc theo ten tim kiem neu co 
    if search_name:
        users = [user for user in users if search_name.lower() in user['username'].lower()]

    def enrich_users(users, orders):
        enriched = []
        for user in users:
            user_id = str(user["_id"])
            user_orders = [o for o in orders if str(o.get("user_id")) == user_id]

            latest_order = None
            if user_orders:
                latest_order = max(
                    user_orders,
                    key=lambda x: x.get("start_date", datetime.min) if isinstance(x.get("start_date"), datetime) else datetime.min
                )

            if latest_order:
                start_date = latest_order.get("start_date")
                if isinstance(start_date, datetime):
                    start_date = start_date.strftime("%d/%m/%Y")
                else:
                    start_date = "Chưa có"

                end_date = latest_order.get("end_date")
                if isinstance(end_date, datetime):
                    end_date = end_date.strftime("%d/%m/%Y")
                else:
                    end_date = "Chưa có"
            else:
                start_date = "Chưa có"
                end_date = "Chưa có"

            free_uses = user.get("free_uses", 0)

            enriched.append({
                "_id": user["_id"],
                "username": user.get("username", ""),
                "email": user.get("email", ""),
                "start_date": start_date,
                "end_date": end_date,
                "free_uses": free_uses,
                "role": user.get("role", "user")
            })
        return enriched

    if not users:
        st.info("Không có người dùng nào.")
        return

    enriched_data = enrich_users(users, orders)

    st.write("### Danh sách người dùng")
   
    # Tiêu đề cột với thêm cột nút Lưu vai trò và nút Xóa
    header_cols = st.columns([2, 3, 2, 2, 2, 2, 1, 1])
    header_cols[0].markdown("**Người dùng**")
    header_cols[1].markdown("**Email**")
    header_cols[2].markdown("**Ngày bắt đầu mua gói**")
    header_cols[3].markdown("**Ngày kết thúc gói**")
    header_cols[4].markdown("**Số lần sử dụng miễn phí**")
    header_cols[5].markdown("**Vai trò**")
    
    for user in enriched_data:
        cols = st.columns([2, 3, 2, 2, 2, 2, 1, 1])
        cols[0].write(user["username"])
        cols[1].write(user["email"])
        cols[2].write(user["start_date"])
        cols[3].write(user["end_date"])
        cols[4].write(user["free_uses"])

        # Selectbox vai tro
        new_role = cols[5].selectbox(
            "",
            options=["user", "admin"],
            index=0 if user["role"] == "user" else 1,
            key=f"role_{user['_id']}",
            label_visibility="collapsed"
        )

        # Nut Luu 
        if new_role != user["role"]:
            if cols[6].button("Lưu", key=f"save_{user['_id']}"):
                update_user_role(user["_id"], new_role)
                st.success(f"Đã cập nhật vai trò cho {user['username']}")
                st.rerun()

        # Nut Xoa
        if cols[7].button("Xóa", key=f"del_{user['_id']}"):
            delete_user(user["_id"])
            st.success(f"Đã xóa tài khoản {user['username']}")
            st.rerun()
