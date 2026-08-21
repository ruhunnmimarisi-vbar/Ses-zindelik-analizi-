import streamlit as st
import librosa
import numpy as np
import io
import noisereduce as nr

# --- SAYFA YAPILANDIRMASI ---
st.set_page_config(page_title="Ruhun Mimarisi | Bütünsel Farkındalık Sentezi", layout="centered", page_icon="🏛️")

st.title("🏛️ Ruhun Mimarisi | VBAR")
st.subheader("Bütünsel Ses ve Enerji Frekansı Analizi")

st.markdown("""
Bu prototip uygulama; ses tonunuzdaki akustik parametreleri (frekans, titreşim ve enerji yoğunluğunu) analiz ederek içsel ritminiz ve zindelik seviyeniz hakkında bütünsel bir farkındalık aynası sunar.
""")

# Veri Sağlama Yöntemi
upload_option = st.radio("Veri Sağlama Yöntemi:", ["Mikrofon ile Kayıt Yap", "Ses Dosyası Yükle"], key="veri_saglama_yontemi")
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
    if st.button("✨ Akustik Analizi ve Sentezi Başlat", key="analiz_baslat_btn"):
        with st.spinner("Ses dalgalarınız ve enerji akışınız çözümleniyor..."):
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
                    st.subheader("🌿 Ruhun Mimarisi | Bütünsel Yansıma")
                    
                    if anlik_f0 < 150:
                        enerji_durumu = "Derin, köklenen ve sükûnet arayan bir ton."
                        tavsiye = "Bugün fiziksel bedeninizle bağınızı güçlendirecek somatic egzersizler ve toprak elementini temsil eden doğal taşlar (Onyx veya Hematit) size denge getirebilir."
                    elif anlik_f0 < 250:
                        enerji_durumu = "Dengeli, akışta ve merkezlenen bir ifade."
                        tavsiye = "İçsel dengeyi korumak adına nefes farkındalığı çalışmaları ve Lapis Lazuli enerjisi zihinsel netliğinizi destekleyebilir."
                    else:
                        enerji_durumu = "Yüksek canlılık, dinamik ve zihinsel hareketlilik."
                        tavsiye = "Bu yüksek enerjiyi dengelemek için su kenarında yürüyüşler yapmak ve zihni sakinleştiren bitki çaylarına yönelmek şifalı olacaktır."

                    st.markdown(f"**Ses Titreşim Analizi:** {enerji_durumu}")
                    st.markdown(f"**Bütünsel Rehberlik:** {tavsiye}")

            except Exception as e:
                st.error(f"Analiz sırasında bir hata oluştu: {e}")
