import streamlit as st
import random
import re
import smtplib
from email.mime.text import MIMEText
from db import users_collection  # Kết nối MongoDB

#Kiem tra dinh dang email
def is_valid_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email)

#Gui email xac nhan co ma 
def send_confirmation_email(to_email, code):
    sender_email = "thelistgaming99@gmail.com"  #Dia chi email goc 
    sender_password = "pkbbadvoprsrwirf"        #App password gmail

    msg = MIMEText(f"Mã xác nhận đăng ký của bạn là: {code}")
    msg["Subject"] = "🔐 Mã xác nhận đăng ký BacLab"
    msg["From"] = sender_email
    msg["To"] = to_email

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, to_email, msg.as_string())
        return True
    except Exception as e:
        st.error(f"❌ Gửi email thất bại: {e}")
        return False

#Dang ki tai khoan
def register():
    st.title("🔐 Đăng ký tài khoản BacLab")

    username = st.text_input("👤 Tên đăng nhập", key="register_username")
    password = st.text_input("🔑 Mật khẩu", type="password", key="register_password")
    confirm_password = st.text_input("🔁 Xác nhận mật khẩu", type="password", key="register_confirm_password")
    email = st.text_input("📧 Email", key="register_email")

    if st.button("📨 Gửi mã xác nhận"):
        if not is_valid_email(email):
            st.error("❌ Email không hợp lệ.")
            return

        if not username or not password or not confirm_password:
            st.error("❌ Vui lòng nhập đầy đủ thông tin trước khi gửi mã")
            return

        code = str(random.randint(100000, 999999))
        st.session_state["email_code"] = code
        st.session_state["register_info"] = {
            "username": username,
            "password": password,
            "confirm_password": confirm_password,
            "email": email
        }

        if send_confirmation_email(email, code):
            st.success("✅ Mã xác nhận đã được gửi đến email của bạn")

    verification_code = st.text_input("📥 Nhập mã xác nhận email")

    if st.button("✅ Hoàn tất đăng ký"):
        info = st.session_state.get("register_info", {})

        if not info:
            st.error("❗ Vui lòng gửi mã xác nhận trước.")
            return

        if verification_code != st.session_state.get("email_code", ""):
            st.error("❌ Mã xác nhận không đúng.")
            return

        if info["password"] != info["confirm_password"]:
            st.error("❌ Mật khẩu và xác nhận không khớp")
            return

        if users_collection.find_one({"username": info["username"]}):
            st.error("❌ Tên đăng nhập đã được sử dụng")
            return

        if users_collection.find_one({"email": info["email"]}):
            st.error("❌ Email đã được đăng ký")
            return

        user = {
            "username": info["username"],
            "password": info["password"], 
            "email": info["email"],
            "role": "user",
            "is_premium": False,
            "premium_until": None,
            "free_uses": 5
        }

        users_collection.insert_one(user)
        st.success("🎉 Đăng ký tài khoản thành công! Bạn có thể đăng nhập ngay")
