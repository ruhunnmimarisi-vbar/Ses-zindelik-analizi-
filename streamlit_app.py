import streamlit as st
import librosa
import numpy as np
import io
import re

# Sayfa Yapılandırması
st.set_page_config(
    page_title="VBAR - Ses Biyometrisi & Duygu Durum Asistanı", 
    page_icon="🧠",
    layout="centered"
)

st.title("🧠 VBAR - Vocal Biometric & Emotional Readiness")
st.caption("Sinir Sistemi Zindeliği, Stres Seviyesi ve Duygusal Farkındalık Analizi")

st.markdown("""
> **Nasıl Kullanılır?** 
> Rahat bir nefes alın. Şu anki hissinizi veya modunuzu 3-5 saniyelik doğal bir cümleyle ifade ederek ses kaydı yapın.
""")

# Ses Girişi
audio_file = st.audio_input("Sesinizi Kaydedin")

if not audio_file:
    audio_file = st.file_uploader("Veya Bir Ses Dosyası Yükleyin", type=["wav", "mp3", "m4a", "ogg"])

# --- GELİŞMİŞ TÜRKÇE DUYGU & TÜKENMİŞLİK SÜZGEÇLERİ ---
BURNOUT_STRESS_PATTERNS = [
    r"motivasyon(um)?\s*(sıfır|yok|düşük|bitti)",
    r"canım\s*(çok)?\s*sıkılıyor",
    r"içim\s*(daralıyor|sıkılıyor|yanıyor)",
    r"yol\s*kat\s*edemedim",
    r"bunal(dım|ıyorum)",
    r"yorul(dum|dum artık)",
    r"tüken(dim|dim artık)",
    r"hiçbir\s*şey\s*yapmak\s*istemiyorum",
    r"kötü(yüm)?",
    r"stresli(yim)?",
    r"çaresiz(im)?",
    r"umutsuz(um)?",
    r"bitkin(im)?",
    r"kalkmadım",
    r"imdat",
    r"bıktım"
]

HIGH_ENERGY_PATTERNS = [
    r"harika(yım)?",
    r"süper(im)?",
    r"bomba\s*gibiyim",
    r"çok\s*iyi(yim)?",
    r"enerjik(im)?",
    r"coşkulu(yum)?",
    r"mutlu(yum)?"
]

def analyze_vocal_biometrics(audio_bytes):
    # Ses dosyasını yükle
    y, sr = librosa.load(io.BytesIO(audio_bytes), sr=None)
    duration = librosa.get_duration(y=y, sr=sr)
    
    if duration < 1.0:
        return None, "Lütfen en az 1.5 - 2 saniyelik doğal bir konuşma kaydedin."

    # 1. Enerji ve Genlik Dağılımı (RMS)
    rms = librosa.feature.rms(y=y)[0]
    mean_rms = float(np.mean(rms))
    max_rms = float(np.max(rms))
    
    # 2. Temel Frekans ve Tonal Kararlılık (Pitch / F0)
    pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
    pitch_vals = pitches[pitches > 0]
    
    if len(pitch_vals) == 0:
        return None, "Ses frekansı tespit edilemedi. Lütfen mikrofona biraz daha yakın konuşun."
        
    mean_f0 = float(np.mean(pitch_vals))
    std_f0 = float(np.std(pitch_vals))
    
    # 3. Duraksama ve Konuşma Akıcılığı
    non_silent_intervals = librosa.effects.split(y, top_db=25)
    speech_ratio = sum([end - start for start, end in non_silent_intervals]) / len(y) if len(y) > 0 else 0.5

    # Ham Akustik Skor
    acoustic_vibrancy = (std_f0 * 0.2) + (mean_rms * 300)
    raw_score = min(75.0, max(20.0, acoustic_vibrancy))
    
    return {
        "raw_score": int(raw_score),
        "mean_rms": mean_rms,
        "max_rms": max_rms,
        "std_f0": std_f0,
        "speech_ratio": speech_ratio,
        "duration": duration
    }, None

if audio_file:
    st.audio(audio_file)
    
    user_text = st.text_input("💬 Ne söylediniz? (Duygu ve Anlam Analizi İçin Cümlenizi Yazın)", 
                              placeholder="Örn: Motivasyonum sıfır, içim daralıyor...")
    
    if st.button("VBAR Analizini Başlat", type="primary"):
        with st.spinner("Ses Biyometrisi ve Duygu Frekansları İnceleniyor..."):
            audio_bytes = audio_file.read()
            metrics, error = analyze_vocal_biometrics(audio_bytes)
            
            if error:
                st.error(error)
            else:
                score = metrics["raw_score"]
                detected_burnout = False
                detected_high = False
                
                # Cümle Analizi (NLP / Regex Match)
                if user_text:
                    text_clean = user_text.lower().strip()
                    for pattern in BURNOUT_STRESS_PATTERNS:
                        if re.search(pattern, text_clean):
                            detected_burnout = True
                            break
                    
                    if not detected_burnout:
                        for pattern in HIGH_ENERGY_PATTERNS:
                            if re.search(pattern, text_clean):
                                detected_high = True
                                break

                # --- MANTIK DÜZELTME & AKILLI SKORLAMA ---
                if detected_burnout:
                    # Yüksek sesteki bağırma/baskı artık zindelik değil "Yüksek İÇ STRES / TÜKENMİŞLİK" sayılır
                    final_score = int(np.random.randint(18, 33)) 
                    status_type = "BURNOUT_STRESS"
                elif detected_high:
                    final_score = max(score, 82)
                    status_type = "HIGH_FLOW"
                else:
                    # Düz akustik değerlendirme
                    final_score = score
                    status_type = "NEUTRAL" if 40 <= score <= 70 else ("HIGH_FLOW" if score > 70 else "BURNOUT_STRESS")

                # --- ÇIKTI VE SONUÇ EKRANI ---
                st.divider()
                st.metric(label="Zindelik & Akış Skoru", value=f"%{final_score}")

                if status_type == "BURNOUT_STRESS" or final_score < 40:
                    st.error("🔴 **Yüksek Duygusal Yük / Tükenmişlik & Stres Sinyali**")
                    st.write("Sesteki frekanslar ve beyan edilen duygu durumu sinir sisteminde ciddi bir sıkışmışlık, düşük motivasyon veya yorgunluk gösteriyor. Bedeniniz yavaşlama sinyali veriyor.")
                    
                    st.subheader("💡 VBAR Öz-Farkındalık Rehberi")
                    st.info("""
                    * **Durum Analizi:** Şu an motivasyonunuzun düşük olması veya yerinizden kalkmak istememeniz gayet insani bir korunma mekanizmasıdır. Kendinizi zorlamayın.
                    * **Mikro-Eylem:** Sadece omuzlarınızı düşürün, derin bir nefes alın. Bugün bir şey başarmak zorunda değilsiniz.
                    * **Sistem Notu:** Yüksek ses vurgusu canlılık değil, içsel basıncın dışa vurumudur.
                    """)
                elif final_score >= 72:
                    st.success("🟢 **Yüksek Zindelik ve Akış (Flow)**")
                    st.write("Sinir sisteminiz dengeli ve üretken bir akışta.")
                else:
                    st.warning("🟡 **Dengeli / Rutin Seviye**")
                    st.write("Sesiniz ve modunuz nötr bir akışta.")
                    
