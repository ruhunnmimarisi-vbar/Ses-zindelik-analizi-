import streamlit as st
import librosa
import numpy as np
import io
import os
import noisereduce as nr

st.set_page_config(page_title="Ruhun Mimarisi | VBAR", layout="centered", page_icon="🏛️")

# --- BAŞLIK GÖRSELİ (LOGOYU KESİNLİKLE UNUTMUYORUZ) ---
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

# DOĞUM BİLGİLERİ VE KONUM
with st.container(border=True):
    st.subheader("✨ Kozmik Yapı ve Konum")
    col1, col2 = st.columns(2)
    yukselen_burc = col1.selectbox("Yükselen Burcunuz:", ["Koç", "Boğa", "İkizler", "Yengeç", "Aslan", "Başak", "Terazi", "Akrep", "Yay", "Oğlak", "Kova", "Balık"], index=4)
    dogum_yeri = col2.text_input("Doğum Yeri:", placeholder="Örn: İstanbul")
    st.info(f"Seçilen: **Yükselen {yukselen_burc}** | Konum: **{dogum_yeri if dogum_yeri else 'Belirtilmedi'}**")

st.markdown("---")

# SES ANALİZİ
audio_input = st.audio_input("Analiz için sesinizi kaydedin")
if audio_input and st.button("✨ Analizi Başlat"):
    try:
        audio_data = audio_input.read()
        y, sr = librosa.load(io.BytesIO(audio_data), sr=16000)
        rms = np.mean(librosa.feature.rms(y=y))
        st.success("Analiz tamamlandı.")
        st.write(f"**Yükselen {yukselen_burc}** enerjisi, sesinizin {rms:.4f} enerji yoğunluğu ile dengeleniyor.")
    except Exception as e:
        st.error(f"Ses işleme hatası: {e}")

st.markdown("---")

# DETAYLI ANALİZ DANIŞMANLIĞI
with st.container(border=True):
    st.subheader("🔮 Detaylı Bireysel Analiz")
    st.write("Doğum haritanızın derinliklerine inen, yaşam döngülerinizi, sesinizin potansiyelini ve somatik ihtiyaçlarınızı içeren **kişiye özel detaylı analiz** için:")
    
    st.markdown("---")
    st.metric("Detaylı Analiz Ücreti", "₺100")
    
    st.write("1. **Ücreti gönderin:** `TR00 0000 0000 0000 0000 0000 00` (Meral Erdil)")
    st.write("2. **Talep edin:** Dekontunuzu ve doğum bilgilerinizi (gün/ay/yıl/saat/dakika/doğum yeri) aşağıdan iletin.")
    
    st.markdown("---")
    st.write("📩 **İletişim:** `Ruhunnmimarisi@gmail.com`")
    st.caption("Not: Gönderilen bilgiler titizlikle incelenip size en kısa sürede detaylı bir sentez raporu olarak geri dönülecektir.")
