import streamlit as st
from audio_recorder_streamlit import audio_recorder
import librosa
import numpy as np

# Page Configuration
st.set_page_config(page_title="Vokal Biyomarker & Zindelik Analizi", page_icon="🎙️")

st.title("🎙️ Vokal Biyomarker & Zindelik Analizi")
st.write(
    "Ses tonunuz, otonom sinir sisteminizin ve zihinsel yorgunluğunuzun anlık aynasıdır. "
    "Aşağıdaki mikrofona tıklayarak yaklaşık 5 saniyelik bir ses kaydı yapın."
)

st.divider()

# 1. Ses Kayıt Alanı
st.subheader("1. Sesinizi Kaydedin")
audio_bytes = audio_recorder(
    text="Kayda başlamak/durdurmak için ikona tıklayın",
    recording_color="#e74c3c",
    neutral_color="#3498db",
    icon_size="3x",
)

# 2. Ses Kaydedildiğinde Çalışacak Kısım
if audio_bytes:
    # Kaydedilen sesi oynatıcıda göster
    st.audio(audio_bytes, format="audio/wav")
    
    # Sesi geçici olarak dosyaya yaz
    with open("temp_audio.wav", "wb") as f:
        f.write(audio_bytes)
    
    st.divider()
    st.subheader("2. Akustik Analiz ve Tahmin")
    
    with st.spinner("Ses parametreleriniz çıkarılıyor ve analiz ediliyor..."):
        try:
            # Sesi librosa ile yükle (ilk 5 saniyesi)
            y, sr = librosa.load("temp_audio.wav", duration=5.0)
            
            # Akustik Öznitelik Çıkarımı (Yapay Zeka Modeline Gidecek Veriler)
            mfccs = np.mean(librosa.feature.mfcc(y=y, sr=sr, n_mfcc=40).T, axis=0)
            pitch = np.mean(librosa.feature.chroma_stft(y=y, sr=sr))
            energy = np.sum(y**2) / len(y)
            
            st.success("Ses başarıyla analiz edildi!")
            
            # Metrikleri Ekrana Bastırma
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric(label="Ses Enerjisi (Genlik)", value=f"{energy:.4f}")
                
            with col2:
                st.metric(label="Mel-Frekans Katsayısı (MFCC Ort.)", value=f"{np.mean(mfccs):.2f}")
            
            # Temsili Sinir Sistemi Denge Değerlendirmesi
            # (Buraya daha sonra eğitilen yapay zeka model.predict() bağlanacak)
            st.info("💡 **Anlık Zindelik Yorumu:**")
            if energy > 0.01:
                st.write(
                    "**Sempatik Sinir Sistemi Baskın (Yüksek Uyarılma):** "
                    "Ses tonunuzda yüksek enerji ve odak tespit edildi. "
                    "Ancak uzun süreli bu seviye zihinsel yorgunluğa yol açabilir."
                )
            else:
                st.write(
                    "**Parasempatik Sinir Sistemi Baskın (Sakin/Düşük Enerji):** "
                    "Ses tonunuz dingin veya hafif bir fizyolojik yorgunluk işaret ediyor. "
                    "Rölanti veya dinlenme durumundasınız."
                )

        except Exception as e:
            st.error(f"Ses işlenirken bir hata oluştu: {e}")
            
