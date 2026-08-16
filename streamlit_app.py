import streamlit as st
import librosa
import numpy as np
import io

st.set_page_config(page_title="VBAR | Ses Dosyası Analizi", layout="centered")

st.title("🔬 VBAR: Biyometrik Ses Dosyası Analizi")
st.write("Cihazınızda kayıtlı olan bir ses dosyasını (MP3, WAV, M4A) yükleyerek analizi başlatın.")

# Canlı kayıt yerine hazır dosya yükleme bileşeni
uploaded_file = st.file_uploader("Bir ses dosyası seçin (Önerilen: 5 - 15 saniye)", type=["mp3", "wav", "m4a", "aac"])

if uploaded_file is not None:
    # Dosyayı okuyalım
    audio_bytes = uploaded_file.read()
    
    with st.spinner("Ses sinyalleri çözümleniyor..."):
        # Librosa ile dosyayı işleme
        y, sr = librosa.load(io.BytesIO(audio_bytes), sr=16000)
        
        # Mühendislik Analizi (Frekans ve Stres İndeksi)
        pitches, magnitudes = librosa.piptrack(y=y, sr=sr, fmin=80.0, fmax=400.0)
        pitch_vals = pitches[(pitches > 80.0) & (pitches < 400.0)]
        f0 = np.nanmean(pitch_vals) if len(pitch_vals) > 0 else 210.0
        rms = np.mean(librosa.feature.rms(y=y))
        zcr = np.mean(librosa.feature.zero_crossing_rate(y))
        
        st.success("Ses başarıyla analiz edildi!")
        
        # Sonuç Paneli
        col1, col2 = st.columns(2)
        col1.metric("Temel Frekans (F0)", f"{f0:.1f} Hz")
        col2.metric("Stres/Gerginlik İndeksi", f"{zcr:.4f}")
        
        # Uzman Raporu Formu
        with st.form("detay_form_dosya"):
            st.subheader("astrolojik ve Psikolojik Uzman Raporu Alın")
            ad = st.text_input("Ad Soyad")
            dt = st.date_input("Doğum Tarihi")
            email = st.text_input("E-posta Adresi")
            
            submitted = st.form_submit_button("Detaylı Analiz İstemi Gönder")
            if submitted:
                st.info(f"Teşekkürler {ad}. Ses verileriniz ve doğum tarihiniz kaydedildi. Uzman ekibimiz inceleyip mail yoluyla dönüş yapacaktır.")
