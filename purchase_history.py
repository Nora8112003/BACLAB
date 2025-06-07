import streamlit as st
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime

MONGO_URI = "mongodb+srv://admin:2qhAarVQ23UzLHhq@cluster0.cxmy1yt.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(MONGO_URI)
db = client['nhandienvikhuan']
orders_collection = db['orders']

def format_date(dt):
    if isinstance(dt, datetime):
        return dt.strftime("%d/%m/%Y %H:%M")
    return "Chưa cập nhật"

def format_currency(amount):
    try:
        return f"{int(amount):,} VNĐ"
    except:
        return "N/A"

def show_purchase_history(user_id):
    st.subheader("🧾 Lịch sử giao dịch")

    try:
        orders = list(orders_collection.find(
            {"user_id": ObjectId(user_id)}
        ).sort("created_at", -1))  #Sap xep theo thoi gian moi nhat 

        if orders:
            for order in orders:
                st.markdown(f"""
                    <div style="border:1px solid #ccc; border-radius:10px; padding:15px; margin-bottom:10px;">
                        <b>🎁 Gói:</b> {order.get("package", "Không rõ")}<br>
                        📅 <b>Thời hạn:</b> {order.get("days", "N/A")} ngày<br>
                        💵 <b>Giá:</b> {format_currency(order.get("price", 0))}<br>
                        🕒 <b>Ngày tạo:</b> {format_date(order.get("created_at"))}<br>
                        ⏳ <b>Hiệu lực:</b> {format_date(order.get("start_date"))} - {format_date(order.get("end_date"))}<br>
                        ✅ <b>Trạng thái:</b> {order.get("status", "pending").capitalize()}
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.info("📭 Bạn chưa có giao dịch nào.")
    except Exception as e:
        st.error(f"Đã xảy ra lỗi khi truy vấn lịch sử giao dịch: {str(e)}")
