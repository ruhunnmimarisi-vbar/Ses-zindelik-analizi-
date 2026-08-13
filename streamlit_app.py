import streamlit as st
import librosa
import numpy as np
import io

# 1. Hugging Face Duygu Tanıma Modeli (Transformers)
from transformers import pipeline

# Modeli belleğe alıyoruz (Sayfa her yenilendiğinde tekrar tekrar yüklemesin diye cache kullanıyoruz)
@st.cache_resource
def load_emotion_model():
    return pipeline("audio-classification", model="jonatasgrosman/wav2vec2-large-xlsr-53-emotion")

st.title("Vokal Biyometrik Zindelik ve Duygu Analizi")
st.warning("⚠️ Bu bir tedavi/klinik teşhis aracı değildir. Sonuçlar yalnızca kendini gözlemleme amaçlıdır.")

# Ses Kayıt ve Yükleme Alanı
audio_value = st.audio_input("Sesinizi kaydetmek için mikrofona dokunun")
uploaded_file = st.file_uploader("Veya ses dosyası yükleyin", type=["wav", "mp3", "m4a", "3ga", "ogg", "flac"])

target_audio = audio_value or uploaded_file

if target_audio is not None:
    if st.button("Analiz Et", type="primary", key="analiz_butonu_vbar"):
        try:
            audio_bytes = target_audio.read()
            
            # --- 1. Akustik ve Zindelik Analizi ---
            y, sr = librosa.load(io.BytesIO(audio_bytes), sr=None)
            
            # Ses Enerjisi (RMS / Genlik)
            rms_val = float(np.mean(librosa.feature.rms(y=y)))
            # MFCC
            mfcc_val = float(np.mean(librosa.feature.mfcc(y=y, sr=sr)))
            
            st.success("Ses başarıyla analiz edildi!")
            
            st.write(f"**Ses Enerjisi (Genlik):** {rms_val:.4f}")
            st.write(f"**Mel-Frekans Katsayısı (MFCC Ort.):** {mfcc_val:.2f}")
            
            # Zindelik Değerlendirmesi
            if rms_val < 0.005:
                zindelik_yorum = "💡 **Anlık Zindelik Yorumu:** Parasempatik Sinir Sistemi Baskın (Sakin/Düşük Enerji): Ses tonunuz dingin veya hafif bir fizyolojik yorgunluk işaret ediyor. Rölanti veya dinlenme durumundasınız."
            else:
                zindelik_yorum = "💡 **Anlık Zindelik Yorumu:** Sempatik Sinir Sistemi Baskın (Canlı/Yüksek Enerji): Sesinizde aktif, dinamik ve yüksek enerjili bir ses kullanımı tespit edildi."
            
            st.info(zindelik_yorum)

            # --- 2. Duygu Tanıma Analizi (Transformers) ---
            with st.spinner("Duygu analizi yapılıyor..."):
                classifier = load_emotion_model()
                emotion_results = classifier(audio_bytes)
                
            st.subheader("🎭 Tahmin Edilen Duygu Durumu")
            top_emotion = emotion_results[0]
            st.info(f"**Dominant Duygu:** {top_emotion['label'].upper()} (Güven Oranı: %{top_emotion['score']*100:.1f})")

        except Exception as e:
            st.error(f"Analiz sırasında bir hata oluştu: {e}")
            
