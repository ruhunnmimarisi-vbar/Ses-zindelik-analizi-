import streamlit as st
import librosa
import numpy as np
import io
import random

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="VBAR | Mistik Kristal", layout="centered")

# --- ESTETİK VE ÇERÇEVE (CSS) ---
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #1a0b1c 0%, #2c1630 100%);
        color: #f8bbd0;
        border: 15px solid #4a154b;
        border-radius: 20px;
        padding: 20px;
    }
    .crystal-hero {
        text-align: center;
        font-size: 120px;
        margin: 20px 0;
        filter: drop-shadow(0 0 20px #ff80ab);
    }
    .vip-title {
        color: #ff80ab;
        font-size: 32px;
        font-weight: bold;
        text-align: center;
        text-shadow: 2px 2px 4px #000;
    }
    div.stButton > button {
        background-color: #4a154b !important;
        color: #ff80ab !important;
        border: 2px solid #ff80ab !important;
        border-radius: 15px !important;
        width: 100%;
        font-weight: bold;
    }
    .result-card {
        background: rgba(255, 255, 255, 0.05);
        border: 2px solid #ff80ab;
        padding: 20px;
        border-radius: 15px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# --- HAFIZA ---
if "history" not in st.session_state: st.session_state.history = []

# --- KRİSTAL VE DUYGU ANALİZ MANTIĞI ---
KRISTALLER = {
    "Kök": ("🔴", "Kırmızı Akik", "Topraklanma ve Güven"),
    "Sakral": ("🟠", "Kaplan Gözü", "Yaratıcılık ve Akış"),
    "Solar": ("🟡", "Kehribar", "Özgüven ve İrade"),
    "Kalp": ("🟢", "Yeşim", "Sevgi ve Şifa"),
    "Boğaz": ("🩵", "Akuamarin", "İfade ve Gerçeklik"),
    "Üçüncü Göz": ("🔵", "Lapis Lazuli", "Sezgi ve Bilgelik"),
    "Tepe": ("🟣", "Ametist", "Aydınlanma ve Ruh")
}

# --- KARŞILAMA EKRANI ---
st.markdown('<div class="crystal-hero">🔮</div>', unsafe_allow_html=True)
st.markdown('<div class="vip-title">VBAR Mistik Analiz</div>', unsafe_allow_html=True)
st.write("Sesinle ruhunun kristalini keşfet...")

# --- GİRDİLER ---
duygu_durumu = st.selectbox("Şu anki hissin nedir?", ["Huzurlu", "Kaygılı", "Heyecanlı", "Yorgun", "İlham Dolu"])
audio_input = st.audio_input("Sesini Kaydet:")

if audio_input and st.button("✨ Analize Başla"):
    # Basit bir analiz simülasyonu
    kristal_key = random.choice(list(KRISTALLER.keys()))
    kristal_data = KRISTALLER[kristal_key]
    
    sonuc = {
        "id": random.randint(1000, 9999),
        "duygu": duygu_durumu,
        "kristal": kristal_data[1],
        "icon": kristal_data[0],
        "mesaj": f"{kristal_data[2]} frekansındasın. {duygu_durumu} halin, bu kristalle birleşerek enerjini dengeleyecek."
    }
    st.session_state.current = sonuc

# --- SONUÇ EKRANI ---
if "current" in st.session_state:
    res = st.session_state.current
    st.markdown(f"""
    <div class="result-card">
        <h3>{res['icon']} {res['kristal']}</h3>
        <p><b>Duygu Durumun:</b> {res['duygu']}</p>
        <p>{res['mesaj']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("💾 Kaydı Hafızaya Al"):
        st.session_state.history.append(res)
        st.success("Hafızaya eklendi!")

# --- GEÇMİŞ ---
if st.session_state.history:
    st.markdown("---")
    st.subheader("📜 Mistik Geçmişin")
    for item in reversed(st.session_state.history):
        st.write(f"{item['icon']} {item['kristal']} - {item['duygu']}")
        if st.button(f"🗑️ Sil #{item['id']}", key=f"del_{item['id']}"):
            st.session_state.history.remove(item)
            st.rerun()
