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
st.set_page_config(page_title="VBAR - Çakra ve Frekans Rehberi", page_icon="🎙️")

st.title("🎙️ VBAR - Biyometrik Çakra & Enerji Analizi")

# --- REHBER / AÇIKLAMA KISMI ---
with st.expander("✨ VBAR Nedir ve Size Nasıl Rehberlik Eder?", expanded=True):
    st.markdown("""
    **VBAR**, sesinizin biyometrik imzasını (frekans ve enerji değerlerini) analiz ederek 7 temel çakra sistemi ve kristal frekanslarıyla eşleştiren sezgisel bir rehberdir.
    
    * **Nasıl Fayda Sağlar?** Sesiniz o anki yorgunluğunuzu, coşkunuzu veya içsel arayışınızı ele verir. Bu uygulama, sesiniz üzerinden ruhsal durumunuzu okur ve o an en çok şifalanmaya ihtiyaç duyan enerji merkezinizi size gösterir.
    * **Yapay Zeka Koçluğu:** Sadece bir ölçüm yapmaz; yapay zeka sesinizin tonunu yorumlayarak size özel farkındalık soruları ve derinlemesine kişisel rehberlik sunar.
    """)

st.divider()

# --- 7 ÇAKRA VE TAŞ PROFİLİ SİSTEMİ ---
def get_chakra_profile(rms, pitch):
    # Frekans ve RMS değerlerine göre 7 çakraya dağılım
    if pitch < 120 or rms < 0.02:
        return "Kök Çakra", "🔴", "Kırmızı Akik", "#C0392B", "Köklenme, fiziksel güvenlik ve hayata tutunma ihtiyacı."
    elif pitch < 160:
        return "Sakral Çakra", "🟠", "Kaplan Gözü", "#E67E22", "Yaratıcılık, duygu akışı ve yaşam coşkusu."
    elif pitch < 210:
        return "Solar Pleksus", "🟡", "Kehribar", "#F1C40F", "Özgüven, irade gücü ve kişisel merkezlenme."
    elif pitch < 300:
        return "Kalp Çakra", "🟢", "Yeşim", "#27AE60", "Şefkat, içsel denge ve sevgiyi kabul etme."
    elif pitch < 450:
        return "Boğaz Çakra", "🩵", "Akuamarin", "#1ABC9C", "İfade gücü, berraklık ve sesin özgürce akışı."
    elif pitch < 650:
        return "Üçüncü Göz Çakra", "🔵", "Lapis Lazuli", "#2980B9", "Sezgi, derin algı ve içsel bilgelik."
    else:
        return "Tepe Çakra", "🟣", "Ametist", "#8E44AD", "Evrensel bağ, saf bilinç ve ruhsal açıklık."

# --- NİYET KARTI HAVUZU ---
def generate_dynamic_card(chakra_name, stone_name):
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

# --- SES GİRDİSİ VE ANALİZ ---
audio_input = st.audio_input("Analiz edilecek sesinizi kaydedin")

if audio_input:
    if st.button("🔍 Detaylı Çakra ve Enerji Analizini Başlat", type="primary", use_container_width=True):
        with st.spinner("Ses imzanız çakralarınızla hizalanıyor ve yapay zeka koçu yanıt hazırlıyor..."):
            audio_bytes = audio_input.read()
            y, sr = librosa.load(io.BytesIO(audio_bytes), sr=16000)
            rms = float(np.mean(librosa.feature.rms(y=y)))
            pitches, _ = librosa.piptrack(y=y, sr=sr)
            mean_pitch = float(np.mean(pitches[pitches > 0])) if len(pitches[pitches > 0]) > 0 else 150.0
            
            # 7 Çakra ve Taş Profilini Belirle
            chakra_name, icon, stone_name, color, chakra_desc = get_chakra_profile(rms, mean_pitch)
            
            # Yapay Zeka Derinlemesine Koçluk Yorumu
            ai_comment = ""
            if AI_READY:
                try:
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    prompt = f"""
                    Sen VBAR sisteminin sezgisel enerji koçu ve ses frekansı rehberisin. 
                    Kullanıcının ses dalgası analiz edildi:
                    - Frekans: {mean_pitch:.1f} Hz
                    - Enerji Seviyesi (RMS): {rms:.4f}
                    - Eşleşen Çakra: {chakra_name}
                    - Eşleşen Kristal/Taş: {stone_name} ({chakra_desc})

                    Lütfen bu verilere dayanarak kullanıcıya özel şu içerikte samimi, derinlikli ve kucaklayıcı bir rehberlik metni yaz:
                    1. Sesinin o anki tonuna bakarak ruh halinin ve içsel enerjisinin ne söylediğini anlat.
                    2. Bu çakranın ve taşın ona bu süreçte nasıl bir fayda sağlayacağını, hayatında neye odaklanması gerektiğini şefkatli bir dille açıkla.
                    3. Kapanışta üzerine düşünmesi için ona ilham verici küçük bir farkındalık sorusu sor.
                    """
                    response = model.generate_content(prompt)
                    ai_comment = response.text
                except Exception:
                    ai_comment = f"Sesiniz {chakra_name} ({stone_name}) frekansı ile uyuştu. Enerji akışınız başarıyla haritalandırıldı."
            else:
                ai_comment = f"Sesiniz {chakra_name} frekansında, {stone_name} taşıyla rezonans gösteriyor."

            st.session_state.analysis_results = {
                "rms": rms, "pitch": mean_pitch, "chakra": chakra_name, "stone": stone_name,
                "icon": icon, "col": color, "desc": chakra_desc, "ai_comment": ai_comment
            }
            st.session_state.current_card = generate_dynamic_card(chakra_name, stone_name)
            st.rerun()

# --- SONUÇLAR VE METRİKLER ---
if st.session_state.analysis_results:
    res = st.session_state.analysis_results
    
    st.markdown(f"## {res['icon']} {res['chakra']} — {res['stone']} Frekansı")
    st.markdown(f"*{res['desc']}*")
    
    col1, col2 = st.columns(2)
    col1.metric("Frekans (Hz)", f"{res['pitch']:.1f}")
    col2.metric("Enerji (RMS)", f"{res['rms']:.4f}")
    
    st.divider()
    
    # Yapay Zeka Koçluk Alanı
    st.markdown("#### 🧠 VBAR Yapay Zeka Enerji Koçu")
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
    
    # --- KULLANICININ YAPAY ZEKAYA SORU SORMASI İÇİN ETKİLEŞİMLİ ALAN ---
    st.divider()
    st.markdown("#### 💬 Yapay Zeka Koçuna Soru Sorun")
    user_question = st.text_input("Bu analizle ilgili kafanıza takılan bir şeyi sorun (Örn: Bu enerjiyi nasıl dengeleyebilirim?)")
    
    if user_question and AI_READY:
        if st.button("Koça Danış"):
            with st.spinner("Koçunuz yanıtlıyor..."):
                try:
                    chat_model = genai.GenerativeModel('gemini-1.5-flash')
                    chat_prompt = f"""
                    Kullanıcı VBAR uygulamasında {res['chakra']} ({res['stone']}) frekansında analiz edildi.
                    Kullanıcının sorusu: "{user_question}"
                    Lütfen bu bağlamda ona samimi, bilge ve rehberlik edici bir dille yanıt ver.
                    """
                    chat_response = chat_model.generate_content(chat_prompt)
                    st.success(chat_response.text)
                except Exception:
                    st.warning("Şu an yanıt oluşturulamadı, lütfen tekrar deneyin.")
    
    st.write("")
    if st.button("🔄 Yeni Bir Ses Analiz Et", use_container_width=True):
        st.session_state.analysis_results = None
        st.rerun()
        
