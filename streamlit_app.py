import streamlit as st
import librosa
import numpy as np
import io
import random
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

# --- NİYET KARTI HAVUZU ---
def generate_dynamic_card(stone_name):
    havuz = [
        {
            "title": "Zihinsel Seyir Hali",
            "affirmation": "Düşüncelerin gelip geçmesine izin veriyorum; ben sadece kıyide duran bir gözlemciyim.",
            "action": "Parmak uçlarınızı birbirine hafifçe değdirin ve aralarındaki sıcaklığı hissedin."
        },
        {
            "title": "Ağırlığı Serbest Bırakmak",
            "affirmation": "Taşıdığım tüm zihinsel yükleri şu an bulunduğum yere nazikçe bırakıyorum.",
            "action": "Gözlerinizi kapatın ve dikkatinizi sadece dilinizin damaktaki duruşuna verip gevşetin."
        },
        {
            "title": "İçsel Alan Açmak",
            "affirmation": "Her şeyin anında mükemmel olması gerekmiyor; belirsizlik içinde de güvendeyim.",
            "action": "Ellerinizi kalbinizin üzerine koyun ve içerideki ritmi sadece 5 saniye dinleyin."
        },
        {
            "title": "Durmanın Hakikati",
            "affirmation": "Üretkenlik maskesini çıkarıyorum; şu an sadece var olmak en büyük eylemim.",
            "action": "Çenenizi hafifçe aralayın ve dişlerinizin birbirine değmesini engelleyin."
        },
        {
            "title": "Zamanın Akışına Bırakış",
            "affirmation": "Günün geri kalanını kontrol etmeye çalışmıyorum, anın beni taşımasına izin veriyorum.",
            "action": "Ayak tabanlarınızın yere bastığı noktadaki güvenli bası hissedin."
        }
    ]
    return random.choice(havuz)

# --- HAFIZA YÖNETİMİ ---
if "analysis_results" not in st.session_state: st.session_state.analysis_results = None
if "current_card" not in st.session_state: st.session_state.current_card = None
if "card_flipped" not in st.session_state: st.session_state.card_flipped = False

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
            
            # Gemini Metin Analizi
            try:
                model = genai.GenerativeModel('gemini-1.5-flash')
                prompt = f"""
                Bir vokal biyometrik analiz uzmanı gibi davran. 
                Ses analizi sonuçları -> Frekans: {mean_pitch:.1f} Hz, Enerji (RMS): {rms:.4f}. 
                Eşleşen Taş Profili: {stone_name}.
                Lütfen bu verilere dayanarak kişinin o anki zindelik, enerji seviyesi ve zihinsel durumu hakkında samimi, derinlikli bir değerlendirme yap.
                """
                ai_response = model.generate_content(prompt)
                ai_comment = ai_response.text
            except Exception as e:
                ai_comment = "Analiz tamamlandı ancak yapay zeka metin yorumu oluşturulamadı."

            st.session_state.analysis_results = {
                "rms": rms, "pitch": mean_pitch, "name": stone_name, 
                "icon": icon, "col": color, "desc": desc, "ai_comment": ai_comment
            }
            st.session_state.card_flipped = False
            st.session_state.current_card = generate_dynamic_card(stone_name)
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
    
    st.divider()
    
    # Niyet Kartı Bölümü
    st.markdown("#### 🔮 Size Özel Niyet Kartı")
    card = st.session_state.current_card
    
    st.markdown(f"""
    <div style="border: 2px solid {res['col']}; padding: 20px; border-radius: 16px; background: rgba(0,0,0,0.03);">
        <h3 style="color:{res['col']}; margin-top:0;">{card['title']}</h3>
        <p style="font-size: 1.1em;">"{card['affirmation']}"</p>
        <div style="background:{res['col']}33; padding:12px; border-radius:10px;">💡 <b>Eylem:</b> {card['action']}</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.write("")
    if st.button("🔄 Yeni Bir Ses Analiz Et", use_container_width=True):
        st.session_state.analysis_results = None
        st.rerun()
    
    
