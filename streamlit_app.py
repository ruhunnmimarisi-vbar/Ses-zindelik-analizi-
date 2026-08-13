import streamlit as st
import librosa
import numpy as np
import io

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
> Rahat bir nefes alın. Şu anki hissinizi, modunuzu veya gününüzün nasıl geçtiğini 3-5 saniyelik doğal bir cümleyle ifade edin.
""")

# Ses Girişi
audio_file = st.audio_input("Sesinizi Kaydedin")

if not audio_file:
    audio_file = st.file_uploader("Veya Bir Ses Dosyası Yükleyin", type=["wav", "mp3", "m4a", "ogg"])

# Olumsuz ve Stres Sinyali Veren Anahtar Kelimeler (Duygu Durum Filtresi)
STRESS_KEYWORDS = [
    "daralıyor", "daraldı", "sıkkın", "bunalıyorum", "bunaldım", "yorgunum", 
    "kötüyüm", "bitkinim", "stresliyim", "üzgünüm", "tıkandım", "imdat", "of"
]

HIGH_ENERGY_KEYWORDS = [
    "harikayım", "süperim", "bomba gibiyim", "çok iyiyim", "enerjik", "coşkulu", "mutluyum"
]

def analyze_vocal_biometrics(audio_bytes):
    # Ses dosyasını yükle
    y, sr = librosa.load(io.BytesIO(audio_bytes), sr=None)
    duration = librosa.get_duration(y=y, sr=sr)
    
    if duration < 1.2:
        return None, "Lütfen en az 2 saniyelik doğal bir konuşma kaydedin."

    # 1. Enerji ve Genlik Dağılımı (RMS)
    rms = librosa.feature.rms(y=y)[0]
    mean_rms = float(np.mean(rms))
    std_rms = float(np.std(rms)) # Sesin dalgalanması (monotonluk kontrolü)
    
    # 2. Temel Frekans ve Tonal Kararlılık (Pitch / F0)
    pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
    pitch_vals = pitches[pitches > 0]
    
    if len(pitch_vals) == 0:
        return None, "Ses frekansı tespit edilemedi. Lütfen mikrofona daha yakın konuşun."
        
    mean_f0 = float(np.mean(pitch_vals))
    std_f0 = float(np.std(pitch_vals)) # Tonal zenginlik / Donukluk ölçütü
    
    # 3. Duraksama ve Konuşma Akıcılığı (Silence Analysis)
    non_silent_intervals = librosa.effects.split(y, top_db=25)
    speech_ratio = sum([end - start for start, end in non_silent_intervals]) / len(y)

    # --- GELİŞMİŞ BİYOMETRİK PUANLAMA METODOLOJİSİ ---
    # Sadece yüksek desibel değil; frekans esnekliği ve konuşma akıcılığı puanlanır.
    
    # Akustik Canlılık Puanı (0 - 60 puan arası)
    acoustic_vibrancy = (std_f0 * 0.25) + (std_rms * 500)
    acoustic_score = min(60.0, max(10.0, acoustic_vibrancy))
    
    # Akıcılık Puanı (0 - 40 puan arası)
    fluency_score = speech_ratio * 40.0
    
    # Ham Biyometrik Skor (0 - 100)
    raw_score = acoustic_score + fluency_score
    
    return {
        "raw_score": int(raw_score),
        "mean_rms": mean_rms,
        "std_f0": std_f0,
        "speech_ratio": speech_ratio,
        "duration": duration
    }, None

if audio_file:
    st.audio(audio_file)
    
    # Kullanıcıya duygu beyanı imkanı (Gerçekçi hibrit analiz için)
    user_text = st.text_input("💬 Cümleniz neydi? (Opsiyonel - Duygu Analizini Hassaslaştırır)", 
                              placeholder="Örn: Çok canım sıkkın içim daralıyor...")
    
    if st.button("VBAR Biyometrik Analizi Başlat", type="primary"):
        with st.spinner("Nöro-Akustik Frekanslar ve Ses Biyometrisi İşleniyor..."):
            audio_bytes = audio_file.read()
            metrics, error = analyze_vocal_biometrics(audio_bytes)
            
            if error:
                st.error(error)
            else:
                score = metrics["raw_score"]
                
                # --- DUYGU VE ANLAM DÜZELTMESİ (NLP / Sentiment Override) ---
                detected_stress = False
                detected_high = False
                
                if user_text:
                    text_lower = user_text.lower()
                    if any(word in text_lower for word in STRESS_KEYWORDS):
                        detected_stress = True
                    elif any(word in text_lower for word in HIGH_ENERGY_KEYWORDS):
                        detected_high = True
                
                # Eğer kullanıcı olumsuz/stresli bir cümle belirttiyse, yüksek ses enerjisi "Baskı/Stres" olarak yorumlanır!
                if detected_stress:
                    final_score = min(score, 38) # Puan otomatik olarak yorgunluk/stres bandına çekilir
                elif detected_high:
                    final_score = max(score, 78)
                else:
                    final_score = score

                # --- EKRAN ÇIKTILARI VE REHBERLİK ---
                st.divider()
                
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.metric(label="Zindelik & Akış Skoru", value=f"%{final_score}")
                
                with col2:
                    if final_score >= 75:
                        st.success("🟢 **Yüksek Zindelik ve Akış (Flow)**")
                        st.write("Sinir sisteminiz dengeli, ses telleri esnek ve tonal zenginlik yüksek. Günün üretken işleri için harika bir an.")
                    elif final_score >= 45:
                        st.warning("🟡 **Dengeli / Nötr Seviye**")
                        st.write("Sesiniz stabil bir akışta. Ne aşırı yorgunluk ne de yüksek coşku sinyali var. Rutin faaliyetler için uygun.")
                    else:
                        st.error("🔴 **Yüksek Stres / Sıkışmışlık Sinyali**")
                        st.write("Sesteki frekanslar sinir sisteminde yorgunluk, daralma veya baskı olduğunu gösteriyor. Bedeniniz yavaşlama sinyali veriyor.")

                # --- MENTÖRLÜK / WELLNESS REHBERLİĞİ ---
                st.subheader("💡 VBAR Öz-Farkındalık Rehberi")
                
                if final_score < 45:
                    st.info("""
                    * **Önerilen Eylem:** Şu an zihniniz veya bedeniniz bir sıkışma hissediyor olabilir. 
                    * **Mikro-Ritüel:** Omuzlarınızı serbest bırakın. 4 saniye nefes alın, 7 saniye tutun, 8 saniyede yavaşça verin (4-7-8 Nefesi). 
                    * **Not:** Zihinsel daralma anlarında yüksek ses çıkarmak zindelik değil, sinir sisteminin deşarj olma çabasıdır.
                    """)
                elif final_score >= 75:
                    st.info("""
                    * **Önerilen Eylem:** Enerjinizi yaratıcı bir projeye veya odak gerektiren bir iletişime aktarın.
                    * **Mikro-Ritüel:** Bu yüksek akış halini korumak için su tüketiminizi destekleyin.
                    """)
                else:
                    st.info("""
                    * **Önerilen Eylem:** Kısa bir mola verip temponuzu gözden geçirin.
                    """)
                    
