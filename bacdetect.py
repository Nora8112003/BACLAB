import streamlit as st
import cv2
import numpy as np
from PIL import Image
from ultralytics import YOLO
from collections import defaultdict
import pandas as pd
import tempfile
from pymongo import MongoClient
from datetime import datetime

#Thiet lap ket noi MongoDB
MONGO_URI = "mongodb+srv://admin:2qhAarVQ23UzLHhq@cluster0.cxmy1yt.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(MONGO_URI)
db = client["nhandienvikhuan"]
category_collection = db["categories"]
feedback_collection = db["feedbacks"]

#Quan ly mo hinh he thong 
@st.cache_resource
def load_model(model_path):
    return YOLO(model_path)

def get_prevention_measures(label):
    doc = category_collection.find_one({"name": label})
    if doc and "pre" in doc:
        return doc["pre"]
    return []

#Kiem tra quyen truy cap 
def is_premium_user():
    user = st.session_state.get("user", {})
    if user.get("is_premium", False):
        return True
    premium_until = user.get("premium_until")
    if premium_until:
        try:
            expiry = datetime.fromisoformat(premium_until)
            return expiry > datetime.now()
        except:
            pass
    return False

def is_admin_user():
    user = st.session_state.get("user", {})
    return user.get("role") == "admin"

def can_use_free_mode():
    user = st.session_state.get("user", {})
    if user.get("is_premium", False) or user.get("role") == "admin":
        return True
    db_user = db["users"].find_one({"username": user.get("username")})
    return db_user.get("free_uses", 0) > 0 if db_user else False

def decrement_free_use():
    user = st.session_state.get("user", {})
    if not user.get("is_premium", False) and user.get("role") != "admin":
        db["users"].update_one({"username": user["username"]}, {"$inc": {"free_uses": -1}})
        updated_user = db["users"].find_one({"username": user["username"]})
        if updated_user:
            st.session_state["user"]["free_uses"] = updated_user.get("free_uses", 0)

#Ham chinh de streamlit chay 
def main():
    is_admin = is_admin_user()
    is_premium = is_premium_user()
    confirm = st.checkbox("Xác nhận chế độ để tiếp tục")

    model_path = st.session_state.get("model_path", "models/yolov11-custom3/weights/last.pt")
    model = load_model(model_path)

    st.markdown("""
        <h1 style='text-align: center; color: purple; font-size: 40px;'>NHẬN DIỆN VI KHUẨN BẰNG YOLOV11</h1>
    """, unsafe_allow_html=True)

    if is_admin or is_premium:
        option = st.radio("Chọn chế độ nhập liệu", ["Tải ảnh", "Chụp webcam", "Video"])
    else:
        option = "Tải ảnh"
        st.info("⚠ Gói miễn phí chỉ được dùng chế độ 'Tải ảnh'")

    def display_results(image_bgr, results):
        if results is None:
            st.info("Không có kết quả nhận diện")
            return
        confidences = []
        for result in results:
            for box in result.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                label = model.names[int(box.cls[0])]
                confidence = box.conf[0]
                confidences.append(float(confidence))
                cv2.rectangle(image_bgr, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(image_bgr, f"{label} {confidence:.2f}", (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.9, (36, 255, 12), 2)
        image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
        st.image(image_rgb, caption='Kết quả nhận diện')

        if confidences:
            min_conf = round(float(min(confidences)) * 100, 2)
            st.markdown(f"#### 📉 Chỉ số tự tin thấp nhất: **{min_conf}%**")
            if min_conf < 50:
                st.warning("⚠ Có đối tượng với độ tự tin thấp. Vui lòng gửi phản hồi để cải thiện hệ thống.")
                show_feedback_form(image_bgr, model, min_conf)
            else:
                with st.expander("✉️ Gửi phản hồi tự nguyện"):
                    show_feedback_form(image_bgr, model, min_conf)
        else:
            st.info("❗ Không phát hiện vi khuẩn nào")

    def show_feedback_form(image_bgr, model, min_conf):
        wrong_label = st.text_input("Nhập tên vi khuẩn bị nhận sai (nếu có)")
        user_comment = st.text_area("Ý kiến phản hồi")
        send_btn = st.button("Gửi phản hồi")
        if send_btn:
            user = st.session_state.get("user", {})
            image_for_feedback = image_bgr.copy()
            save_feedback(user, user_comment, Image.fromarray(image_for_feedback), wrong_label, min_conf)
            st.success("✔ Phản hồi của bạn đã được ghi nhận. Cảm ơn bạn!")

    def save_feedback(user, message, image=None, wrong_labels=None, min_conf=None):
        import base64
        import io
        feedback_doc = {
            "user": user.get("username", "unknown"),
            "message": message,
            "timestamp": datetime.now(),
        }
        if image:
            img_bytes = io.BytesIO()
            image.save(img_bytes, format='PNG')
            img_base64 = base64.b64encode(img_bytes.getvalue()).decode()
            feedback_doc["image_base64"] = img_base64
        if wrong_labels:
            feedback_doc["wrong_labels"] = wrong_labels
        if min_conf is not None:
            feedback_doc["min_confidence"] = min_conf
        feedback_collection.insert_one(feedback_doc)

    def statistics_and_recommendations(results):
        if not results:
            st.info("Không có dữ liệu để thống kê")
            return None
        st.subheader("Thống kê nhận diện:")
        label_data = defaultdict(list)
        for result in results:
            for box in result.boxes:
                label = model.names[int(box.cls[0])]
                confidence = float(box.conf[0])
                label_data[label].append(confidence)
        df_data = {
            "Vi khuẩn": [],
            "Số lượng": [],
            "Độ chính xác trung bình (%)": [],
        }
        for label, confs in label_data.items():
            df_data["Vi khuẩn"].append(label)
            df_data["Số lượng"].append(len(confs))
            avg_conf = round(np.mean(confs) * 100, 2)
            df_data["Độ chính xác trung bình (%)"].append(avg_conf)

        df_stats = pd.DataFrame(df_data)
        st.dataframe(df_stats)

        st.subheader("Biện pháp phòng chống chi tiết:")
        prevention_data = {
            "Vi khuẩn": [],
            "Biện pháp phòng chống": []
        }
        for label in label_data.keys():
            preventions = get_prevention_measures(label)
            if preventions:
                st.markdown(f"### {label}:")
                for item in preventions:
                    st.markdown(f"- {item}")
                prevention_data["Vi khuẩn"].append(label)
                prevention_data["Biện pháp phòng chống"].append("\n".join(preventions))
            else:
                st.warning(f"⚠️ Chưa có biện pháp cho: {label}")
                prevention_data["Vi khuẩn"].append(label)
                prevention_data["Biện pháp phòng chống"].append("Chưa có biện pháp")

        df_preventions = pd.DataFrame(prevention_data)

# Nut xuat file thong ke 
        import io
        towrite_stats = io.BytesIO()
        df_stats.to_excel(towrite_stats, index=False, engine='openpyxl')
        towrite_stats.seek(0)
        st.download_button(
            label="📥 Xuất thống kê vi khuẩn ra file Excel",
            data=towrite_stats,
            file_name="thong_ke_vikhuan.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

# Nut xuat file bien phap phong chong 
        towrite_preventions = io.BytesIO()
        df_preventions.to_excel(towrite_preventions, index=False, engine='openpyxl')
        towrite_preventions.seek(0)
        st.download_button(
            label="📥 Xuất biện pháp phòng chống ra file Excel",
            data=towrite_preventions,
            file_name="bien_phap_phong_chong.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        st.success("🎉 Cảm ơn bạn đã sử dụng ứng dụng của chúng tôi!")
        return df_stats
#Xu ly anh 
    if confirm:
        user = st.session_state.get("user", {})
        if not is_admin and not is_premium:
            db_user = db["users"].find_one({"username": user.get("username")})
            remaining = db_user.get("free_uses", 0) if db_user else 0
            st.info(f"🔄 Bạn còn {remaining} lượt sử dụng miễn phí")
            if remaining <= 0:
                st.error("⚠️ Bạn đã hết lượt sử dụng miễn phí. Vui lòng nâng cấp lên gói Premium để tiếp tục.")
                st.stop()
        results = None
        if option == "Tải ảnh":
            uploaded_file = st.file_uploader("Chọn một ảnh để nhận diện", type=["jpg", "jpeg", "png"])
            if uploaded_file:
                image = Image.open(uploaded_file)
                image_np = np.array(image)
                image_bgr = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)
                results = model.predict(image_bgr)
                display_results(image_bgr, results)
                decrement_free_use()
            if is_premium or is_admin:
                statistics_and_recommendations(results)
            else:
                st.info("❗ Vui lòng nâng cấp lên gói Premium để xem thống kê và biện pháp phòng ngừa")

        elif option == "Chụp webcam":
            if not (is_admin or is_premium):
                st.warning("⚠️ Chức năng này chỉ dành cho người dùng Premium hoặc Admin")
                return
            picture = st.camera_input("Chụp ảnh từ webcam")
            if picture:
                image = Image.open(picture)
                image_np = np.array(image)
                image_bgr = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)
                results = model.predict(image_bgr)
                display_results(image_bgr, results)
                statistics_and_recommendations(results)

        elif option == "Video":
            if not (is_admin or is_premium):
                st.warning("⚠️ Chức năng này chỉ dành cho người dùng Premium hoặc Admin")
                return
            video_file = st.file_uploader("Tải video để nhận diện", type=["mp4", "avi", "mov"])
            if video_file:
                tfile = tempfile.NamedTemporaryFile(delete=False)
                tfile.write(video_file.read())
                cap = cv2.VideoCapture(tfile.name)
                stframe = st.empty()
                frame_idx = 0
                all_results = []
                while cap.isOpened():
                    ret, frame = cap.read()
                    if not ret or frame_idx > 300:
                        break
                    frame_idx += 1
                    results = model.predict(frame)
                    all_results.extend(results)
                    for result in results:
                        for box in result.boxes:
                            x1, y1, x2, y2 = map(int, box.xyxy[0])
                            label = model.names[int(box.cls[0])]
                            confidence = box.conf[0]
                            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                            cv2.putText(frame, f"{label} {confidence:.2f}", (x1, y1 - 10),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (36, 255, 12), 2)
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    stframe.image(frame_rgb, caption=f"Frame {frame_idx}", use_container_width=True)
                cap.release()
                statistics_and_recommendations(all_results)
    else:
        st.warning("⚠️ Vui lòng xác nhận chế độ trước khi tiếp tục")
