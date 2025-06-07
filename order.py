from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime, timedelta
import streamlit as st
from db import users_collection

MONGO_URI = "mongodb+srv://admin:2qhAarVQ23UzLHhq@cluster0.cxmy1yt.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(MONGO_URI)

db = client['nhandienvikhuan']
orders_collection = db['orders']
packages_collection = db['packages']

def create_order(user_id, package_name, days, price):
    now = datetime.utcnow()
    order = {
        "user_id": ObjectId(user_id),
        "package": package_name,
        "days": days,
        "price": price,
        "start_date": None,   #duyet moi bat dau 
        "end_date": None,
        "created_at": now,
        "status": "pending"   # trang thai cho duyet
    }
    orders_collection.insert_one(order)
    return {"message": "Đơn hàng đã được tạo, xin vui lòng đợi đơn hàng được duyệt"}

def buy_package():
    st.title("Mua gói dịch vụ")
    packages = list(packages_collection.find())
    if not packages:
        st.warning("Hiện chưa có gói dịch vụ nào, vui lòng liên hệ quản trị viên")
        return
    cols = st.columns(len(packages))
    for idx, pkg in enumerate(packages):
        with cols[idx]:
            st.markdown(
                f"""
                <div style="
                    border: 1px solid #ddd; 
                    border-radius: 10px; 
                    padding: 20px; 
                    text-align: center; 
                    box-shadow: 2px 2px 8px rgba(0,0,0,0.1);
                ">
                    <h3>{pkg.get('name', '')}</h3>
                    <p>Thời gian: {pkg.get('days', '')} ngày</p>
                    <p>Giá: {int(pkg.get('price', 0)):,} VNĐ</p>
                </div>
                """, unsafe_allow_html=True
            )

            if st.button(f"Mua {pkg.get('name', '')}", key=str(pkg.get('_id'))):
                user_id = st.session_state.get("user_id")
                if not user_id:
                    st.error("Không tìm thấy id, vui lòng đăng nhập lại.")
                    return

                st.session_state["payment_package"] = {
                    "name": pkg.get("name"),
                    "days": int(pkg.get("days")),
                    "price": int(pkg.get("price")),
                }
                # Luu don hang va chuyen toi trang thanh toan 
                st.session_state["payment_package"] = {
                    "name": pkg.get("name"),
                    "days": int(pkg.get("days")),
                    "price": int(pkg.get("price")),
                    "status": "pending"
                }
                st.session_state["page"] = "payment"
                st.rerun()

