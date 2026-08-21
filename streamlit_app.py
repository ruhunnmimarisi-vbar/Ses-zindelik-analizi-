import streamlit as st
import librosa
import numpy as np
import io
import os
import noisereduce as nr
import urllib.parse

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
    """)

st.markdown("---")

# --- KİŞİSEL BİLGİLER ---
with st.container(border=True):
    st.subheader("✨ Bilgileriniz")
    ad_soyad = st.text_input("Adınız Soyadınız:")
    col1, col2 = st.columns(2)
    with col1:
        dogum_tarihi_str = st.text_input("Doğum Tarihi:", placeholder="Örn: 29.12.1984")
        dogum_saati_str = st.text_input("Doğum Saati:", placeholder="Örn: 14:30")
    with col2:
        dogum_yeri_str = st.text_input("Doğum Yeri:", placeholder="Örn: İstanbul")

st.markdown("---")

# --- SES ANALİZİ ---
audio_input = st.audio_input("Analiz için sesinizi kaydedin")

if "analiz_yapildi" not in st.session_state:
    st.session_state.analiz_yapildi = False

if audio_input:
    if st.button("✨ Analizi Başlat"):
        try:
            audio_data = audio_input.read()
            y, sr = librosa.load(io.BytesIO(audio_data), sr=16000)
            y_denoised = nr.reduce_noise(y=y, sr=sr, prop_decrease=0.7)
            pitches, _ = librosa.piptrack(y=y_denoised, sr=sr, fmin=80, fmax=400)
            
            st.session_state.f0 = float(np.nanmean(pitches[pitches > 0])) if np.any(pitches > 0) else 210.0
            rms_val = float(np.mean(librosa.feature.rms(y=y_denoised)))
            cent_val = float(np.mean(librosa.feature.spectral_centroid(y=y_denoised, sr=sr)))
            st.session_state.gerilim = (rms_val * 50) + (cent_val / 400)
            
            st.session_state.analiz_yapildi = True
            st.success("Analiz tamamlandı.")
        except Exception as e:
            st.error(f"Ses işleme hatası: {e}")

if st.session_state.analiz_yapildi:
    with st.container(border=True):
        st.subheader("📊 Akustik Sonuçlarınız")
        c1, c2 = st.columns(2)
        c1.metric("Ses Frekansı", f"{st.session_state.f0:.1f} Hz")
        c2.metric("Gerilim İndeksi", f"{st.session_state.gerilim:.2f}")
        
        # Mail Hazırlığı
        mail_konu = "Detaylı VBAR Analiz Talebi"
        mail_govde = f"""Merhabalar,\n\nDetaylı VBAR analizi talep ediyorum.\n\nKişisel Bilgiler:\n- İsim Soyisim: {ad_soyad}\n- Doğum Tarihi: {dogum_tarihi_str}\n- Doğum Saati: {dogum_saati_str}\n- Doğum Yeri: {dogum_yeri_str}\n- Ses Frekansı (F0): {st.session_state.f0:.1f} Hz\n- Gerilim İndeksi: {st.session_state.gerilim:.2f}\n\nDekontum ektedir. Görüşmek dileğiyle."""
        
        mailto_link = f"mailto:Ruhunnmimarisi@gmail.com?subject={urllib.parse.quote(mail_konu)}&body={urllib.parse.quote(mail_govde)}"
        
        st.markdown("---")
        st.write("📩 **Tüm verilerinizle mail gönderin:**")
        st.link_button("🚀 Analiz Talebini Gönder", mailto_link)

st.markdown("---")

# --- DETAYLI ANALİZ DANIŞMANLIĞI ---
with st.container(border=True):
    st.subheader("🔮 Detaylı Bireysel Analiz")
    st.metric("Detaylı Analiz Ücreti", "₺100")
    st.write("1. **Ücret ve Talep:** Detaylı analiz için ödeme yaptıktan sonra, yukarıdaki butonu kullanarak verilerinizi ve dekontunuzu doğrudan bana iletebilirsiniz.")
    st.write("📩 **İletişim:** `Ruhunnmimarisi@gmail.com`")
