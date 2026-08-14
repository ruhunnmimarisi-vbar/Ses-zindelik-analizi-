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
    .result-card, .qa-card {
        background: rgba(255, 128, 171, 0.05);
        border: 2px solid #ff80ab;
        padding: 20px;
        border-radius: 20px;
        margin: 15px 0;
        box-shadow: inset 0 0 15px rgba(255, 128, 171, 0.1);
    }
    label, .stSelectbox, .stAudioInput, .stTextInput {
        color: #ff80ab !important;
    }
</style>
""", unsafe_allow_html=True)

# --- HAFIZA ---
if "history" not in st.session_state: st.session_state.history = []
if "current" not in st.session_state: st.session_state.current = None
if "qa_history" not in st.session_state: st.session_state.qa_history = []

# --- NET ÇAKRA VE FREKANS EŞLEŞTİRMELERİ ---
def get_crystal_by_pitch(pitch):
    if pitch < 170:
        return ("🔴", "Kırmızı Akik", "Kök Çakra", "Topraklanma ve Güven")
    elif pitch < 210:
        return ("🟠", "Kaplan Gözü", "Sakral Çakra", "İçsel Güç ve Yaratıcılık")
    elif pitch < 250:
        return ("🟡", "Kehribar", "Solar Pleksus", "Özgüven ve İrade")
    elif pitch < 290:
        return ("🟢", "Yeşim", "Kalp Çakra", "Koşulsuz Sevgi ve Şifa")
    elif pitch < 330:
        return ("🩵", "Akuamarin", "Boğaz Çakra", "İfade ve Gerçeklik Akışı")
    elif pitch < 370:
        return ("🔵", "Lapis Lazuli", "Üçüncü Göz Çakra", "Sezgi ve Bilgelik")
    else:
        return ("🟣", "Ametist", "Tepe Çakra", "Yüksek Bilinç ve Aydınlanma")

# --- GÖRSEL KARŞILAMA EKRANI ---
st.markdown('<div class="crystal-hero">💎</div>', unsafe_allow_html=True)
st.markdown('<div class="vip-title">VBAR MİSTİK FREKANS</div>', unsafe_allow_html=True)
st.markdown('<div class="vip-subtitle">Sesinin ve ruhunun kristalini keşfet...</div>', unsafe_allow_html=True)

# --- BÖLÜMLER (SEKMELER) ---
tab1, tab2 = st.tabs(["✨ Frekans & Kristal Analizi", "🔮 Mistik Soru-Cevap Rehberi"])

with tab1:
    # --- GİRDİLER ---
    duygu_durumu = st.selectbox("✨ Şu anki duygu durumun nedir?", ["Huzurlu", "Kaygılı", "Heyecanlı", "Yorgun", "İlham Dolu"], key="duygu_select")
    audio_input = st.audio_input("🎙️ Sesini Kaydet:")

    if audio_input:
        if st.button("✨ Mistik Analizi Başlat"):
            with st.spinner("Ses frekansların taranıyor..."):
                audio_bytes = audio_input.read()
                y, sr = librosa.load(io.BytesIO(audio_bytes), sr=16000)
                
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
                <b>{item.get('icon', '💎')} {item.get('kristal', '')} ({item.get('cakra', '')})</b> — <i>{item.get('pitch', 0):.1f} Hz</i> | <b>{item.get('duygu', '')}</b>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"🗑️ Bu Kaydı Sil #{item.get('id', 0)}", key=f"del_{item.get('id', 0)}"):
                st.session_state.history.remove(item)
                st.rerun()

with tab2:
    st.markdown("<h3 style='color: #ff80ab; text-align: center;'>🌟 Mistik Bilgeye Sor</h3>", unsafe_allow_html=True)
    st.write("Aklına takılan bir soruyu, karar vermekte zorlandığın bir konuyu veya ruhsal bir durumu buraya yaz; evrenin ve içsel rehberliğin süzgecinden geçirelim.")
    
    user_question = st.text_input("Sormak istediğin soru veya niyetin nedir?", placeholder="Örn: Bugün enerjimi dengelemek için ne yapmalıyım?")
    
    if st.button("✨ Rehberlik İste"):
        if user_question:
            cevaplar = [
                f"'{user_question}' niyetin için kristallerin fısıltısı: Derin bir nefes al ve iç sesine güven. Bu süreçte sabır en büyük rehberindir.",
                f"'{user_question}' konusunda evren sana 'akışta kal' diyor. Direnci bırakıp kabule geçtiğinde yolun aydınlanacak.",
                f"'{user_question}' sorusunun cevabı senin kalbinde saklı. Bugün biraz toprakla temas etmek ve içsel sınırlarını korumak sana çok iyi gelecek.",
                f"'{user_question}' enerjisiyle ilgili olarak: İçindeki o şifalı gücü fark et. Doğru zamandasın, doğru yerdesin."
            ]
            secilen_cevap = random.choice(cevaplar)
            st.session_state.qa_history.append({"soru": user_question, "cevap": secilen_cevap})
        else:
            st.warning("Lütfen rehberlik almak istediğin soruyu yaz.")
            
    if st.session_state.qa_history:
        st.markdown("---")
        st.markdown("#### 📜 Geçmiş Rehberlikler")
        for qa in reversed(st.session_state.qa_history):
            st.markdown(f"""
            <div class="qa-card">
                <p><b>Soru:</b> {qa['soru']}</p>
                <p style="color: #f8bbd0;"><b>Rehberlik:</b> {qa['cevap']}</p>
            </div>
            """, unsafe_allow_html=True)
