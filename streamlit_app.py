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
st.set_page_config(page_title="VBAR - Kişisel Enerji & Koçluk Rehberi", page_icon="🎙️")

# --- ÖZEL TASARIM (PEMBE TONLAR VE ŞIK STİLLER) ---
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #fce4ec 0%, #f8bbd0 50%, #f48fb1 100%);
        color: #3e2723;
    }
    h1 {
        color: #880e4f;
        text-align: center;
        font-family: 'Helvetica Neue', sans-serif;
        text-shadow: 1px 1px 2px rgba(255,255,255,0.8);
    }
    .stButton>button {
        background-color: #c2185b;
        color: white;
        border-radius: 12px;
        border: none;
        font-weight: bold;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .stButton>button:hover {
        background-color: #880e4f;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# --- GÖRSEL ALAN ---
st.markdown("""
<div style="text-align: center; padding: 20px; background: rgba(255, 255, 255, 0.6); border-radius: 20px; backdrop-filter: blur(5px); margin-bottom: 20px; box-shadow: 0 8px 16px rgba(0,0,0,0.05);">
    <div style="font-size: 55px; margin-bottom: -10px;">☁️ 💎 ☁️</div>
    <h1 style="font-size: 28px; margin-top: 5px; color: #880e4f;">VBAR Biyometrik Enerji Rehberi</h1>
    <p style="font-size: 1.15em; color: #6a1b9a; font-weight: 600;">Sesinizin frekansıyla ruhsal merkezinizi keşfedin, kristal enerjisiyle hizalanın.</p>
</div>
""", unsafe_allow_html=True)

# --- DETAYLI AÇIKLAMA KISMI ---
with st.expander("✨ VBAR Nedir? Nasıl Çalışır ve Size Ne Sunar?", expanded=False):
    st.markdown("""
    **VBAR**, sesinizin yaydığı o anki biyometrik titreşimleri (frekans ve enerji değerlerini) analiz ederek **7 temel çakra sistemi** ve şifalı kristallerle buluşturan özel bir farkındalık alanıdır.
    
    ---
    
    ### 🌟 Bu Uygulamada Sizi Neler Bekliyor?
    * **Ses Analizi:** Mikrofona konuştuğunuzda sesinizin frekansı taranır ve o an en çok hangi enerji merkezinde yoğunlaştığınız tespit edilir.
    * **Manevi ve Tinsel Karşılık:** Kök çakradan tepe çakraya kadar her katmanın ilahi ve enerjik anlamı derinlemesine yorumlanır.
    * **Size Özel Niyet Kartı:** Analiz sonucunuza göre zihninizi ve ruhunuzu dinlendirecek özel niyetler ve somut eylem adımları sunulur.
    * **Birebir Rehberlik:** Yolculuğunuzu derinleştirmek için doğrudan **Ruhunnmimarisi@gmail.com** üzerinden iletişime geçebilirsiniz.
    """)

st.divider()

# --- 7 ÇAKRA VE TAŞ PROFİLİ SİSTEMİ (GÜNCELLENMİŞ EŞİKLER) ---
def get_chakra_profile(rms, pitch):
    if pitch < 100 or rms < 0.015:
        return "Kök Çakra (Muladhara)", "🔴", "Kırmızı Akik", "#C0392B", "Dünya ile bağ, fiziksel güven, köklenme ve aidiyetin merkezidir."
    elif pitch < 140:
        return "Sakral Çakra (Svadhisthana)", "🟠", "Kaplan Gözü", "#E67E22", "Duygu akışı, yaratım enerjisi ve yaşam coşkusunun merkezidir."
    elif pitch < 180:
        return "Solar Pleksus (Manipura)", "🟡", "Kehribar", "#F1C40F", "Özdeğer, irade, özgüven ve bireysel gücün merkezidir."
    elif pitch < 250:
        return "Kalp Çakra (Anahata)", "🟢", "Yeşim", "#27AE60", "Koşulsuz sevgi, şefkat, merhamet ve içsel dengenin merkezidir."
    elif pitch < 350:
        return "Boğaz Çakra (Vishuddha)", "🩵", "Akuamarin", "#1ABC9C", "Hakikat, ilahi ifade, sesin özgürce ve dürüstçe akışının merkezidir."
    elif pitch < 600:
        return "Üçüncü Göz Çakra (Ajna)", "🔵", "Lapis Lazuli", "#2980B9", "Sezgi, içsel bilgelik, ötesini görebilme ve idrakin merkezidir."
    else:
        return "Tepe Çakra (Sahasrara)", "🟣", "Ametist", "#8E44AD", "İlahi olanla bağ, saf bilinç, evrensel birlik ve Hakikat ile bütünleşme merkezidir."

# --- NİYET KARTI HAVUZU ---
def generate_dynamic_card(chakra_name, stone_name):
    havuz = [
        {
            "title": "İlahi Akışa Teslimiyet",
            "affirmation": "Yaradan ile aramdaki tüm perdeleri kaldırıyorum; evrenin kusursuz akışına güvenle teslim oluyorum.",
            "action": "Başınızın tepesindeki hafifleme hissine odaklanıp derin ve yavaş bir nefes alın."
        },
        {
            "title": "Saf Bilinç Alanı",
            "affirmation": "Zihnin gürültüsünden arınıyor, özümdeki o sessiz ve ilahi huzurla buluşuyorum.",
            "action": "Gözlerinizi kapatın ve zihninizin tepesinde parlayan saf ışığı hayal edin."
        },
        {
            "title": "Hakikati Duymak",
            "affirmation": "Kendi iç sesimin ve ilahi rehberliğin sesimin tonundan kalbime akmasına izin veriyorum.",
            "action": "Ellerinizi boynunuza veya kalbinize götürerek sesinizin titreşimini hissedin."
        }
    ]
    return random.choice(havuz)

# --- HAFIZA YÖNETİMİ ---
if "analysis_results" not in st.session_state: st.session_state.analysis_results = None
if "current_card" not in st.session_state: st.session_state.current_card = None

# --- SES GİRDİSİ VE ANALİZ ---
st.markdown("<p style='font-weight: bold; color: #880e4f; font-size: 1.1em;'>🎤 Analiz edilecek sesinizi kaydetmek için mikrofona dokunun</p>", unsafe_allow_html=True)
audio_input = st.audio_input("")

if audio_input:
    if st.button("🔍 Detaylı Çakra ve Enerji Analizini Başlat", type="primary", use_container_width=True):
        with st.spinner("Ses imzanız manevi frekanslarla hizalanıyor..."):
            audio_bytes = audio_input.read()
            y, sr = librosa.load(io.BytesIO(audio_bytes), sr=16000)
            rms = float(np.mean(librosa.feature.rms(y=y)))
            pitches, _ = librosa.piptrack(y=y, sr=sr)
            mean_pitch = float(np.mean(pitches[pitches > 0])) if len(pitches[pitches > 0]) > 0 else 150.0
            
            chakra_name, icon, stone_name, color, chakra_desc = get_chakra_profile(rms, mean_pitch)
            
            ai_comment = ""
            if AI_READY:
                try:
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    prompt = f"""
                    Sen VBAR sisteminin manevi enerji ve çakra rehberisin. 
                    Kullanıcının ses dalgası analiz edildi:
                    - Frekans: {mean_pitch:.1f} Hz
                    - Enerji Seviyesi (RMS): {rms:.4f}
                    - Eşleşen Çakra: {chakra_name}
                    - Çakra Anlamı: {chakra_desc}
                    - Eşleşen Taş: {stone_name}

                    KESİN KURALLAR:
                    1. Asla konuyu sıradan bir stres veya günlük yorgunluğa indirgeme. Çakranın manevi ve tinsel anlamına sadık kal. 
                    2. Eğer çıkan çakra Tepe Çakra (Sahasrara) ise; kişinin ilahi olanla bağını, evrensel bilinçle bütünleşmesini, ruhsal açıklığını ve saf idrak halini şiirsel ve derin bir dille kutla.
                    3. Kullanıcıya bu manevi boyutu derinleştirmesi için **2 adet düşündürücü farkındalık sorusu** sor.
                    4. Bu çalışmayı ve içsel yolculuğu **Ruhunnmimarisi@gmail.com** adresine e-posta göndererek birebir danışmanlık alabileceğini nazikçe hatırlat.
                    """
                    response = model.generate_content(prompt)
                    ai_comment = response.text
                except Exception:
                    ai_comment = f"Sesiniz {chakra_name} ({stone_name}) frekansı ile rezonans gösterdi. Bu ilahi ve tinsel frekans, ruhsal bağınızın ve içsel açıklığınızın en saf yansımasıdır."
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
    
    st.markdown("#### 🧠 Manevi Farkındalık & Koçluk Rehberi")
    st.info(res['ai_comment'])
    
    st.divider()
    
    st.markdown("#### 🔮 Size Özel Niyet Kartı")
    card = st.session_state.current_card
    
    st.markdown(f"""
    <div style="border: 2px solid {res['col']}; padding: 20px; border-radius: 16px; background: rgba(255,255,255,0.85);">
        <h3 style="color:{res['col']}; margin-top:0;">{card['title']}</h3>
        <p style="font-size: 1.1em; font-weight: 500;">"{card['affirmation']}"</p>
        <div style="background:{res['col']}22; padding:12px; border-radius:10px; font-weight: 500;">💡 <b>Eylem:</b> {card['action']}</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.write("")
    
    st.divider()
    st.markdown("""
    <div style="background: rgba(255, 255, 255, 0.9); padding: 20px; border-radius: 16px; border: 1px dashed #c2185b; text-align: center;">
        <h3 style="color: #ad1457; margin-top: 0;">✨ Bu Çalışmayı Derinleştirmek İster misiniz?</h3>
        <p style="font-size: 1.05em; font-weight: 500;">Çıkan bu frekans analizini, aklınıza takılan manevi soruları ve kişisel gelişim yolculuğunuzu birebir seanslarla desteklemek için doğrudan <b>Ruhunnmimarisi@gmail.com</b> adresine yazarak iletişime geçebilirsiniz.</p>
        <a href="mailto:Ruhunnmimarisi@gmail.com" style="display: inline-block; background: #c2185b; color: white; padding: 10px 20px; border-radius: 8px; text-decoration: none; font-weight: bold; margin-top: 10px;">📧 Ruhunnmimarisi@gmail.com ile İletişime Geç</a>
    </div>
    """, unsafe_allow_html=True)
    
    st.write("")
    if st.button("🔄 Yeni Bir Ses Analiz Et", use_container_width=True):
        st.session_state.analysis_results = None
        st.rerun()
