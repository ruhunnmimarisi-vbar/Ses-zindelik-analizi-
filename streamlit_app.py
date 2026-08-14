import streamlit as st
import librosa
import numpy as np
import io
import google.generativeai as genai

# --- API VE MODEL BAĞLANTISI ---
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# --- SAYFA VE SES AYARLARI ---
st.set_page_config(page_title="VBAR - Derinlemesine Biyometrik Analiz", page_icon="🎙️")
st.title("🎙️ VBAR - Ses Zindelik ve Enerji Analizi")

# --- TAŞ PROFİLİ BELİRLEME ---
def get_stone_profile(rms, pitch):
    if rms < 0.03: 
        return "Oniks", "🖤", "#2C3E50", "Topraklanma ve derin sessizlik arayışında bir frekans."
    elif rms < 0.06: 
        return "Labradorit", "✨", "#34495E", "Sezgisel geçişler ve zihinsel dalgalanmaların olduğu bir alan."
    elif pitch > 200: 
        return "Akuamarin", "🩵", "#1ABC9C", "Yüksek titreşimli, akışkan ve berrak bir enerji alanı."
    else: 
        return "Hematit", "🩶", "#95A5A6", "Güçlü bir merkezleme ve fiziksel denge frekansı."

# --- HAFIZA YÖNETİMİ ---
if "analysis_results" not in st.session_state: st.session_state.analysis_results = None

# --- SES GİRDİSİ VE ANALİZ ---
audio_input = st.audio_input("Analiz edilecek sesinizi kaydedin")

if audio_input:
    if st.button("🔍 Detaylı Biyometrik Analizi Başlat", type="primary", use_container_width=True):
        with st.spinner("Ses imzanız analiz ediliyor ve yorumlanıyor..."):
            audio_bytes = audio_input.read()
            y, sr = librosa.load(io.BytesIO(audio_bytes), sr=16000)
            rms = float(np.mean(librosa.feature.rms(y=y)))
            pitches, _ = librosa.piptrack(y=y, sr=sr)
            mean_pitch = float(np.mean(pitches[pitches > 0])) if len(pitches[pitches > 0]) > 0 else 150.0
            
            # Taş profilini belirle
            stone_name, icon, color, desc = get_stone_profile(rms, mean_pitch)
            
            # Gemini'ye Sadece Metin Tabanlı Güvenli Prompt
            try:
                model = genai.GenerativeModel('gemini-1.5-flash')
                prompt = f"""
                Bir vokal biyometrik analiz uzmanı gibi davran. 
                Ses analizi sonuçları -> Frekans: {mean_pitch:.1f} Hz, Enerji (RMS): {rms:.4f}. 
                Eşleşen Taş Profili: {stone_name}.
                Lütfen bu verilere dayanarak kişinin o anki zindelik, enerji seviyesi ve zihinsel durumu hakkında samimi, derinlikli ve yol gösterici bir değerlendirme yap.
                """
                ai_response = model.generate_content(prompt)
                ai_comment = ai_response.text
            except Exception as e:
                ai_comment = "Analiz tamamlandı ancak yapay zeka metin yorumu oluşturulamadı."

            st.session_state.analysis_results = {
                "rms": rms, "pitch": mean_pitch, "name": stone_name, 
                "icon": icon, "col": color, "desc": desc, "ai_comment": ai_comment
            }
            st.rerun()

# --- SONUÇLAR VE METRİKLER ---
if st.session_state.analysis_results:
    res = st.session_state.analysis_results
    
    st.markdown(f"## {res['icon']} {res['name']} Frekansı")
    st.markdown(f"*{res['desc']}*")
    
    col1, col2 = st.columns(2)
    col1.metric("Frekans (Hz)", f"{res['pitch']:.1f}")
    col2.metric("Enerji (RMS)", f"{res['rms']:.4f}")
    
    st.divider()
    
    st.markdown("#### 🧠 VBAR Derinlemesine Analiz")
    st.info(res['ai_comment'])
    
    if st.button("🔄 Yeni Bir Ses Analiz Et"):
        st.session_state.analysis_results = None
        st.rerun()
    
