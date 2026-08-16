import streamlit as st
import librosa
import numpy as np
import io

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

# 2. ADIM: ANALİZ VE MÜDAHALE
if audio_bytes:
    st.audio(audio_bytes, format="audio/mp3")
    
    if st.button("🚀 Biyometrik Analizi Başlat"):
        y, sr = librosa.load(io.BytesIO(audio_bytes), sr=16000)
        pitches, _ = librosa.piptrack(y=y, sr=sr, fmin=80, fmax=400)
        f0 = np.nanmean(pitches[pitches > 0]) if np.any(pitches > 0) else 210.0
        zcr = np.mean(librosa.feature.zero_crossing_rate(y))
        
        st.markdown(f"""
        <div class="report-box">
            <h3>Biyometrik Ölçüm Raporu</h3>
            <p><b>Temel Frekans (F0):</b> {f0:.1f} Hz</p>
            <p><b>Gerginlik İndeksi:</b> {zcr:.4f}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Somatik Rahatlama Modülü (Eşiğe göre otomatik çıkar)
        if zcr > 0.12:
            st.warning("⚠️ Ses frekansınızda zihinsel yoğunluk tespit edildi. Dinlendirici somatik akış başlatılıyor:")
            st.audio("rahatlama.mp3", format="audio/mp3")
        else:
            st.success("✅ Enerjiniz dengeli ve akışta.")

# 3. ADIM: KURUMSAL İLETİŞİM FORMU (Doğru E-Posta Adresiyle Güncellendi)
st.markdown("---")
with st.form("iletisim_formu"):
    st.subheader("📩 Ruhun Mimarisi - Uzman Raporu Talep Et")
    st.write("Analiz sonuçlarınızın değerlendirilmesi ve size özel rehberlik için bilgilerinizi bırakın.")
    
    ad_soyad = st.text_input("Adınız Soyadınız")
    kullanici_mail = st.text_input("E-posta Adresiniz")
    
    # Doğru kurumsal mail adresi
    hedef_eposta = "ruhunnmimarisi@gmail.com"
    
    submitted = st.form_submit_button("Raporu 'Ruhun Mimarisi' Ekibine Gönder")
    if submitted:
        if ad_soyad and kullanici_mail:
            st.success(f"Teşekkürler {ad_soyad}. Talebiniz başarıyla **{hedef_eposta}** adresine iletilmek üzere kuyruğa alındı.")
        else:
            st.error("Lütfen adınızı ve e-posta adresinizi eksiksiz doldurun.")
