import streamlit as st
import librosa
import numpy as np
import io
import os
import noisereduce as nr

st.set_page_config(page_title="Ruhun Mimarisi | VBAR", layout="centered", page_icon="🏛️")

# --- BAŞLIK GÖRSELİ ---
if os.path.exists("1783526207831.png"):
    st.image("1783526207831.png", use_container_width=True)

st.title("🏛️ Ruhun Mimarisi | VBAR")
st.subheader("Bütünsel Ses, Enerji ve Farkındalık Analizi")

# VBAR AÇIKLAMASI
with st.expander("🏛️ VBAR Nedir? Bütünsel Farkındalık Aynası"):
    st.markdown("""
    **VBAR (Voice-Body-Astrology Resonance)**, sesinizin frekansı ile gökyüzünün kozmik izdüşümünü sentezleyen bütünsel bir farkındalık aracıdır.
    Sesiniz, o anki duygusal ve fiziksel durumunuzun yansıması; doğum haritanız ise ruhunuzun mimari planıdır.
    VBAR, bu iki frekansı birleştirerek sizi şefkatli bir öz-farkındalık alanına davet eder.
    """)

st.markdown("---")

# --- KİŞİSEL BİLGİLER VE KONUM ---
with st.container(border=True):
    st.subheader("✨ Kozmik Yapı ve Konum")
    ad_soyad = st.text_input("Adınız Soyadınız:")
    col1, col2 = st.columns(2)
    
    with col1:
        yukselen_burc = st.selectbox("Yükselen Burcunuz:", ["Koç", "Boğa", "İkizler", "Yengeç", "Aslan", "Başak", "Terazi", "Akrep", "Yay", "Oğlak", "Kova", "Balık"], index=4)
        dogum_tarihi = st.date_input("Doğum Tarihi")
    
    with col2:
        dogum_yeri = st.text_input("Doğum Yeri (Şehir/Ülke):")
        dogum_saati = st.text_input("Doğum Saati ve Dakikası:")

st.markdown("---")

# --- SES ANALİZİ ---
audio_input = st.audio_input("Analiz için sesinizi kaydedin")

if "analiz_yapildi" not in st.session_state:
    st.session_state.analiz_yapildi = False
    st.session_state.f0 = 0.0
    st.session_state.gerilim = 0.0

if audio_input:
    if st.button("✨ Analizi Başlat"):
        try:
            audio_data = audio_input.read()
            y, sr = librosa.load(io.BytesIO(audio_data), sr=16000)
            y_denoised = nr.reduce_noise(y=y, sr=sr, prop_decrease=0.7)
            pitches, _ = librosa.piptrack(y=y_denoised, sr=sr, fmin=80, fmax=400)
            
            anlik_f0 = float(np.nanmean(pitches[pitches > 0])) if np.any(pitches > 0) else 210.0
            rms_val = float(np.mean(librosa.feature.rms(y=y_denoised)))
            cent_val = float(np.mean(librosa.feature.spectral_centroid(y=y_denoised, sr=sr)))
            gerilim = (rms_val * 50) + (cent_val / 400)
            
            st.session_state.analiz_yapildi = True
            st.session_state.f0 = anlik_f0
            st.session_state.gerilim = gerilim
            
            st.success("Analiz tamamlandı.")
        except Exception as e:
            st.error(f"Ses işleme hatası: {e}")

if st.session_state.analiz_yapildi:
    with st.container(border=True):
        st.subheader("📊 Akustik ve Enerji Sonuçlarınız")
        col_m1, col_m2 = st.columns(2)
        col_m1.metric("Ses Frekansı (F0)", f"{st.session_state.f0:.1f} Hz")
        col_m2.metric("Gerilim / Enerji İndeksi", f"{st.session_state.gerilim:.2f}")
        
        ozet_metin = f"""Merhabalar,\n\nDetaylı VBAR analizi talep ediyorum.\n\nKişisel Bilgiler:\n- İsim Soyisim: {ad_soyad}\n- Doğum Tarihi: {dogum_tarihi}\n- Doğum Saati: {dogum_saati}\n- Doğum Yeri: {dogum_yeri}\n- Yükselen Burç: {yukselen_burc}\n- Ses Frekansı (F0): {st.session_state.f0:.1f} Hz\n- Gerilim İndeksi: {st.session_state.gerilim:.2f}\n\nDekontum ektedir."""
        
        st.markdown("---")
        st.write("📋 **Detaylı Analiz İçin Ön Bilgi Paketi:**")
        st.text_area("Aşağıdaki metni kopyalayıp mailinize yapıştırabilirsiniz:", ozet_metin, height=150)

st.markdown("---")

# --- DETAYLI ANALİZ DANIŞMANLIĞI ---
with st.container(border=True):
    st.subheader("🔮 Detaylı Bireysel Analiz")
    st.write("Doğum haritanızın derinliklerine inen, yaşam döngülerinizi, sesinizin potansiyelini ve somatik ihtiyaçlarınızı içeren **kişiye özel detaylı analiz** için:")
    st.metric("Detaylı Analiz Ücreti", "₺100")
    st.write("1. **Ücreti gönderin:** İlgili hesaba ödemeyi yapın.")
    st.write("2. **Talep edin:** Dekontunuzu ve yukarıdaki **ön bilgi paketini** mail adresime iletin.")
    st.markdown("---")
    st.write("📩 **İletişim:** `Ruhunnmimarisi@gmail.com`")
