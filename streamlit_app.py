import streamlit as st
from streamlit_audio_recorder import st_audio_recorder
import librosa
import numpy as np

st.title("🎙️ Ses Analiz ve Zindelik Uygulaması")
st.write("Butona basın, 5 saniye boyunca konuşun ve analizi görün.")

# Ses Kaydedici Bileşeni
audio_bytes = st_audio_recorder(
    text="Kaydı Başlatmak için Tıklayın",
    recording_color="#e74c3c",
    neutral_color="#95a5a6",
    icon_name="microphone",
    icon_size="3x",
)

if audio_bytes:
    # Kaydedilen sesi bir dosyaya yazalım ki işleyebilelim
    with open('ses_kaydi.wav', 'wb') as f:
        f.write(audio_bytes)
    
    st.audio(audio_bytes, format='audio/wav')
    
    # Sesi işleme (Analiz kısmı buraya gelecek)
    y, sr = librosa.load('ses_kaydi.wav', duration=5.0)
    
    # MFCC Özelliklerini çıkarma (Yapay zeka bu veriyi kullanacak)
    mfccs = np.mean(librosa.feature.mfcc(y=y, sr=sr, n_mfcc=40).T, axis=0)
    
    # Örnek bir analiz sonucu (Daha sonra buraya yapay zeka modelinizi bağlayacağız)
    # Şimdilik "sesin gücü" üzerinden basit bir tahmin gösterelim:
    ses_enerjisi = np.sum(np.abs(y))
    
    st.success("Ses Analiz Edildi!")
    
    # Burayı eğitilmiş modelinize göre değiştireceksiniz
    if ses_enerjisi > 0.5:
        st.write("Durum: **Yüksek Enerji / Heyecanlı**")
    else:
        st.write("Durum: **Sakin / Düşük Enerji**")

    st.write(f"Ses Öznitelik Boyutu: {mfccs.shape}")
    
