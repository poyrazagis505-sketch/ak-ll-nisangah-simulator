import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
from magazine_manager import MagazineManager

# Sayfa ayarları
st.set_page_config(
    page_title="📦 Mühimmat Takip Sistemi",
    page_icon="🔫",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Tema
st.markdown("""
<style>
    .main {
        padding: 0rem 1rem;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
    }
    [data-testid="stSidebar"] {
        background-color: #0e1117;
    }
</style>
""", unsafe_allow_html=True)

# Session state başlatma
if "magazine_manager" not in st.session_state:
    st.session_state.magazine_manager = MagazineManager()

mm = st.session_state.magazine_manager

# Header
st.markdown("# 📦 Elektronik Mühimmat Takip Sistemi")
st.markdown("### Şarjör Kimliği ve Olay Kaydı Simülasyonu")
st.divider()

# Sidebar - Kontrol Paneli
with st.sidebar:
    st.markdown("## ⚙️ Kontrol Paneli")
    st.divider()
    
    tab1, tab2, tab3 = st.tabs(["➕ Şarjör Ekle", "🗑️ Yönet", "📊 İstatistik"])
    
    with tab1:
        st.subheader("Yeni Şarjör Ekle")
        with st.form("add_magazine_form"):
            nfc_id = st.text_input(
                "NFC ID",
                placeholder="Örn: NFC_001",
                help="Şarjörün benzersiz NFC kimliği"
            )
            
            mag_name = st.text_input(
                "Şarjör Adı",
                placeholder="Örn: A Şarjörü",
                help="İnsan tarafından okunabilir ad"
            )
            
            initial_rounds = st.number_input(
                "İlk Fişek Sayısı",
                min_value=1,
                max_value=1000,
                value=30,
                step=1,
                help="Şarjörün toplam kapasitesi"
            )
            
            submitted = st.form_submit_button("✅ Şarjörü Ekle", use_container_width=True)
            
            if submitted:
                if not nfc_id or not mag_name:
                    st.error("Lütfen tüm alanları doldurun!")
                else:
                    result = mm.add_magazine(nfc_id, mag_name, initial_rounds)
                    if result["success"]:
                        st.success(result["message"])
                        st.rerun()
                    else:
                        st.error(result["message"])
    
    with tab2:
        st.subheader("Şarjörleri Yönet")
        
        all_mags = mm.get_all_magazines()
        
        if all_mags:
            selected_mag = st.selectbox(
                "Şarjör Seç",
                options=list(all_mags.keys()),
                format_func=lambda x: f"{all_mags[x]['name']} ({x})"
            )
            
            if selected_mag:
                mag = all_mags[selected_mag]
                
                st.metric("Mevcut Fişek", mag["current_rounds"], f"/ {mag['initial_rounds']}")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("🔄 Doldur", use_container_width=True):
                        result = mm.reload_magazine(selected_mag)
                        st.success(result["message"])
                        st.rerun()
                
                with col2:
                    if st.button("🗑️ Kaldır", use_container_width=True, type="secondary"):
                        result = mm.remove_magazine(selected_mag)
                        st.warning(result["message"])
                        st.rerun()
        else:
            st.info("Henüz şarjör eklenmedi.")
    
    with tab3:
        stats = mm.get_statistics()
        
        st.metric("Toplam Şarjör", stats["total_magazines"])
        st.metric("Toplam Fişek", stats["total_rounds_initial"])
        st.metric("Atılan Fişek", stats["total_rounds_fired"])
        st.metric("Kalan Fişek", stats["total_rounds_remaining"])
        
        if st.button("🧹 Tüm Verileri Sil", use_container_width=True, type="secondary"):
            mm.clear_all_data()
            st.warning("Tüm veriler silindi!")
            st.rerun()

# Ana İçerik
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📋 Şarjör Tablosu")
    
    all_mags = mm.get_all_magazines()
    
    if all_mags:
        # DataFrame oluştur
        mag_data = []
        for nfc_id, mag in all_mags.items():
            mag_data.append({
                "🔖 NFC ID": nfc_id,
                "📦 Şarjör Adı": mag["name"],
                "🔫 Fişek": f"{mag['current_rounds']}/{mag['initial_rounds']}",
                "💥 Atılan": mag["fired_rounds"],
                "📅 Eklenme": mag["created_at"][:10],
                "🕐 Son Kullanım": mag["last_used"][:10] if mag["last_used"] else "-"
            })
        
        df = pd.DataFrame(mag_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("Henüz şarjör eklenmedi. Sidebar'dan yeni şarjör ekleyin.")

with col2:
    st.subheader("📊 Hızlı İstatistik")
    stats = mm.get_statistics()
    
    st.metric("Toplam Şarjör", stats["total_magazines"])
    st.metric("Toplam Fişek", stats["total_rounds_initial"])
    st.metric("Atılan Fişek", stats["total_rounds_fired"])
    st.metric("Kalan Fişek", stats["total_rounds_remaining"])
    
    if stats["uncertain_events"] > 0:
        st.metric("⚠️ Belirsiz Olay", stats["uncertain_events"], delta=None)

st.divider()

# Ateş Simülasyonu
st.subheader("🎯 Ateş Simülasyonu")

all_mags = mm.get_all_magazines()

if all_mags:
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        selected_mag_for_fire = st.selectbox(
            "Hangi şarjörden ateş edilsin?",
            options=list(all_mags.keys()),
            format_func=lambda x: f"{all_mags[x]['name']} ({all_mags[x]['current_rounds']}/{all_mags[x]['initial_rounds']} fişek)"
        )
    
    with col2:
        num_rounds = st.number_input(
            "Kaç fişek ateş edilsin?",
            min_value=1,
            max_value=10,
            value=1
        )
    
    with col3:
        if st.button("💥 ATEŞ ET", use_container_width=True, type="primary"):
            for i in range(num_rounds):
                result = mm.fire_round(selected_mag_for_fire)
                if result["success"]:
                    st.success(f"✅ {i+1}. atış: {result['message']}")
                else:
                    if result.get("is_uncertain"):
                        st.warning(f"⚠️ {i+1}. atış belirsiz: {result['message']}")
                    else:
                        st.error(f"❌ {i+1}. atış başarısız: {result['message']}")
            st.rerun()
else:
    st.info("Ateş etmek için önce bir şarjör ekleyin.")

st.divider()

# Grafik Gösterimler
st.subheader("📈 Analiz ve Grafikler")

if all_mags:
    col1, col2 = st.columns(2)
    
    with col1:
        # Şarjör durumu pie chart
        mag_names = []
        remaining_rounds = []
        
        for mag in all_mags.values():
            mag_names.append(mag["name"])
            remaining_rounds.append(mag["current_rounds"])
        
        fig_pie = go.Figure(data=[
            go.Pie(
                labels=mag_names,
                values=remaining_rounds,
                marker=dict(line=dict(color='white', width=2)),
                textposition='auto'
            )
        ])
        fig_pie.update_layout(
            title="Şarjörlerdeki Kalan Fişek Oranı",
            height=400
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        # Kullanım durumu bar chart
        mag_data_for_chart = []
        for mag in all_mags.values():
            mag_data_for_chart.append({
                "Şarjör": mag["name"],
                "Atılan": mag["fired_rounds"],
                "Kalan": mag["current_rounds"]
            })
        
        df_chart = pd.DataFrame(mag_data_for_chart)
        
        fig_bar = go.Figure(data=[
            go.Bar(name='Atılan', x=df_chart['Şarjör'], y=df_chart['Atılan'], marker_color='#ff6b6b'),
            go.Bar(name='Kalan', x=df_chart['Şarjör'], y=df_chart['Kalan'], marker_color='#51cf66')
        ])
        fig_bar.update_layout(
            barmode='stack',
            title="Şarjör Durumu",
            height=400,
            xaxis_title="Şarjör",
            yaxis_title="Fişek Sayısı"
        )
        st.plotly_chart(fig_bar, use_container_width=True)

st.divider()

# Olay Geçmişi
st.subheader("📝 Olay Geçmişi")

col1, col2 = st.columns([2, 1])

with col1:
    filter_type = st.selectbox(
        "Filtre",
        ["Tümü", "Başarılı Atışlar", "Başarısız Atışlar", "Belirsiz Olaylar", "Şarjör İşlemleri"]
    )

with col2:
    event_limit = st.number_input("Gösterilecek olay sayısı", min_value=10, max_value=500, value=50)

events = mm.get_events(limit=event_limit)

if events:
    filtered_events = events
    
    if filter_type == "Başarılı Atışlar":
        filtered_events = [e for e in events if e["type"] == "FIRE_SUCCESS"]
    elif filter_type == "Başarısız Atışlar":
        filtered_events = [e for e in events if "FIRE_FAILED" in e["type"]]
    elif filter_type == "Belirsiz Olaylar":
        filtered_events = [e for e in events if e.get("is_uncertain")]
    elif filter_type == "Şarjör İşlemleri":
        filtered_events = [e for e in events if "MAGAZINE" in e["type"]]
    
    # Event tablosu
    event_data = []
    for event in filtered_events:
        event_type_icon = {
            "FIRE_SUCCESS": "💥",
            "FIRE_FAILED_EMPTY": "⚠️",
            "MAGAZINE_ADDED": "➕",
            "MAGAZINE_REMOVED": "🗑️",
            "MAGAZINE_RELOADED": "🔄"
        }.get(event["type"], "📌")
        
        uncertain_mark = "⚠️ BELİRSİZ" if event.get("is_uncertain") else ""
        
        event_data.append({
            "⏰ Zaman": event["timestamp"][5:16],  # YYYY-MM-DD HH:MM
            "🔖 NFC ID": event["nfc_id"],
            "📌 Olay": f"{event_type_icon} {event['type']}",
            "📝 Açıklama": event["description"],
            "⚠️ Durum": uncertain_mark
        })
    
    df_events = pd.DataFrame(event_data)
    st.dataframe(df_events, use_container_width=True, hide_index=True)
else:
    st.info("Henüz olay kaydedilmedi.")

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: gray; font-size: 12px;'>
    <p>TÜBİTAK 2209-A/B | Elektronik Mühimmat Takip ve Gösterge Sistemi</p>
    <p>Sandbox Simülasyon Prototipi v1.0</p>
</div>
""", unsafe_allow_html=True)
