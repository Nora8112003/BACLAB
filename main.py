import streamlit as st
import importlib
import base64
from login import login
from register import register
from developer import developer
from home import home
from admin_orders import review_orders
from admin_system import system_info 
import streamlit.components.v1 as components
from streamlit_javascript import st_javascript
from db import update_password, verify_password  
import base64
import streamlit as st

import os
import subprocess
import sys

def install_torch_cpu():
    subprocess.check_call([sys.executable, "-m", "pip", "install", 
                           "torch", "torchvision", "torchaudio", 
                           "--index-url", "https://download.pytorch.org/whl/cpu"])

try:
    import torch
except ImportError:
    install_torch_cpu()

def img_to_base64_str(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

#Ho so nguoi dung
    
def profile_page():
    st.title("👤 Hồ sơ người dùng")
    user_info = st.session_state.get("user", {})

    # Hien thi avatar
    avatar_url = user_info.get("avatar")
    if avatar_url:
        st.image(avatar_url, width=100)

    with st.form("edit_profile_form"):
        new_username = st.text_input("Tên đăng nhập", user_info.get("username", ""))
        new_email = st.text_input("Email", user_info.get("email", ""))
        uploaded_avatar = st.file_uploader("Ảnh đại diện", type=["png", "jpg", "jpeg"])

        #Truong cap nhat mat khau 
        st.markdown("### 🔐 Đổi mật khẩu")
        current_password = st.text_input("Mật khẩu hiện tại", type="password")
        new_password = st.text_input("Mật khẩu mới", type="password")
        confirm_password = st.text_input("Xác nhận mật khẩu mới", type="password")

        submitted = st.form_submit_button("💾 Cập nhật")
        if submitted:
            # Cap nhat thong tin va email
            st.session_state['user']['username'] = new_username
            st.session_state['user']['email'] = new_email

            if uploaded_avatar:
                avatar_data = base64.b64encode(uploaded_avatar.read()).decode()
                avatar_base64 = f"data:image/png;base64,{avatar_data}"
                st.session_state['user']['avatar'] = avatar_base64

            #Xu ly cap nhat mat khau 
            if current_password or new_password or confirm_password:
                if not (current_password and new_password and confirm_password):
                    st.warning("⚠️ Vui lòng điền đầy đủ tất cả các trường mật khẩu.")
                elif new_password != confirm_password:
                    st.error("❌ Mật khẩu mới và xác nhận không khớp.")
                elif not verify_password(st.session_state['user']['id'], current_password):
                    st.error("❌ Mật khẩu hiện tại không đúng.")
                else:
                    update_password(st.session_state['user']['id'], new_password)
                    st.success("🔑 Mật khẩu đã được cập nhật.")

            st.success("✅ Hồ sơ đã được cập nhật.")
            st.rerun()

    st.markdown("---")
    st.write(f"**Premium:** {'Có' if user_info.get('is_premium') else 'Không'}")
    if user_info.get("premium_until"):
        st.write(f"**Hết hạn Premium:** {user_info['premium_until']}")
    st.write(f"**Lượt dùng miễn phí còn lại:** {user_info.get('free_uses', 0)}")

    if st.button("⬅️ Quay lại"):
        st.session_state["page"] = "main"
        st.rerun()


def main_page():
    st.set_page_config(page_title="BacLab", page_icon="🦠", layout="wide")

    if 'authenticated' not in st.session_state:
        st.session_state['authenticated'] = False
    if 'username' not in st.session_state:
        st.session_state['username'] = None
    if 'role' not in st.session_state:
        st.session_state['role'] = None
    if 'user_id' not in st.session_state:
        st.session_state['user_id'] = None
    if 'current_page' not in st.session_state:
        st.session_state['current_page'] = "Giới thiệu"
    if 'page' not in st.session_state:
        st.session_state['page'] = "main"
    if 'user' not in st.session_state:
        st.session_state['user'] = None

    logo_base64 = img_to_base64_str("assets/logo.png")
    st.markdown(f"""
    <div style="display:flex; align-items:center; cursor:pointer;">
        <a href="?page=home" style="display:flex; align-items:center; text-decoration:none; color: inherit;">
            <img src="data:image/png;base64,{logo_base64}" width="100" style="margin-right: 10px;" />
            <h1 style="margin:0; font-size: 60px;">BACLAB</h1>
        </a>
    </div>
    """, unsafe_allow_html=True)

    #Lay query params de chuyen trang 
    query_params = st.query_params
    if "page" in query_params:
        page = query_params["page"][0]
        if page == "home":
            st.session_state["current_page"] = "Giới thiệu"
            # Xóa param page để tránh lặp lại
            st.query_params()
            st.rerun()

    if st.session_state['authenticated']:
        user = st.session_state.get("user")
        if isinstance(user, dict):
            username = user.get("username", "Người dùng")
        else:
            username = "Người dùng"

        col1, col2, col3 = st.columns([6, 0.7, 1])
        with col1:
            user = st.session_state.get("user", {})
            avatar = user.get("avatar", None)
            if avatar:
                st.markdown(f"""
                <div style='display: flex; align-items: center; gap: 10px; font-size: 18px;'>
                    👋 Xin chào,
                    <img src="{avatar}" width="32" height="32" style="border-radius: 50%; object-fit: cover;" />
                    <b>{username}</b>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style='font-size: 18px;'>👋 Hello, <b>{username}</b></div>
                """, unsafe_allow_html=True)
        with col2:
            if st.session_state.get("role") == "user":
                if st.button("👤 Hồ sơ"):
                    st.session_state["page"] = "profile"
                    st.rerun()
        with col3:
            if st.button("🚪 Đăng xuất"):
                st.session_state['authenticated'] = False
                st.session_state['user'] = None
                st.session_state['username'] = None
                st.session_state['role'] = None
                st.session_state['user_id'] = None
                st.session_state['current_page'] = "Giới thiệu"
                st.session_state['page'] = "main"
                st.rerun()


    if st.session_state['page'] == "payment":
        import payment
        payment.show_payment()

    if st.session_state['authenticated']:
        if st.session_state['role'] == 'admin':
            tabs = ["Giới thiệu", "Nhà phát triển", "Nhận diện vi khuẩn"]
        elif st.session_state['role'] == 'user':
            tabs = ["Giới thiệu", "Nhận diện vi khuẩn", "Mua gói", "Lịch sử giao dịch"]
        else:
            tabs = ["Giới thiệu", "Nhận diện vi khuẩn"]
    else:
        tabs = ["Giới thiệu", "Đăng nhập", "Đăng ký"]

    try:
        current_tab_index = tabs.index(st.session_state['current_page'])
    except ValueError:
        current_tab_index = 0
        st.session_state['current_page'] = tabs[0]

    selected_tabs = st.tabs(tabs)

    for i, tab_name in enumerate(tabs):
        with selected_tabs[i]:
            if tab_name == "Đăng nhập":
                user_info = login()
                if user_info:
                    st.session_state["authenticated"] = True
                    st.session_state["user"] = user_info
                    st.session_state["username"] = user_info.get("username")
                    st.session_state["role"] = user_info.get("role")
                    st.session_state["user_id"] = user_info.get("id")
                    st.session_state["current_page"] = "Giới thiệu"
                    st.rerun()

            elif tab_name == "Đăng ký":
                register()

            elif tab_name == "Giới thiệu":
                home()

            elif tab_name == "Nhận diện vi khuẩn":
                if st.session_state['authenticated']:
                    bacdetect = importlib.import_module("bacdetect")
                    bacdetect.main()
                else:
                    st.warning("⚠️ Vui lòng đăng nhập để sử dụng tính năng này.")

            elif tab_name == "Lịch sử giao dịch":
                if st.session_state['authenticated'] and st.session_state['role'] == "user":
                    from purchase_history import show_purchase_history
                    show_purchase_history(st.session_state["user_id"])
                else:
                    st.warning("⚠️ Vui lòng đăng nhập để sử dụng tính năng này.")

            elif tab_name == "Nhà phát triển":
                if st.session_state["authenticated"] and st.session_state["role"] == "admin":
                    dev_menu = st.radio("👨‍💻 Quản trị viên", [
                        "📋 Người dùng",
                        "🛡️ Biện pháp vi khuẩn",
                        "💳 Người dùng đã mua gói",
                        "📬 Phản hồi người dùng",
                        "🛠 Quản lý đơn hàng",
                        "🗃 Quản lý hệ thống"
                    ])

                    if dev_menu == "📋 Người dùng":
                        from list_user import list_user
                        list_user()
                    elif dev_menu == "💳 Người dùng đã mua gói":
                        from list_paid_users import list_paid_users
                        list_paid_users()
                    elif dev_menu == "🛡️ Biện pháp vi khuẩn":
                        from list_pre import list_pre
                        list_pre()
                    elif dev_menu == "📬 Phản hồi người dùng":
                        from list_feedback import list_feedback
                        list_feedback()
                    elif dev_menu == "🛠 Quản lý đơn hàng":
                        review_orders()
                    elif dev_menu == "🗃 Quản lý hệ thống":
                        system_info()
                else:
                    st.error("⚠️ Chỉ quản trị viên được truy cập.")

            elif tab_name == "Mua gói":
                if st.session_state['authenticated'] and st.session_state['role'] == "user":
                    import order
                    order.buy_package()
                else:
                    st.warning("⚠️ Vui lòng đăng nhập với tài khoản khách hàng để mua gói.")

    if tabs[current_tab_index] != st.session_state["current_page"]:
        st.session_state["current_page"] = tabs[current_tab_index]
        st.rerun()

    # Footer
    st.markdown("""
        <hr style="margin-top: 50px; margin-bottom: 10px;">
        <div style='text-align: center; font-size: 15px; color: gray;'>
            📞 <b>Liên hệ:</b> <a href="tel:0335526732" style="text-decoration: none; color: #4F8BF9;">0335526732</a> |  
            💬 <a href="https://zalo.me/0335526732" target="_blank" style="text-decoration: none; color: #0084FF;">Zalo</a> |  
            🌐 <a href="https://www.facebook.com/Noranyanya/" target="_blank" style="text-decoration: none; color: #4267B2;">Facebook</a><br>
            <small>© 2025 BacLab. All rights reserved.</small>
        </div>
    """, unsafe_allow_html=True)


def main():
    if 'page' not in st.session_state:
        st.session_state['page'] = "main"

    if st.session_state['page'] == "profile":
        profile_page()
    else:
        main_page()

if __name__ == "__main__":
    if "current_page" not in st.session_state:
        st.session_state["current_page"] = "Giới thiệu"
    if "page" not in st.session_state:
        st.session_state["page"] = "main"

    if st.session_state["page"] == "profile":
        profile_page()
    else:
        main_page()

