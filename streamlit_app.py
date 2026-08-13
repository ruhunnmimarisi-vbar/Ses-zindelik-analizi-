import streamlit as st
import librosa
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
            
            # --- 1. Temel Akustik Analiz (Zindelik & Genlik) ---
            y, sr = librosa.load(io.BytesIO(audio_bytes), sr=None)
            duration = librosa.get_duration(y=y, sr=sr)
            
            st.success("Ses başarıyla işlendi!")
            st.write(f"⏱️ **Ses Süresi:** {duration:.2f} saniye")

            # --- 2. Duygu Tanıma Analizi (Transformers) ---
            with st.spinner("Duygu analizi yapılıyor..."):
                classifier = load_emotion_model()
                # Duygu tahminini çalıştırıyoruz
                emotion_results = classifier(audio_bytes)
                
            st.subheader("🎭 Tahmin Edilen Duygu Durumu")
            # En yüksek olasılıklı duyguyu göster
            top_emotion = emotion_results[0]
            st.info(f"**Dominant Duygu:** {top_emotion['label'].upper()} (Güven Oranı: %{top_emotion['score']*100:.1f})")

        except Exception as e:
            st.error(f"Analiz sırasında bir hata oluştu: {e}")
            
