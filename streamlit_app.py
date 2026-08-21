import streamlit as st
import librosa
import numpy as np
import io
import os
import noisereduce as nr

st.set_page_config(page_title="Ruhun Mimarisi | VBAR Bütünsel Sentez", layout="centered", page_icon="🏛️")

# VBAR AÇIKLAMASI
with st.expander("🏛️ VBAR Nedir? Bütünsel Farkındalık Aynası"):
    st.markdown("""
    **VBAR (Voice-Body-Astrology Resonance)**, sesinizin frekansı ile gökyüzünün kozmik izdüşümünü sentezleyen bütünsel bir farkındalık aracıdır.
    Sesiniz, o anki duygusal ve fiziksel durumunuzun yansıması; doğum haritanız ise ruhunuzun mimari planıdır.
    VBAR, bu iki frekansı birleştirerek sizi şefkatli bir öz-farkındalık alanına davet eder.
    """)

# DOĞUM BİLGİLERİ VE KONUM
with st.container(border=True):
    st.subheader("✨ Kozmik Yapı ve Konum")
    col1, col2 = st.columns(2)
    
    yukselen_burc = col1.selectbox("Yükselen Burcunuzu Seçin:", 
        ["Koç", "Boğa", "İkizler", "Yengeç", "Aslan", "Başak", "Terazi", "Akrep", "Yay", "Oğlak", "Kova", "Balık"], 
        index=4)
    
    dogum_yeri = col2.text_input("Doğum Yeri (Şehir/Ülke):", placeholder="Örn: İstanbul, Türkiye")
    
    st.info(f"Seçilen Kozmik Yapı: **Yükselen {yukselen_burc}** | Konum: **{dogum_yeri if dogum_yeri else 'Belirtilmedi'}**")

# SES ANALİZİ
audio_input = st.audio_input("Analiz için sesinizi kaydedin")

if audio_input:
    if st.button("✨ Analizi Başlat"):
        try:
            audio_data = audio_input.read()
            y, sr = librosa.load(io.BytesIO(audio_data), sr=16000)
            rms = np.mean(librosa.feature.rms(y=y))
            
            st.success("Analiz tamamlandı.")
            st.write(f"**Yükselen {yukselen_burc}** enerjisi, {dogum_yeri} konumu ve sesinizin {rms:.4f} enerji yoğunluğu ile dengeleniyor.")
        except Exception as e:
            st.error(f"Ses işleme hatası: {e}")

st.markdown("---")

# DETAYLI ANALİZ DANIŞMANLIĞI
with st.container(border=True):
    st.subheader("🔮 Detaylı Bireysel Analiz")
    st.write("""
    Bu sistem size anlık bir farkındalık aynası sunar. Eğer doğum haritanızın derinliklerine inen, yaşam döngülerinizi, 
    sesinizin potansiyelini ve somatik ihtiyaçlarınızı içeren **kişiye özel detaylı bir analiz** isterseniz, 
    size rehberlik etmeye hazırım.
    """)
    
    st.markdown("---")
    st.metric("Detaylı Analiz Ücreti", "₺100")
    
    st.write("Detaylı analiz için aşağıdaki adımları izleyebilirsiniz:")
    st.info("1. **Ücreti Gönderin:** TR00 0000 0000 0000 0000 0000 00 (Meral Erdil)")
    st.write("2. **Analiz Talep Edin:** Dekontunuzu ve doğum bilgilerinizi (gün/ay/yıl/saat/dakika/doğum yeri) aşağıdaki mail adresime iletin.")
    
    st.subheader("📩 İletişim")
    st.markdown("📧 **E-posta:** `Ruhunnmimarisi@gmail.com`")
    st.caption("Not: Gönderilen bilgiler titizlikle incelenip size en kısa sürede detaylı bir sentez raporu olarak geri dönülecektir.")
