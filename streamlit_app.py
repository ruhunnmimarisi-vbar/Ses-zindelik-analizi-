import streamlit as st
import librosa
import numpy as np
import io
import os
import urllib.parse
import noisereduce as nr

# --- SAYFA YAPILANDIRMASI ---
st.set_page_config(page_title="Ruhun Mimarisi | VBAR Biyometrik Analiz", layout="centered", page_icon="🔬")

# ŞIK VE KURUMSAL ARAYÜZ STİLLERİ (Sıcak Tonlar, Krem & Altın & Lacivert)
st.markdown("""
<style>
    .stApp {
        background-color: #fcfbfa;
        color: #2c2c2c;
    }
    .report-box {
        border: 1px solid #d4af37;
        padding: 20px;
        border-radius: 12px;
        background: #ffffff;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        margin-top: 15px;
    }
    .welcome-card {
        background: #fff8e8;
        border-left: 4px solid #d4af37;
        padding: 15px;
        border-radius: 8px;
        font-style: italic;
        color: #4a4a4a;
        margin-bottom: 20px;
    }
    /* Buton ve form estetiği */
    .stButton>button {
        background-color: #1b263b;
        color: #ffffff;
        border-radius: 8px;
        border: none;
        font-weight: bold;
        padding: 10px 20px;
    }
    .stButton>button:hover {
        background-color: #d4af37;
        color: #000000;
    }
</style>
""", unsafe_allow_html=True)

# 1. GÖRSEL BANNER (GitHub'daki görselinin adı)
if os.path.exists("1783526207831.png"):
    st.image("1783526207831.png", use_container_width=True)
else:
    st.title("🔬 Ruhun Mimarisi | VBAR Terminali")

# KARŞILAMA VE VİZYON
st.markdown("""
<div class="welcome-card">
    "Sesiniz; zihninizin, duygularınızın ve sinir sistemi durumunuzun en saf fiziksel imzasıdır." 
    Bu terminal, biyometrik verilerinizi bilimsel temellerle harmanlayarak içsel dengenizi keşfetmeniz için tasarlanmıştır.
</div>
""", unsafe_allow_html=True)

# SEKME YAPISI (Ana Uygulama ve Bilimsel Altyapı)
tab1, tab2 = st.tabs(["🔬 Biyometrik Analiz", "📖 Bilimsel Altyapı & Hakkında"])

with tab2:
    st.subheader("Ruhun Mimarisi ve VBAR Nedir?")
    st.write("""
    **VBAR (Voice-Based Assessment & Regulation)**, insan sesindeki akustik mikro titreşimleri analiz ederek sinir sisteminin o anki yükünü ve gerilim seviyesini objektif bir şekilde ölçen yenilikçi bir araçtır.
    """)
    
    st.markdown("### 🧬 Bilimsel Arka Plan")
    st.markdown("""
    * **Akustik Biyometri:** Ses tellerinin çalışması, solunum mekaniği ve merkezi sinir sistemi birbirleriyle doğrudan etkileşim içerisindedir. Konuşma sırasında ortaya çıkan mikro değişimler, bireyin zihinsel eforunu ve stres yükünü ele verir.
    * **Temel Frekans ($F_0$):** Vokal kıvrımların saniyedeki titreşim hızıdır. Kişinin anlık zihinsel enerjisini ve vokal irtifasını yansıtır.
    * **Gerginlik İndeksi (ZCR):** Ses dalgalarındaki ani değişim ve pürüzlülük oranlarını inceleyerek sinir sistemindeki o anki eforu ve baskıyı matematiksel olarak ortaya koyar.
    """)
    
    st.markdown("### 🧭 Nasıl Kullanılır?")
    st.markdown("""
    1. **Ses Girişi:** Mikrofon yardımıyla 5-10 saniyelik doğal bir ses kaydı gerçekleştirilir.
    2. **Gürültü Filtreleme:** Sistem, ortamdaki arka plan uğultularını spektral algoritmalarla temizleyerek saf vokal imzayı izole eder.
    3. **Ölçüm ve Dengeleme:** Rapor saniyeler içinde oluşturulur. Eğer gerginlik eşiği aşılırsa, sistem somatik akışı ve dinlendirici frekansları devreye sokar.
    """)

with tab1:
    # 1. ADIM: SES VERİSİ GİRİŞİ
    st.subheader("1. Aşama: Ses Verisi Girişi")
    upload_option = st.radio("Ses Verisi Sağlama Yöntemi:", ["Mikrofon ile Kayıt Yap", "Ses Dosyası Yükle (.mp3, .wav)"])

    audio_bytes = None

    if upload_option == "Mikrofon ile Kayıt Yap":
        audio_file = st.audio_input("Lütfen 5-10 saniye boyunca konuşun")
        if audio_file:
            audio_bytes = audio_file.read()
    else:
        uploaded_file = st.file_uploader("Ses dosyanızı yükleyin", type=["mp3", "wav", "m4a"])
        if uploaded_file:
            audio_bytes = uploaded_file.read()

    # Durum yönetimi
    if "f0_val" not in st.session_state: st.session_state.f0_val = 0.0
    if "zcr_val" not in st.session_state: st.session_state.zcr_val = 0.0

    # 2. ADIM: ANALİZ VE GÜRÜLTÜ FİLTRELEME
    if audio_bytes:
        st.audio(audio_bytes, format="audio/mp3")
        
        if st.button("🚀 Gürültü Filtreli Analizi Başlat"):
            with st.spinner("Sesiniz arındırılıyor ve biyometrik veriler analiz ediliyor..."):
                # Ham sesi yükle
                y, sr = librosa.load(io.BytesIO(audio_bytes), sr=16000)
                
                # Gürültü Azaltma Filtresi
                y_denoised = nr.reduce_noise(y=y, sr=sr, prop_decrease=0.7)
                
                # Analiz
                pitches, _ = librosa.piptrack(y=y_denoised, sr=sr, fmin=80, fmax=400)
                st.session_state.f0_val = float(np.nanmean(pitches[pitches > 0])) if np.any(pitches > 0) else 210.0
                st.session_state.zcr_val = float(np.mean(librosa.feature.zero_crossing_rate(y_denoised)))
            
            st.markdown(f"""
            <div class="report-box">
                <h3 style="color: #1b263b; margin-top: 0;">Biyometrik Ölçüm Raporu (Arındırılmış)</h3>
                <p><b>Temel Frekans (F0):</b> {st.session_state.f0_val:.1f} Hz</p>
                <p><b>Gerginlik İndeksi:</b> {st.session_state.zcr_val:.4f}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Somatik Rahatlama Modülü
            if st.session_state.zcr_val > 0.12:
                st.warning("⚠️ Zihinsel yoğunluk tespit edildi. Dinlendirici somatik akış başlatılıyor:")
                if os.path.exists("rahatlama .mp3"):
                    st.audio("rahatlama .mp3", format="audio/mp3")
                else:
                    st.info("💡 Rahatlama ses dosyası aranıyor...")
            else:
                st.success("✅ Enerjiniz dengeli ve akışta.")

    # 3. ADIM: E-POSTA GÖNDERME
    st.markdown("---")
    st.subheader("📩 Uzman Raporu Talep Et")
    with st.form("iletisim_formu"):
        ad_soyad = st.text_input("Adınız Soyadınız")
        kullanici_mail = st.text_input("E-posta Adresiniz")
        submitted = st.form_submit_button("Raporu Hazırla")
        
        if submitted:
            if ad_soyad and kullanici_mail:
                konu = f"VBAR Analiz Talebi - {ad_soyad}"
                govde = f"Ad Soyad: {ad_soyad}\nE-posta: {kullanici_mail}\n\nÖlçüm Sonuçları:\n- F0: {st.session_state.f0_val:.1f} Hz\n- Gerginlik: {st.session_state.zcr_val:.4f}"
                mailto_link = f"mailto:ruhunnmimarisi@gmail.com?subject={urllib.parse.quote(konu)}&body={urllib.parse.quote(govde)}"
                st.markdown(f'<a href="{mailto_link}" target="_blank" style="display:inline-block;background:#1b263b;color:#fff;padding:10px 20px;border-radius:8px;font-weight:bold;text-decoration:none;margin-top:10px;">📬 E-Posta Uygulamasını Aç ve Gönder</a>', unsafe_allow_html=True)
            else:
                st.error("Lütfen adınızı ve e-posta adresinizi eksiksiz doldurun.")
