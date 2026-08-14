import streamlit as st
import librosa
import numpy as np
import io
import random
import google.generativeai as genai

# --- API VE MODEL BAĞLANTISI ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
    AI_READY = True
except Exception:
    AI_READY = False

# --- SAYFA VE SES AYARLARI ---
st.set_page_config(page_title="VBAR | VIP Mistik Deneyim", page_icon="💎", layout="centered")

# --- ULTRA VIP MİSTİK TASARIM (CSS) ---
st.markdown("""
<style>
    /* Arka Plan - Derin Mistik Gradyan */
    .stApp {
        background: linear-gradient(135deg, #2c1630 0%, #4a154b 50%, #1a0b1c 100%);
        color: #fce4ec;
        font-family: 'Helvetica Neue', sans-serif;
    }
    
    /* Gizlenecek Streamlit Elementleri */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* VIP Karşılama Kartı */
    .vip-hero {
        background: rgba(255, 255, 255, 0.04);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 215, 0, 0.25);
        padding: 35px 20px;
        border-radius: 30px;
        text-align: center;
        margin-bottom: 25px;
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.4);
    }
    
    .vip-title {
        color: #ffd700;
        font-size: 24px;
        font-weight: 700;
        letter-spacing: 1px;
        margin-bottom: 10px;
        text-transform: uppercase;
    }
    
    .vip-desc {
        color: #f8bbd0;
        font-size: 1.05em;
        line-height: 1.6;
        font-weight: 300;
    }

    /* Ses Kayıt Bölümü Başlığı */
    .section-label {
        color: #e1bee7;
        font-size: 1rem;
        font-weight: 500;
        text-align: center;
        margin-bottom: 10px;
        letter-spacing: 0.5px;
    }

    /* Özel Buton Tasarımı (Analiz/Kaydet) */
    div.stButton > button.save-btn {
        background: linear-gradient(135deg, #ffd700 0%, #ffa000 100%);
        color: #1a0b1c !important;
        border-radius: 50px !important;
        padding: 12px 24px !important;
        border: none !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        box-shadow: 0 8px 20px rgba(255, 215, 0, 0.25);
        transition: all 0.3s ease;
        width: auto;
        margin: 10px auto; /* Ortala */
    }
    
    div.stButton > button.save-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 25px rgba(255, 215, 0, 0.4);
        background: linear-gradient(135deg, #ffea79 0%, #ffb300 100%);
    }
    
    /* Sil Butonu Tasarımı */
    div.stButton > button.delete-btn {
        background: rgba(255, 215, 0, 0.1) !important;
        color: #ffd700 !important;
        border: 1px solid rgba(255, 215, 0, 0.3) !important;
        border-radius: 20px !important;
        padding: 6px 18px !important;
        font-size: 0.85rem !important;
        margin-top: -10px;
        margin-bottom: 20px;
    }
    
    div.stButton > button.delete-btn:hover {
        background: rgba(255, 215, 0, 0.2) !important;
    }

    /* Geçmiş Kartları Tasarımı */
    .result-card {
        background: rgba(255, 255, 255, 0.06);
        backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.15);
        padding: 15px 20px;
        border-radius: 16px;
        margin-bottom: 8px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .result-text {
        font-size: 1.1rem;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# --- HAFIZA YÖNETİMİ (Hem Sonuç Hem Geçmiş) ---
if "current_analysis" not in st.session_state: st.session_state.current_analysis = None
if "history" not in st.session_state: st.session_state.history = []

# --- 7 ÇAKRA PROFİLİ ---
def get_chakra_profile(rms, pitch):
    normalized_pitch = min(max(pitch, 80.0), 800.0)
    
    if normalized_pitch < 180:
        return "Kök Çakra", "🔴", "Kırmızı Akik", "#E74C3C"
    elif normalized_pitch < 270:
        return "Sakral Çakra", "🟠", "Kaplan Gözü", "#E67E22"
    elif normalized_pitch < 360:
        return "Solar Pleksus", "🟡", "Kehribar", "#F1C40F"
    elif normalized_pitch < 450:
        return "Kalp Çakra", "🟢", "Yeşim", "#2ECC71"
    elif normalized_pitch < 540:
        return "Boğaz Çakra", "🩵", "Akuamarin", "#1ABC9C"
    elif normalized_pitch < 650:
        return "Üçüncü Göz Çakra", "🔵", "Lapis Lazuli", "#3498DB"
    else:
        return "Tepe Çakra", "🟣", "Ametist", "#9B59B6"

# --- UYGULAMA AKIŞI ---

# 1. VIP Karşılama
st.markdown("""
<div class="vip-hero">
    <div style="font-size: 45px; margin-bottom: 12px; letter-spacing: 8px;">✨ 💎 🔮</div>
    <div class="vip-title">VBAR Mistik Frekans</div>
    <div class="vip-desc">Sesinizin eşsiz biyometrik imzası, evrenin ve kristallerin kadim frekansıyla hizalanıyor.</div>
</div>
""", unsafe_allow_html=True)

# 2. Ses Girişi (Geri Getirildi!)
st.markdown("<div class='section-label'>🎙️ Analiz için sesinizi kaydedin</div>", unsafe_allow_html=True)
audio_input = st.audio_input("")

if audio_input:
    st.write("")
    # Analiz Butonu (Stil Eklendi)
    if st.button("✨ Mistik Frekans Analizini Başlat", key="btn_analyze", type="primary"):
        with st.spinner("Ses imzanız evrensel akışla taranıyor..."):
            audio_bytes = audio_input.read()
            y, sr = librosa.load(io.BytesIO(audio_bytes), sr=16000)
            rms = float(np.mean(librosa.feature.rms(y=y)))
            pitches, _ = librosa.piptrack(y=y, sr=sr)
            mean_pitch = float(np.mean(pitches[pitches > 0])) if len(pitches[pitches > 0]) > 0 else 150.0
            
            chakra_name, icon, stone_name, color = get_chakra_profile(rms, mean_pitch)
            
            ai_comment = ""
            if AI_READY:
                try:
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    prompt = f"""
                    Sen VBAR sisteminin manevi enerji ve çakra rehberisin. 
                    Kullanıcının ses dalgası analiz edildi:
                    - Frekans: {mean_pitch:.1f} Hz
                    - Eşleşen Çakra: {chakra_name} ({stone_name})
                    
                    GÖREVİN:
                    Bu çakranın ruhsal derinliğini, kişinin potansiyelini son derece şiirsel, lüks ve büyüleyici bir dille yorumla. Asla mekanik olma.
                    """
                    response = model.generate_content(prompt)
                    ai_comment = response.text.strip()
                except Exception:
                    ai_comment = "Sesinizin mistik frekansı, enerjinizin derin bir akışta olduğunu müjdeliyor."
            else:
                ai_comment = "Sesinizin mistik frekansı, enerjinizin derin bir akışta olduğunu müjdeliyor."

            st.session_state.current_analysis = {
                "id": random.randint(1000, 9999),
                "rms": rms, "pitch": mean_pitch, "chakra": chakra_name, "stone": stone_name,
                "icon": icon, "col": color, "ai_comment": ai_comment
            }
            # Analizden sonra sayfayı yenilemeye gerek yok, sadece kaydı göster.

# 3. Sonuçları Göster ve Kaydetme İmkanı
if st.session_state.current_analysis:
    res = st.session_state.current_analysis
    
    st.markdown("#### 🔮 Analiz Sonucu")
    st.markdown(f"""
    <div class="result-card">
        <div class="result-text" style="color: {res['col']};">
            {res['icon']} {res['chakra']} — {res['stone']} (Frekans: {res['pitch']:.1f} Hz)
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.info(res['ai_comment'])
    
    # Kaydet Butonu (Stil ve İşlev Eklendi)
    st.write("")
    if st.button("💾 Bu Sonucu Geçmişe Kaydet", key="btn_save", help="Bu analizi kalıcı geçmişinize ekler."):
        if st.session_state.current_analysis not in st.session_state.history:
            st.session_state.history.append(st.session_state.current_analysis)
            st.success("Başarıyla kaydedildi!")
        else:
            st.warning("Bu analiz zaten geçmişinizde mevcut.")

# 4. GEÇMİŞİ LİSTELE VE SİL (İstediğiniz gibi)
if st.session_state.history:
    st.markdown("---")
    st.subheader("📜 Geçmiş Analizleriniz")
    
    # En yeniden en eskiye sıralamak için ters çevir
    for i, item in enumerate(reversed(st.session_state.history)):
        # Geri çevirdiğimiz listenin orijinal indeksini bulmamız gerekiyor
        original_index = len(st.session_state.history) - 1 - i
        
        with st.container():
            st.markdown(f"""
            <div class='result-card'>
                <div class='result-text' style='color: {item['col']}; font-size: 1.0rem;'>
                    {item['icon']} {item['chakra']} | {item['pitch']:.1f} Hz
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Silme Butonu (Stil ve İşlev Eklendi)
            if st.button(f"🗑️ Sil", key=f"del_{item['id']}", type="secondary"):
                # Orijinal indeksteki elemanı sil
                st.session_state.history.pop(original_index)
                st.rerun()
