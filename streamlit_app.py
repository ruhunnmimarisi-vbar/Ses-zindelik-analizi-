import streamlit as st
import librosa
import numpy as np
import io

st.set_page_config(page_title="VBAR - Ses Zindelik Analizi", page_icon="🎙️")

st.title("🎙️ VBAR - Ses Zindelik Asistanı")
st.caption("Ses Biyometrisi ile Sinir Sistemi Zindelik & Yorgunluk Analizi")

st.info("💡 **İpucu:** En doğru sonuç için mikrofona eşit mesafede durun ve 3 saniye boyunca coşkulu/canlı bir tonda konuşun veya 'AAAA' deyin.")

audio_file = st.audio_input("Mikrofonla Kayıt Yapın")

if not audio_file:
    audio_file = st.file_uploader("Veya Ses Dosyası Yükleyin", type=["wav", "mp3", "m4a", "ogg"])

if audio_file:
    st.audio(audio_file)
    
    if st.button("Zindelik Analizi Yap", type="primary"):
        with st.spinner("Ses Frekansları ve Sinir Sistemi Vurgusu Analiz Ediliyor..."):
            try:
                audio_bytes = audio_file.read()
                y, sr = librosa.load(io.BytesIO(audio_bytes), sr=None)
                duration = librosa.get_duration(y=y, sr=sr)
                
                if duration < 1.5:
                    st.error("Lütfen en az 2 saniyelik net bir ses kaydı yapın.")
                else:
                    # 1. Enerji Hesaplama (RMS)
                    rms = librosa.feature.rms(y=y)[0]
                    mean_rms = float(np.mean(rms))
                    max_rms = float(np.max(rms))
                    
                    # 2. Frekans ve Tonal Değişim (Pitch - F0)
                    pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
                    pitch_vals = pitches[pitches > 0]
                    
                    std_f0 = float(np.std(pitch_vals)) if len(pitch_vals) > 0 else 0.0
                    mean_f0 = float(np.mean(pitch_vals)) if len(pitch_vals) > 0 else 0.0

                    # 3. Dinamik Skorlama (0 - 100 Aralığını Tam Kullanan Yeni Matematik)
                    # Enerji Puanı (Max %50 katkı)
                    energy_score = min(50.0, (max_rms * 400.0)) 
                    
                    # Tonal Canlılık Puanı (Max %50 katkı)
                    vibrancy_score = min(50.0, (std_f0 * 0.4) + (mean_f0 * 0.05))
                    
                    # Toplam Skor
                    raw_score = energy_score + vibrancy_score
                    
                    # Taban ve tavan dengelemesi
                    final_score = int(min(100, max(15, raw_score)))

                    # --- EKRAN ÇIKTISI VE REHBERLİK ---
                    st.divider()
                    st.metric(label="Zindelik Skoru", value=f"%{final_score}")

                    if final_score >= 75:
                        st.success("🚀 **Yüksek Zindelik & Canlılık (%75 - %100)**\n\n"
                                   "Ses frekanslarınız son derece dinamik ve enerjik. Sinir sisteminiz yüksek akışta! "
                                   "Günün en önemli kararlarını almak ve üretken çalışmak için harika bir an.")
                    elif final_score >= 45:
                        st.warning("🧘 **Dengeli / Orta Zindelik (%45 - %74)**\n\n"
                                   "Sesiniz stabil ve dengeli bir seviyede. Yorgun değilsiniz ancak modunuz rutin bir akışta. "
                                   "Kısa bir yürüyüş veya bitki çayı canlılığınızı artırabilir.")
                    else:
                        st.error("💤 **Düşük Zindelik & Yorgunluk Sinyali (%15 - %44)**\n\n"
                                 "Sesteki enerji ve tonal dalgalanma düşük. Sinir sisteminiz yorgunluk veya monotonluk sinyali veriyor. "
                                 "5 dakika derin nefes egzersizi yapmak ve zihninizi dinlendirmek iyi gelecektir.")

            except Exception as e:
                st.error("Ses analiz edilirken bir hata oluştu. Lütfen tekrar deneyin.")
