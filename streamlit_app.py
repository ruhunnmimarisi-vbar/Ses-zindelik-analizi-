import streamlit as st
import librosa
import numpy as np
import io
import os
import urllib.parse

# --- SAYFA YAPILANDIRMASI ---
st.set_page_config(page_title="Ruhun Mimarisi | VBAR Biyometrik Analiz", layout="centered", page_icon="🔬")

st.markdown("""
<style>
    .stApp {background-color: #0e1117; color: #e0e0e0;}
    .report-box {border: 1px solid #ffd700; padding: 20px; border-radius: 10px; background: #1a1a1a; margin-top: 15px;}
</style>
""", unsafe_allow_html=True)

# KURUMSAL BAŞLIK
st.title("🔬 Ruhun Mimarisi | VBAR Terminali")
st.markdown("*Sesiniz; zihninizin, duygularınızın ve sinir sistemi durumunuzun en saf fiziksel imzasıdır.*")
st.markdown("---")

# 1. ADIM: SES KAYDI VEYA DOSYA YÜKLEME ALANI
st.subheader("1. Aşama: Ses Verisi Girişi")
upload_option = st.radio("Ses Verisi Sağlama Yöntemi:", ["Mikrofon ile Kayıt Yap", "Ses Dosyası Yükle (.mp3, .wav)"])

audio_bytes = None

if upload_option == "Mikrofon ile Kayıt Yap":
    audio_file = st.audio_input("Lütfen 5-10 saniye boyunca konuşun veya sesinizi kaydedin")
    if audio_file:
        audio_bytes = audio_file.read()
else:
    uploaded_file = st.file_uploader("Ses dosyanızı yükleyin", type=["mp3", "wav", "m4a"])
    if uploaded_file:
        audio_bytes = uploaded_file.read()

# Oturumda verileri tutmak için
if "f0_val" not in st.session_state:
    st.session_state.f0_val = 0.0
if "zcr_val" not in st.session_state:
    st.session_state.zcr_val = 0.0

# 2. ADIM: ANALİZ VE MÜDAHALE
if audio_bytes:
    st.audio(audio_bytes, format="audio/mp3")
    
    if st.button("🚀 Biyometrik Analizi Başlat"):
        y, sr = librosa.load(io.BytesIO(audio_bytes), sr=16000)
        pitches, _ = librosa.piptrack(y=y, sr=sr, fmin=80, fmax=400)
        st.session_state.f0_val = float(np.nanmean(pitches[pitches > 0])) if np.any(pitches > 0) else 210.0
        st.session_state.zcr_val = float(np.mean(librosa.feature.zero_crossing_rate(y)))
        
        st.markdown(f"""
        <div class="report-box">
            <h3>Biyometrik Ölçüm Raporu</h3>
            <p><b>Temel Frekans (F0):</b> {st.session_state.f0_val:.1f} Hz</p>
            <p><b>Gerginlik İndeksi:</b> {st.session_state.zcr_val:.4f}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Somatik Rahatlama Modülü
        if st.session_state.zcr_val > 0.12:
            st.warning("⚠️ Ses frekansınızda zihinsel yoğunluk tespit edildi. Dinlendirici somatik akış başlatılıyor:")
            if os.path.exists("rahatlama .mp3"):
                st.audio("rahatlama .mp3", format="audio/mp3")
            else:
                st.error("⚠️ 'rahatlama .mp3' dosyası klasörde bulunamadı.")
        else:
            st.success("✅ Enerjiniz dengeli ve akışta.")

# 3. ADIM: TEK TIKLA E-POSTA OLUŞTURMA (Şifresiz, Harici Servissiz)
st.markdown("---")
with st.form("iletisim_formu"):
    st.subheader("📩 Ruhun Mimarisi - Uzman Raporu Talep Et")
    st.write("Analiz sonuçlarınızın değerlendirilmesi ve size özel rehberlik için bilgilerinizi bırakın.")
    
    ad_soyad = st.text_input("Adınız Soyadınız")
    kullanici_mail = st.text_input("E-posta Adresiniz")
    
    hedef_eposta = "ruhunnmimarisi@gmail.com"
    
    submitted = st.form_submit_button("Raporu Hazırla ve Gönder")
    if submitted:
        if ad_soyad and kullanici_mail:
            # E-posta içeriğini otomatik hazırlıyoruz
            konu = f"VBAR Analiz Talebi - {ad_soyad}"
            govde = f"Ad Soyad: {ad_soyad}\nE-posta: {kullanici_mail}\n\nÖlçüm Sonuçları:\n- Temel Frekans (F0): {st.session_state.f0_val:.1f} Hz\n- Gerginlik İndeksi: {st.session_state.zcr_val:.4f}"
            
            # Bağlantıyı güvenli formatta kodluyoruz
            mailto_link = f"mailto:{hedef_eposta}?subject={urllib.parse.quote(konu)}&body={urllib.parse.quote(govde)}"
            
            st.success("✅ Raporunuz başarıyla hazırlandı! Aşağıdaki bağlantıya tıklayarak doğrudan e-posta uygulamanız üzerinden gönderebilirsiniz:")
            st.markdown(f'<a href="{mailto_link}" target="_blank" style="display:inline-block;background:#ffd700;color:#000;padding:10px 20px;border-radius:5px;font-weight:bold;text-decoration:none;margin-top:10px;">📬 E-Posta Uygulamasını Aç ve Gönder</a>', unsafe_allow_html=True)
        else:
            st.error("Lütfen adınızı ve e-posta adresinizi eksiksiz doldurun.")
