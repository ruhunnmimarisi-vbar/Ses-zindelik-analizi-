import streamlit as st
import librosa
import numpy as np
import io
import random

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="VBAR | Mistik Kristal Frekans", layout="centered")

# --- GELİŞMİŞ ESTETİK VE ÇERÇEVE (CSS) ---
st.markdown("""
<style>
    .stApp {
        background: radial-gradient(circle at center, #2c1630 0%, #1a0b1c 100%);
        color: #ff80ab;
        border: 4px solid #ff80ab;
        border-radius: 25px;
        padding: 25px;
        box-shadow: 0 0 30px rgba(255, 128, 171, 0.2);
    }
    .crystal-hero {
        text-align: center;
        font-size: 110px;
        margin: 10px 0;
        filter: drop-shadow(0 0 25px #ff80ab);
    }
    .vip-title {
        color: #ff80ab;
        font-size: 32px;
        font-weight: 800;
        text-align: center;
        letter-spacing: 2px;
        text-shadow: 0 0 10px rgba(255, 128, 171, 0.5);
        margin-bottom: 5px;
    }
    .vip-subtitle {
        color: #f8bbd0;
        text-align: center;
        font-size: 1.1rem;
        margin-bottom: 25px;
        font-style: italic;
    }
    div.stButton > button {
        background: linear-gradient(135deg, #4a154b 0%, #2c1630 100%) !important;
        color: #ff80ab !important;
        border: 2px solid #ff80ab !important;
        border-radius: 20px !important;
        width: 100%;
        font-weight: bold;
        padding: 10px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        transition: 0.3s;
    }
    div.stButton > button:hover {
        background: #ff80ab !important;
        color: #1a0b1c !important;
    }
    .result-card {
        background: rgba(255, 128, 171, 0.05);
        border: 2px solid #ff80ab;
        padding: 20px;
        border-radius: 20px;
        margin: 15px 0;
        box-shadow: inset 0 0 15px rgba(255, 128, 171, 0.1);
    }
    label, .stSelectbox, .stAudioInput {
        color: #ff80ab !important;
    }
</style>
""", unsafe_allow_html=True)

# --- HAFIZA ---
if "history" not in st.session_state: st.session_state.history = []
if "current" not in st.session_state: st.session_state.current = None

# --- ÇAKRA VE FREKANS EŞLEŞTİRMELERİ ---
def get_crystal_by_pitch(pitch):
    if pitch < 130:
        return ("🔴", "Kırmızı Akik", "Kök Çakra", "Topraklanma ve Güven")
    elif pitch < 170:
        return ("🟠", "Kaplan Gözü", "Sakral Çakra", "İçsel Güç ve Yaratıcılık")
    elif pitch < 210:
        return ("🟡", "Kehribar", "Solar Pleksus", "Özgüven ve İrade")
    elif pitch < 250:
        return ("🟢", "Yeşim", "Kalp Çakra", "Koşulsuz Sevgi ve Şifa")
    elif pitch < 290:
        return ("🩵", "Akuamarin", "Boğaz Çakra", "İfade ve Gerçeklik Akışı")
    elif pitch < 330:
        return ("🔵", "Lapis Lazuli", "Üçüncü Göz", "Sezgi ve Bilgelik")
    else:
        return ("🟣", "Ametist", "Tepe Çakra", "Yüksek Bilinç ve Aydınlanma")

# --- GÖRSEL KARŞILAMA EKRANI ---
st.markdown('<div class="crystal-hero">💎</div>', unsafe_allow_html=True)
st.markdown('<div class="vip-title">VBAR MİSTİK FREKANS</div>', unsafe_allow_html=True)
st.markdown('<div class="vip-subtitle">Sesinin ve ruhunun kristalini keşfet...</div>', unsafe_allow_html=True)

# --- GİRDİLER ---
duygu_durumu = st.selectbox("✨ Şu anki duygu durumun nedir?", ["Huzurlu", "Kaygılı", "Heyecanlı", "Yorgun", "İlham Dolu"])
audio_input = st.audio_input("🎙️ Sesini Kaydet:")

if audio_input:
    if st.button("✨ Mistik Analizi Başlat"):
        with st.spinner("Ses frekansların taranıyor..."):
            audio_bytes = audio_input.read()
            y, sr = librosa.load(io.BytesIO(audio_bytes), sr=16000)
            
            # Ses frekansını (pitch) hesapla
            f0 = librosa.yin(y, fmin=80.0, fmax=400.0)
            valid_f0 = f0[~np.isnan(f0)]
            mean_pitch = float(np.mean(valid_f0)) if len(valid_f0) > 0 else 180.0
            mean_pitch = max(80.0, min(mean_pitch, 400.0))
            
            icon, kristal_adi, cakra, aciklama = get_crystal_by_pitch(mean_pitch)
            
            st.session_state.current = {
                "id": random.randint(1000, 9999),
                "duygu": duygu_durumu,
                "kristal": kristal_adi,
                "icon": icon,
                "cakra": cakra,
                "pitch": mean_pitch,
                "mesaj": f"Sesindeki {mean_pitch:.1f} Hz frekans, '{duygu_durumu}' halinle bütünleşerek {aciklama} enerjini aktive ediyor."
            }
            st.success("✨ Ruhsal frekansınız başarıyla tarandı.")

# --- SONUÇ EKRANI ---
if st.session_state.current:
    res = st.session_state.current
    st.markdown(f"""
    <div class="result-card">
        <h3 style="color: #ff80ab; margin-top:0;">{res.get('icon', '💎')} {res.get('kristal', 'Kristal')} ({res.get('cakra', '')})</h3>
        <p><b>Frekans Değeri:</b> {res.get('pitch', 0):.1f} Hz</p>
        <p><b>Duygu Durumun:</b> {res.get('duygu', '')}</p>
        <p style="color: #f8bbd0; font-size: 1.05rem;">{res.get('mesaj', '')}</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("💾 Bu Sonucu Hafızaya Kaydet"):
        if st.session_state.current not in st.session_state.history:
            st.session_state.history.append(st.session_state.current)
            st.success("Mistik hafızaya eklendi!")
        else:
            st.warning("Bu analiz zaten hafızanızda kayıtlı.")

# --- GEÇMİŞ ---
if st.session_state.history:
    st.markdown("---")
    st.markdown("<h3 style='color: #ff80ab; text-align: center;'>📜 Mistik Geçmişin</h3>", unsafe_allow_html=True)
    for item in reversed(st.session_state.history):
        st.markdown(f"""
        <div style="background: rgba(255,128,171,0.03); border: 1px solid rgba(255,128,171,0.3); padding: 10px 15px; border-radius: 12px; margin-bottom: 8px;">
            <b>{item.get('icon', '💎')} {item.get('kristal', '')}</b> — <i>{item.get('pitch', 0):.1f} Hz</i> | <b>{item.get('duygu', '')}</b>
        </div>
        """, unsafe_allow_html=True)
        if st.button(f"🗑️ Bu Kaydı Sil #{item.get('id', 0)}", key=f"del_{item.get('id', 0)}"):
            st.session_state.history.remove(item)
            st.rerun()
