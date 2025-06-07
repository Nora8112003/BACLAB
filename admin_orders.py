import streamlit as st
from db import orders_collection, users_collection
from bson.objectid import ObjectId
from datetime import datetime, timedelta

def approve_order(order_id):
    order = orders_collection.find_one({"_id": ObjectId(order_id)})
    if not order:
        return {"error": "Không tìm thấy đơn hàng."}
    
    user_id = order.get("user_id")
    days = order.get("days", 0)
    now = datetime.utcnow()

    start_date = now
    end_date = start_date + timedelta(days=days)

#Cap nhat trang thai va thoi gian cho don hang 
    orders_collection.update_one(
        {"_id": ObjectId(order_id)},
        {
            "$set": {
                "status": "approved",
                "approved_at": now,
                "start_date": start_date,
                "end_date": end_date
            }
        }
    )
#Cap nhat thong tin nguoi dung 
    user = users_collection.find_one({"_id": user_id})
    if not user:
        return {"error": "Không tìm thấy user"}

    current_premium_until = user.get("premium_until")
    if current_premium_until and current_premium_until > now:
        new_premium_until = current_premium_until + timedelta(days=days)
    else:
        new_premium_until = now + timedelta(days=days)

    users_collection.update_one(
        {"_id": user_id},
        {
            "$set": {
                "is_premium": True,
                "premium_until": new_premium_until,
                "usage_count": 0,
                "usage_limit": 5,
                "free_uses": 0
            }
        }
    )

    return {"message": "✔ Đã duyệt đơn hàng và cấp quyền sử dụng cho người dùng"}


def reject_order(order_id):
    order = orders_collection.find_one({"_id": ObjectId(order_id)})
    if not order:
        return {"error": "Không tìm thấy đơn hàng"}

    orders_collection.update_one({"_id": ObjectId(order_id)}, {"$set": {"status": "rejected", "rejected_at": datetime.utcnow()}})
    return {"message": "❗ Đã từ chối đơn hàng"}

def review_orders():
    st.title("🛠 Quản lý đơn hàng chờ duyệt")

    pending_orders = list(orders_collection.find({"status": "pending"}))

    if not pending_orders:
        st.info("Không có đơn hàng nào chờ duyệt")
        return

    for order in pending_orders:
        user = users_collection.find_one({"_id": order["user_id"]})
        username = user.get("username") if user else "Unknown"

        st.write(f"**Người dùng:** {username}")
        st.write(f"**Gói:** {order.get('package')}")
        st.write(f"**Thời gian:** {order.get('days')} ngày")
        st.write(f"**Giá:** {order.get('price'):,} VNĐ")
        st.write(f"**Ngày đặt:** {order.get('created_at').strftime('%d/%m/%Y %H:%M:%S')}")

        col1, col2 = st.columns(2)
        with col1:
            if st.button(f"Duyệt {order['_id']}", key=f"approve_{order['_id']}"):
                result = approve_order(order["_id"])
                if "message" in result:
                    st.success(result["message"])
                elif "error" in result:
                    st.error(result["error"])
                st.rerun()

        with col2:
            if st.button(f"Từ chối {order['_id']}", key=f"reject_{order['_id']}"):
                result = reject_order(order["_id"])
                if "message" in result:
                    st.info(result["message"])
                elif "error" in result:
                    st.error(result["error"])
                st.rerun()

        st.markdown("---")
