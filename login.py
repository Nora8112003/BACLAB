import streamlit as st
from db import users_collection

def login():
    st.title("🔐 Đăng nhập")

    username = st.text_input("Tên đăng nhập", key="login_username")
    password = st.text_input("Mật khẩu", type="password", key="login_password")
    
    if st.button("Đăng nhập", key="login_button"):
        user = users_collection.find_one({"username": username})
        if user:
            if password == user["password"]:
                user_info = {
                    "username": user["username"],
                    "email": user.get("email", ""),
                    "role": user.get("role", "user"),
                    "is_premium": user.get("is_premium", False),
                    "premium_until": user.get("premium_until", None),
                    "id": str(user["_id"]),
                }
                return user_info  #Tra ve user info
            else:
                st.error("❌ Sai mật khẩu.")
        else:
            st.error("❌ Tài khoản không tồn tại.")
    
    return None  #Dang nhap khong thanh cong thi tra ve None 
