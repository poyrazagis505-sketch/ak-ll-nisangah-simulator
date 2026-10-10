import streamlit as st
import pandas as pd
from magazine_manager import MagazineManager

st.set_page_config(page_title="Mühimmat Takip Sistemi", page_icon="🔫", layout="wide")

st.title("📦 Elektronik Mühimmat Takip Sistemi")
st.caption("Sandbox simülasyonu — şarjör kimliği, fişek takibi ve olay kaydı")

try:
    if "manager" not in st.session_state:
        st.session_state.manager = MagazineManager()

    manager = st.session_state.manager

    with st.sidebar:
        st.header("⚙️ Kontrol Paneli")
        with st.form("add_form"):
            nfc_id = st.text_input("NFC ID", "NFC_001")
            name = st.text_input("Şarjör Adı", "A01")
            capacity = st.number_input("Kapite", min_value=1, max_value=200, value=30)
            submitted = st.form_submit_button("Şarjör Ekle")
            if submitted:
                result = manager.add_magazine(nfc_id, name, capacity)
                if result["success"]:
                    st.success(result["message"])
                    st.rerun()
                else:
                    st.error(result["message"])

        st.divider()

        all_mags = manager.get_all_magazines()
        if all_mags:
            key = st.selectbox("Şarjör seç", list(all_mags.keys()))
            if st.button("Doldur"):
                st.success(manager.reload_magazine(key)["message"])
                st.rerun()
            if st.button("Kaldır"):
                st.warning(manager.remove_magazine(key)["message"])
                st.rerun()

    stats = manager.get_statistics()
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Toplam şarjör", stats["total_magazines"])
    col2.metric("Toplam fişek", stats["total_rounds_initial"])
    col3.metric("Atılan fişek", stats["total_rounds_fired"])
    col4.metric("Kalan fişek", stats["total_rounds_remaining"])

    st.divider()

    all_mags = manager.get_all_magazines()
    if all_mags:
        rows = []
        for nfc_id, mag in all_mags.items():
            rows.append({
                "NFC ID": nfc_id,
                "Şarjör": mag["name"],
                "Kalan": mag["current_rounds"],
                "Toplam": mag["initial_rounds"],
                "Atılan": mag["fired_rounds"],
            })
        st.subheader("📋 Şarjör tablosu")
        st.dataframe(pd.DataFrame(rows), use_container_width=True)

        selected = st.selectbox("Ateş edilecek şarjör", list(all_mags.keys()))
        shots = st.slider("Atış adedi", 1, 10, 1)
        if st.button("💥 Ateş Et"):
            for _ in range(shots):
                result = manager.fire_round(selected)
                if result["success"]:
                    st.success(result["message"])
                else:
                    st.warning(result["message"])
            st.rerun()

        st.subheader("📝 Olay geçmişi")
        events = manager.get_events(limit=20)
        if events:
            event_rows = []
            for e in events:
                event_rows.append({
                    "Zaman": e["timestamp"],
                    "NFC": e["nfc_id"],
                    "Tip": e["type"],
                    "Açıklama": e["description"],
                })
            st.dataframe(pd.DataFrame(event_rows), use_container_width=True)
    else:
        st.info("Henüz şarjör eklenmedi. Sol menüden ekleyin.")

except Exception as e:
    st.error(f"Uygulama çalışırken hata oluştu: {e}")
    st.code(str(e))
