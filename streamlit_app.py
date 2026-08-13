import streamlit as st
import librosa
import numpy as np
import io

st.set_page_config(page_title="VBAR - Biyometrik Analiz", page_icon="🎙️")

st.title("🎙️ Vokal Biyometrik Zindelik ve Duygu Analizi")
st.warning("⚠️ Bu bir tedavi/klinik teşhis aracı değildir. Sonuçlar yalnızca kendini gözlemleme amaçlıdır.")

# Ses Kayıt ve Yükleme Alanı
audio_value = st.audio_input("Sesinizi kaydetmek için mikrofona dokunun")
uploaded_file = st.file_uploader("Veya ses dosyası yükleyin", type=["wav", "mp3", "m4a", "ogg", "flac"])

target_audio = audio_value or uploaded_file

if target_audio is not None:
    if st.button("Analiz Et", type="primary", key="analiz_butonu_vbar"):
        try:
            with st.spinner("Gelişmiş biyometrik akustik analiz yapılıyor..."):
                audio_bytes = target_audio.read()
                
                # Sesi 16kHz olarak yüklüyoruz
                y, sr = librosa.load(io.BytesIO(audio_bytes), sr=16000)
                
                # --- 1. Temel Akustik Parametreler ---
                # RMS (Ses Enerjisi / Genlik)
                rms_val = float(np.mean(librosa.feature.rms(y=y)))
                
                # Pitch (Temel Frekans F0)
                pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
                pitch_values = pitches[pitches > 0]
                mean_pitch = float(np.mean(pitch_values)) if len(pitch_values) > 0 else 0.0
                
                # --- 2. Gelişmiş Mikro-Titreme Analizleri (Jitter & Shimmer) ---
                # Jitter: Frekanstaki milisaniyelik sapma/kararsızlık
                if len(pitch_values) > 1:
                    pitch_diffs = np.abs(np.diff(pitch_values))
                    jitter_val = float(np.mean(pitch_diffs) / (mean_pitch + 1e-6))
                else:
                    jitter_val = 0.0
                    
                # Shimmer: Genlikteki (enerji) milisaniyelik kararsızlık
                rms_frames = librosa.feature.rms(y=y)[0]
                if len(rms_frames) > 1:
                    shimmer_val = float(np.mean(np.abs(np.diff(rms_frames))) / (rms_val + 1e-6))
                else:
                    shimmer_val = 0.0

            st.success("✅ Biyometrik analiz tamamlandı!")
            
            # --- Metriklerin Gösterimi ---
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Ses Enerjisi", f"{rms_val:.4f}")
            col2.metric("Frekans (Pitch)", f"{mean_pitch:.1f} Hz")
            col3.metric("Jitter (Titreşim)", f"{jitter_val:.3f}")
            col4.metric("Shimmer (Dalgalanma)", f"{shimmer_val:.3f}")

            st.markdown("---")

            # --- 3. Akustik Matris & Biyometrik Teşhis ---
            st.subheader("💡 Sinir Sistemi & Zindelik Analizi")
            
            # Titreşim Eşiği (Jitter > 0.080 veya Shimmer > 0.400 ise sesteki stres/kararsızlık yüksektir)
            stres_var = jitter_val > 0.080 or shimmer_val > 0.400
            
            if rms_val >= 0.008 and stres_var:
                tahmin = "😫 Zihinsel Yorgunluk / Bıkkınlık ve Gerilim"
                detay = (
                    "Sesinizin enerjisi/yüksekliği (RMS) fazla görünse de sesteki mikro-titreşimler (Jitter/Shimmer) oldukça yüksek. "
                    "Bu durum bedensel canlılıktan ziyade zihinsel yorgunluk, bıkkınlık ve sinir sistemindeki uyarılma/stres eforuna işaret eder."
                )
                st.warning(f"**Baskın Durum:** {tahmin}\n\n_{detay}_")
                
            elif rms_val >= 0.008 and not stres_var:
                tahmin = "😊 Gerçek Canlılık / Yüksek Enerji"
                detay = "Ses enerjiniz yüksek ve vokal titreşimleriniz oldukça kararlı/stabil. Sinir sisteminiz canlı ve yüksek enerjili bir durumda."
                st.success(f"**Baskın Durum:** {tahmin}\n\n_{detay}_")
                
            elif rms_val < 0.008 and stres_var:
                tahmin = "🛌 Fizyolojik ve Bedensel Yorgunluk"
                detay = "Ses enerjiniz düşük ve vokal kontrolünüzde mikro-dalgalanmalar var. Bedeninizin dinlenmeye ihtiyacı olduğunu gösterir."
                st.error(f"**Baskın Durum:** {tahmin}\n\n_{detay}_")
                
            else:
                tahmin = "😐 Nötr / Sakin Rölanti Durumu"
                detay = "Sesinizde dengeli, düşük titreşimli ve stabil bir profil gözlemlendi."
                st.info(f"**Baskın Durum:** {tahmin}\n\n_{detay}_")

        except Exception as e:
            st.error(f"Analiz sırasında bir hata oluştu: {e}")
