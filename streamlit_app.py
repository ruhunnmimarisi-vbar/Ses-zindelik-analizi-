"""
Ses Üzerinden Zindelik & Ruh Hali Analizi (Streamlit sürümü)
-------------------------------------------------------------
Ücretsiz barındırma (Streamlit Community Cloud) için hafif sürüm:
büyük bir öğrenilmiş model indirmek yerine yalnızca librosa ile
çıkarılan akustik özelliklere (perde, enerji, tempo, akıcılık)
dayalı bir "Zindelik Skoru" hesaplar.

ÖNEMLİ: Bu bir tıbbi/klinik teşhis aracı DEĞİLDİR. Sonuçlar yalnızca
kendini gözlemleme ve farkındalık amaçlıdır.
"""

import numpy as np
import librosa
import soundfile as sf
import streamlit as st
import io

TARGET_SR = 16000


# ----------------------------------------------------------------------
# Ses yükleme / hazırlama
# ----------------------------------------------------------------------
def _load_audio(file_bytes):
    """Yüklenen/kaydedilen ses baytlarını mono float32 @16kHz array'e çevirir."""
    data, sr = sf.read(io.BytesIO(file_bytes), dtype="float32")
    if data.ndim > 1:
        data = np.mean(data, axis=1)
    if sr != TARGET_SR:
        data = librosa.resample(data, orig_sr=sr, target_sr=TARGET_SR)
    return data


# ----------------------------------------------------------------------
# Akustik özellik çıkarımı
# ----------------------------------------------------------------------
def _acoustic_features(signal, sr=TARGET_SR):
    signal = librosa.util.normalize(signal)

    f0, voiced_flag, _ = librosa.pyin(
        signal, fmin=librosa.note_to_hz("C2"), fmax=librosa.note_to_hz("C6"), sr=sr
    )
    f0_voiced = f0[~np.isnan(f0)] if f0 is not None else np.array([])

    pitch_mean = float(np.mean(f0_voiced)) if len(f0_voiced) > 0 else 0.0
    pitch_std = float(np.std(f0_voiced)) if len(f0_voiced) > 1 else 0.0

    rms = librosa.feature.rms(y=signal)[0]
    energy_mean = float(np.mean(rms))

    onset_env = librosa.onset.onset_strength(y=signal, sr=sr)
    tempo, _ = librosa.beat.beat_track(onset_envelope=onset_env, sr=sr)
    tempo = float(np.atleast_1d(tempo)[0])

    voiced_ratio = float(np.mean(voiced_flag)) if voiced_flag is not None and len(voiced_flag) else 0.0

    return {
        "pitch_mean": pitch_mean,
        "pitch_std": pitch_std,
        "energy_mean": energy_mean,
        "tempo": tempo,
        "voiced_ratio": voiced_ratio,
    }


# ----------------------------------------------------------------------
# Skor ve yorum
# ----------------------------------------------------------------------
def _vitality_score(acoustic):
    """
    0-100 arası 'Zindelik Skoru'. Tamamen akustik özelliklere dayalı:
      - energy_mean   -> ses gücü, normalize edilmiş        ağırlık 0.35
      - voiced_ratio  -> akıcılık, az duraksama              ağırlık 0.25
      - pitch_std     -> tonlama canlılığı, normalize        ağırlık 0.20
      - tempo         -> konuşma temposu, normalize          ağırlık 0.20
    """
    energy_norm = float(np.clip(acoustic["energy_mean"] * 8, 0, 1))
    pitch_var_norm = float(np.clip(acoustic["pitch_std"] / 60, 0, 1))
    tempo_norm = float(np.clip(acoustic["tempo"] / 160, 0, 1))

    score = (
        0.35 * energy_norm
        + 0.25 * acoustic["voiced_ratio"]
        + 0.20 * pitch_var_norm
        + 0.20 * tempo_norm
    )
    return round(score * 100, 1)


def _yorum_uret(score, acoustic):
    if score >= 70:
        seviye = "Yüksek zindelik"
        aciklama = "Ses tonun enerjik ve akıcı görünüyor; konuşma temponda ve ses gücünde canlılık var."
    elif score >= 45:
        seviye = "Orta zindelik"
        aciklama = "Ne çok düşük ne çok yüksek bir enerji seviyesi görülüyor; sakin ama uyanık bir hal."
    else:
        seviye = "Düşük zindelik"
        aciklama = "Ses tonunda yorgunluk veya düşük enerji izleri var; konuşma temposu ve ses gücü düşük."

    if acoustic["pitch_std"] >= 35:
        ton = "tonlaman oldukça değişken, bu genelde canlı/duygusal bir anlatıma işaret eder"
    else:
        ton = "tonlaman görece düz, bu da sakin veya monoton bir anlatıma işaret edebilir"

    return f"**{seviye}** ({score}/100) — {aciklama} Ayrıca {ton}."


# ----------------------------------------------------------------------
# Streamlit arayüzü
# ----------------------------------------------------------------------
st.set_page_config(page_title="Ses ile Zindelik Analizi", page_icon="🎙️")

st.title("🎙️ Ses Üzerinden Zindelik & Ruh Hali Analizi")
st.markdown(
    """
    Sesinizden enerji seviyenizi ve genel canlılığınızı tahmin eden bir prototip.
    Mikrofonla kayıt yapabilir veya bir ses dosyası yükleyebilirsiniz
    (3-15 saniye, doğal konuşma önerilir).

    ⚠️ **Bu bir tıbbi/klinik teşhis aracı değildir.** Sonuçlar yalnızca
    kendini gözlemleme amaçlıdır.
    """
)

tab1, tab2 = st.tabs(["🎤 Mikrofon ile kaydet", "📁 Dosya yükle"])

audio_bytes = None
with tab1:
    mic_input = st.audio_input("Konuş ve kaydet")
    if mic_input is not None:
        audio_bytes = mic_input.read()
import streamlit as st
import librosa
import io

st.title("Ses Zindelik Analizi")
st.warning("⚠️ Bu bir tedavi/klinik teşhis aracı değildir. Sonuçları yalnızca kendini gözlemleme amaçlanmaktadır.")

# 1. MİKROFON İLE DOĞRUDAN KAYIT (YENİ EKLENEN KISIM)
audio_value = st.audio_input("Sesinizi kaydetmek için mikrofona dokunun")

# 2. DOSYA YÜKLEME
uploaded_file = st.file_uploader("Veya ses dosyası yükleyin", type=["wav", "mp3", "m4a", "3ga", "ogg", "flac"])

# Hangisi doluysa onu hedef ses yapıyoruz
target_audio = audio_value or uploaded_file

if target_audio is not None:
    if st.button("Analiz Et", type="primary"):
        try:
            # Sesi arka planda okuma
            audio_bytes = target_audio.read()
            y, sr = librosa.load(io.BytesIO(audio_bytes), sr=None)
            
            # -------------------------------------------------------------
            # BURADAN SONRASI SİZİN MEVCUT KODLARINIZ OLMALI:
            # (Frekans hesaplamaları, zindelik skorları, grafikler vb.)
            # -------------------------------------------------------------
            
        except Exception as e:
            st.error(f"Ses işlenirken bir hata oluştu: {e}")
            
with tab2:
    uploaded_file = st.file_uploader("Ses dosyası seç (wav, mp3, m4a...)", type=None)
    if uploaded_file is not None:
        audio_bytes = uploaded_file.read()

if audio_bytes is not None:
    if st.button("Analiz Et", type="primary"):
        with st.spinner("Ses analiz ediliyor..."):
            try:
                signal = _load_audio(audio_bytes)
            except Exception as e:
                st.error(f"Ses dosyası okunamadı: {e}")
                st.stop()

            if len(signal) < TARGET_SR * 0.5:
                st.warning("Ses çok kısa görünüyor, lütfen en az 1-2 saniyelik bir kayıt sağlayın.")
                st.stop()

            acoustic = _acoustic_features(signal)
            score = _vitality_score(acoustic)
            yorum = _yorum_uret(score, acoustic)

        st.metric("Zindelik Skoru", f"{score} / 100")
        st.markdown(yorum)

        with st.expander("Detaylı akustik metrikler"):
            st.json({
                "Ortalama perde (Hz)": round(acoustic["pitch_mean"], 1),
                "Perde değişkenliği (Hz)": round(acoustic["pitch_std"], 1),
                "Ortalama ses enerjisi": round(acoustic["energy_mean"], 4),
                "Tahmini tempo": round(acoustic["tempo"], 1),
                "Seslendirilmiş oran": round(acoustic["voiced_ratio"], 3),
            })

st.markdown(
    """
    ---
    **Nasıl çalışıyor?** Zindelik skoru; perde (pitch), ses enerjisi (RMS),
    konuşma temposu ve akıcılık gibi akustik özelliklerden ağırlıklı bir
    birleşimle hesaplanıyor.
    """
)
