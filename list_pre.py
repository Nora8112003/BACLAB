import streamlit as st
from db import get_categories, categories_collection

def list_pre():
    st.header("🛡 Biện pháp phòng ngừa vi khuẩn")

    #Kiem tra khoi tao reload key neu chua co 
    if "reload_key" not in st.session_state:
        st.session_state.reload_key = 0

    # Them vi khuan moi 
    with st.expander("➕ Thêm vi khuẩn mới"):
        new_name = st.text_input("Tên vi khuẩn mới:", key="new_name")
        new_pre = st.text_area("Biện pháp phòng ngừa (mỗi dòng là 1 biện pháp):", key="new_pre")
        if st.button("Thêm vi khuẩn"):
            if not new_name.strip():
                st.warning("❗ Vui lòng nhập tên vi khuẩn")
            else:
                existing = categories_collection.find_one({"name": new_name})
                if existing:
                    st.warning("❗ Vi khuẩn này đã tồn tại.")
                else:
                    pre_list = [item.strip() for item in new_pre.split("\n") if item.strip()]
                    categories_collection.insert_one({
                        "name": new_name,
                        "pre": pre_list
                    })
                    st.session_state.reload_key += 1  #Tang reload key de trigger rerun 
                    return

    #Danh sach vi khuan 
    categories = get_categories()
    if not categories:
        st.info("Không có dữ liệu biện pháp")
        return

    for cat in categories:
        name = cat.get("name", "Chưa có tên vi khuẩn")
        prevention_measures = cat.get("pre", [])

        with st.expander(f"🦠 {name}"):
            updated_measures = prevention_measures.copy()

            for i, tip in enumerate(prevention_measures):
                col1, col2 = st.columns([10, 1])
                with col1:
                    updated_tip = st.text_input(f"Biện pháp {i+1} - {name}", tip, key=f"{name}_tip_{i}_{st.session_state.reload_key}")
                    updated_measures[i] = updated_tip.strip()
                with col2:
                    if st.button("Xóa", key=f"delete_{name}_{i}_{st.session_state.reload_key}"):
                        updated_measures.pop(i)
                        categories_collection.update_one(
                            {"name": name},
                            {"$set": {"pre": updated_measures}}
                        )
                        st.session_state.reload_key += 1  # Tăng reload_key để trigger rerun
                        return

            # Them bien phap moi 
            new_tip = st.text_input(f"Biện pháp mới cho {name}")
            if st.button(f"Thêm biện pháp cho {name}", key=f"add_tip_{name}_{st.session_state.reload_key}"):
                if new_tip.strip():
                    updated_measures.append(new_tip.strip())
                    categories_collection.update_one(
                        {"name": name},
                        {"$set": {"pre": updated_measures}}
                    )
                    st.session_state.reload_key += 1 #Tang reload key de trigger rerun 
                    return
                else:
                    st.warning("⚠️ Vui lòng nhập biện pháp mới")

            # Luu thay doi 
            if updated_measures:
                if st.button(f"Lưu thay đổi - {name}", key=f"save_{name}_{st.session_state.reload_key}"):
                    cleaned_list = [item.strip() for item in updated_measures if item.strip()]
                    result = update_category_prevention(name, cleaned_list)
                    if "message" in result:
                        st.session_state.reload_key += 1  # Tăng reload_key để trigger rerun
                        return
                    else:
                        st.warning(f"⚠️ Không có thay đổi hoặc lỗi cập nhật")
            else:
                if st.button(f"🗑️ Xóa vi khuẩn {name}", key=f"del_cat_{name}_{st.session_state.reload_key}"):
                    categories_collection.delete_one({"name": name})
                    st.session_state.reload_key += 1  #Tang reload key de trigger rerun
                    return


def update_category_prevention(name, new_prevention_measures):
    result = categories_collection.update_one(
        {"name": name},
        {"$set": {"pre": new_prevention_measures}}
    )
    if result.modified_count:
        return {"message": "Category updated successfully"}
    return {"error": "Category not found or no changes made"}
