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

# --- GELİŞTİRİLMİŞ AKILLI YANIT MOTORU ---
def generate_smart_response(question):
    q = question.lower()
    
    # İhanet, Aldatma, Paramparça, Hayal Kırıklığı Senaryoları
    if any(k in q for k in ["aldat", "ihanet", "yalan", "paramparça", "bırakıp gitti", "terk"]):
        return (
            "Yaşadığın bu derin ihanet ve sarsıcı hayal kırıklığı karşısında kalbinin acı içinde kalması çok normal. "
            "Böyle anlarda dünyan başına yıkılmış gibi hissedebilirsin, çünkü sen ilişkiye ve sevgiye dürüstçe adandın. "
            "Ancak unutma ki bu acı, senin değerini düşürmez; aksine karşı tarafın eksikliğini ve niyetini gösterir. "
            "Bugün kendine yapabileceğin en büyük iyilik, o kırık parçaları dışarıda aramak yerine, kendi öz sevgine ve ruhunun şifa alanına çekilmektir. "
            "Zaman bu yarayı kapatacak ve sen bu fırtınadan eskisinden çok daha güçlü çıkacaksın."
        )
    # Kalp Kırıklığı / Üzüntü Senaryoları
    elif any(k in q for k in ["kalp kırık", "hayal kırık", "üzgün", "ağrı", "acır", "ağla"]):
        return (
            "Yaşadığın bu kırgınlık ve içindeki sessiz ağırlık, ruhunun çok derin bir arınma sürecinden geçtiğini gösteriyor. "
            "Her gözyaşı ve her acı anı, aslında kalbinin üzerine binen o ağır yükü dışarı akıtır. "
            "Kendine bu yas sürecini yaşama izni ver; her şeyi aynı anda omuzlamak zorunda değilsin. "
            "Bugün sadece kendi kabuğuna çekil, derin nefesler al ve içindeki o saf özün yeniden aydınlanmasını bekle."
        )
    # Can Sıkıntısı / Daralma Senaryoları
    elif any(k in q for k in ["sıkıl", "daral", "bunul", "ne yapmalıyım", "bununtu"]):
        return (
            "Canının sıkılması ya da içini bir daralmanın kaplaması, zihninin ve enerjinin artık dış dünyanın rutininden yorulduğunun işaretidir. "
            "Sana 'biraz dur ve içeri dön' diyor. Hiçbir şey üretmek veya mükemmel olmak zorunda değilsin. "
            "Pencereyi açıp taze bir nefes al, sevdiğin sakin bir bitki çayı demle ve zihninin gürültüsünü sessizliğe bırak."
        )
    # Kaygı / Korku / Endişe Senaryoları
    elif any(k in q for k in ["kaygı", "korku", "endişe", "stres", "kararsız"]):
        return (
            "Zihin kontrol edemediği yarınlar ve belirsizlikler için endişelenirken, beden şu anda güvende olmayı unutur. "
            "Şimdi omuzlarındaki o gerginliği serbest bırak, ayak tabanlarının yere bastığı teması hisset. "
            "Şu an bu andasın ve güvendesin; her şey kendi ilahi vaktinde yolunu bulacak."
        )
    # Genel Kapsamlı Akıllı Alternatif
    else:
        return (
            f"Paylaştığın '{question}' niyetinin arkasındaki o yoğun duyguyu ve arayışı çok net hissediyorum. "
            f"Hayatın karmaşası içinde bazen yönümüzü kaybetmiş gibi hissetmemiz gayet insani. "
            f"Ancak bil ki içindeki o sessiz pusula, dışarıdaki tüm gürültüye rağmen her zaman en doğru yolu bilir. "
            f"Bugün akışa güven ve kendi iç sesinin şefkatli rehberliğine sığın."
        )

# --- GÖRSEL KARŞILAMA EKRANI ---
st.markdown('<div class="crystal-hero">💎</div>', unsafe_allow_html=True)
st.markdown('<div class="vip-title">VBAR MİSTİK FREKANS</div>', unsafe_allow_html=True)
st.markdown('<div class="vip-subtitle">Sesinin ve ruhunun kristalini keşfet...</div>', unsafe_allow_html=True)

# --- BÖLÜMLER (SEKMELER) ---
tab1, tab2 = st.tabs(["✨ Frekans & Kristal Analizi", "🔮 Mistik Soru-Cevap Rehberi"])

with tab1:
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
    st.write("Aklına takılan bir soruyu, ruhsal durumunu veya paylaşmak istediğin bir hissi buraya yaz; kelimelerinin ardındaki enerjiyi hissedip sana özel, akışkan bir rehberlik oluşturalım.")
    
    user_question = st.text_input("Sormak istediğin soru veya niyetin nedir?", placeholder="Örn: Sevgili aldattı kalbim paramparça / Canım sıkılıyor...")
    
    if st.button("✨ Rehberlik İste"):
        if user_question:
            with st.spinner("Mistik rehberlik hazırlanıyor..."):
                yanit = generate_smart_response(user_question)
                st.session_state.qa_history.append({"soru": user_question, "cevap": yanit})
        else:
            st.warning("Lütfen rehberlik almak istediğin soruyu yaz.")
            
    if st.session_state.qa_history:
        st.markdown("---")
        st.markdown("#### 📜 Geçmiş Rehberlikler")
        for qa in reversed(st.session_state.qa_history):
            st.markdown(f"""
            <div class="qa-card">
                <p><b>Soru:</b> {qa['soru']}</p>
                <p style="color: #f8bbd0; margin-top: 10px;"><b>Rehberlik:</b><br>{qa['cevap']}</p>
            </div>
            """, unsafe_allow_html=True)
