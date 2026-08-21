import streamlit as st
import librosa
import numpy as np
import io
import noisereduce as nr

# --- SAYFA YAPILANDIRMASI ---
st.set_page_config(page_title="Ruhun Mimarisi | VBAR Bütünsel Sentez", layout="centered", page_icon="🏛️")

st.title("🏛️ Ruhun Mimarisi | VBAR")
st.subheader("Bütünsel Ses, Enerji ve Farkındalık Analizi")

st.markdown("""
Bu prototip uygulama; ses tonunuzdaki akustik parametreleri (frekans, titreşim, gerilim) ve burç enerjilerinizi sentezleyerek içsel ritminiz hakkında bütünsel bir farkındalık aynası sunar.
""")

# --- KULLANICI GİRDİLERİ (BURÇ & SES) ---
with st.container(border=True):
    st.subheader("✨ Doğum Haritası / Astrolojik Altyapı")
    col_b1, col_b2, col_b3 = st.columns(3)
    with col_b1:
        gun = st.number_input("Gün", min_value=1, max_value=31, value=29)
    with col_b2:
        ay = st.selectbox("Ay", ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"], index=11)
    with col_b3:
        yil = st.number_input("Yıl", min_value=1940, max_value=2015, value=1984)

    burc_secimi = st.selectbox("Güneş Burcunuz (veya Yükseleniniz)", ["Koç", "Boğa", "İkizler", "Yengeç", "Aslan", "Başak", "Terazi", "Akrep", "Yay", "Oğlak", "Kova", "Balık"], index=9)

st.markdown("---")

# Veri Sağlama Yöntemi (Mobil Uyumludur)
upload_option = st.radio("Ses Verisi Sağlama Yöntemi:", ["Mikrofon ile Kayıt Yap", "Ses Dosyası Yükle"], key="veri_saglama_yontemi")
audio_bytes = None

if upload_option == "Mikrofon ile Kayıt Yap":
    audio_file = st.audio_input("Lütfen konuşun veya sesinizi kaydedin", key="mobil_mikrofon_input")
    if audio_file is not None:
        audio_bytes = audio_file.read()
else:
    uploaded_file = st.file_uploader("Ses dosyanızı seçin", type=["mp3", "wav", "m4a"], key="dosya_yukleme_input")
    if uploaded_file is not None:
        audio_bytes = uploaded_file.read()

st.markdown("---")

if audio_bytes is not None:
    if st.button("✨ Akustik ve Bütünsel Analizi Başlat", key="analiz_baslat_btn"):
        with st.spinner("Ses dalgalarınız ve element dengeniz çözümleniyor..."):
            try:
                # Akustik Hesaplamalar
                y, sr = librosa.load(io.BytesIO(audio_bytes), sr=16000)
                y_denoised = nr.reduce_noise(y=y, sr=sr, prop_decrease=0.7)
                pitches, _ = librosa.piptrack(y=y_denoised, sr=sr, fmin=80, fmax=400)
                
                anlik_f0 = float(np.nanmean(pitches[pitches > 0])) if np.any(pitches > 0) else 210.0
                rms_val = float(np.mean(librosa.feature.rms(y=y_denoised)))
                cent_val = float(np.mean(librosa.feature.spectral_centroid(y=y_denoised, sr=sr)))
                gerilim = (rms_val * 50) + (cent_val / 400)

                # Sonuç Paneli
                with st.container(border=True):
                    st.subheader("🔬 Akustik Biyometrik Rapor")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Ortalama Ses Frekansı (F0)", f"{anlik_f0:.1f} Hz")
                    with col2:
                        st.metric("Gerilim / Enerji İndeksi", f"{gerilim:.2f}")

                # Bütünsel Yorumlar ve Farkındalık Alanı
                with st.container(border=True):
                    st.subheader("🌿 Ruhun Mimarisi | Bütünsel Yansıma ve Sentez")
                    
                    # Burç bazlı element eşleştirmesi
                    elementler = {
                        "Koç": "Ateş", "Aslan": "Ateş", "Yay": "Ateş",
                        "Boğa": "Toprak", "Başak": "Toprak", "Oğlak": "Toprak",
                        "İkizler": "Hava", "Terazi": "Hava", "Kova": "Hava",
                        "Yengeç": "Su", "Akrep": "Su", "Balık": "Su"
                    }
                    secilen_element = elementler.get(burc_secimi, "Toprak")

                    if anlik_f0 < 150:
                        ses_yorumu = "Derin, köklenen, otoriter ve sükûnet arayan bir ton."
                    elif anlik_f0 < 250:
                        ses_yorumu = "Dengeli, akışta, merkezlenen ve şefkatli bir ifade."
                    else:
                        ses_yorumu = "Yüksek canlılık, dinamik, ilham veren ve zihinsel hareketlilik."

                    st.markdown(f"**Burç & Element Matrisi:** {burc_secimi} burcu ({secilen_element} elementi) ile ses titreşiminiz arasındaki uyum haritalandı.")
                    st.markdown(f"**Ses Titreşim Profili:** {ses_yorumu}")
                    
                    # Doğal taş ve şifa önerileri
                    if secilen_element == "Toprak":
                        tas_onerisi = "Onyx, Hematit veya Akik (Topraklanma ve fiziksel zindelik için)"
                    elif secilen_element == "Ateş":
                        tas_onerisi = "Kırmızı Agat veya Obsidyen (İçsel ateşi dengelemek ve koruma için)"
                    elif secilen_element == "Hava":
                        tas_onerisi = "Labradorit veya Beril (Zihinsel odak ve akışkanlık için)"
                    else:
                        tas_onerisi = "Lapis Lazuli veya Akuamarin (Duygusal berraklık ve şifa için)"

                    st.markdown(f"**Önerilen Doğal Taş Desteği:** {tas_onerisi}")
                    st.markdown(f"**Bütünsel Pratik Tavsiyesi:** Bugün somatik nefes çalışmaları ve doğada (veya su kenarında) kısa bir yürüyüş, enerji alanınızı tamamen tazeleyecektir.")

            except Exception as e:
                st.error(f"Analiz sırasında bir hata oluştu: {e}")
