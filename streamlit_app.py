import streamlit as st
import librosa
import numpy as np
import io
import os
import noisereduce as nr
from datetime import datetime

# --- SAYFA YAPILANDIRMASI ---
st.set_page_config(page_title="Ruhun Mimarisi | VBAR Bütünsel Sentez", layout="centered", page_icon="🏛️")

if os.path.exists("1783526207831.png"):
    st.image("1783526207831.png", use_container_width=True)

st.title("🏛️ Ruhun Mimarisi | VBAR")
st.markdown("> *“Sesiniz, iç dünyanızın coğrafyasını ve an’daki frekansınızı fısıldar. Derin bir nefes alın ve içsel Mimarınıza kulak verin.”*")
st.markdown("---")

# --- GELİŞMİŞ ASTROLOJİK HESAPLAMA ---
# Yükselen ve Kadrant hesaplaması için temel bir mantık katmanı (Sadeleştirilmiş Placidus mantığı)
def astrolojik_sentez(gun, ay, yil, saat):
    # Basit bir yükselen tahmini algoritması (Doğum saati ve gün üzerinden)
    saat_faktoru = (saat + (gun / 30)) % 24
    burclar = ["Koç", "Boğa", "İkizler", "Yengeç", "Aslan", "Başak", "Terazi", "Akrep", "Yay", "Oğlak", "Kova", "Balık"]
    yukselen_idx = int(saat_faktoru / 2)
    yukselen = burclar[yukselen_idx]
    
    # Kadrant Analizi (1-3, 4-6, 7-9, 10-12 evler)
    kadrant = "Güney (Dışsal/Sosyal)" if 6 <= saat < 18 else "Kuzey (İçsel/Ruhsal)"
    return yukselen, kadrant

# --- KULLANICI GİRDİLERİ ---
with st.container(border=True):
    st.subheader("✨ Kozmik Zamanlama (Doğum Bilgileri)")
    col1, col2, col3 = st.columns(3)
    gun = col1.number_input("Gün", 1, 31, 29)
    ay = col2.selectbox("Ay", ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"], 11)
    yil = col3.number_input("Yıl", 1940, 2015, 1984)
    saat = st.slider("Doğum Saati", 0, 23, 12)
    
    yukselen, kadrant = astrolojik_sentez(gun, ay, yil, saat)
    st.info(f"Yükselen Burç: **{yukselen}** | Yaşam Kadrantı: **{kadrant}**")

st.markdown("---")

# SES VERİSİ
audio_bytes = st.audio_input("Lütfen analize başlamak için sesinizi kaydedin")

if audio_bytes:
    if st.button("✨ Bütünsel Analizi Başlat"):
        with st.spinner("Ses tınısı ve yıldız haritası sentezleniyor..."):
            try:
                y, sr = librosa.load(io.BytesIO(audio_bytes), sr=16000)
                pitches, _ = librosa.piptrack(y=y, sr=sr)
                anlik_f0 = float(np.nanmean(pitches[pitches > 0])) if np.any(pitches > 0) else 210.0
                
                with st.container(border=True):
                    st.subheader("🌿 Ruhun Mimarisi | Derinlemesine Analiz")
                    st.markdown(f"**Yükseleniniz {yukselen}**'in getirdiği dışsal ifade biçimi ile sesinizin {anlik_f0:.1f} Hz frekansı uyumlanıyor.")
                    st.markdown(f"**Kadrant Analizi:** Şu an {kadrant} kadrantında bir enerji akışına sahipsiniz. Bu durum içsel odaklanmanızın yoğunluğunu gösteriyor.")
                    
                    if yukselen == "Aslan":
                        st.markdown("**Not:** Yükselen Aslan, sesinize otoriter ve parlak bir tını katar; bugün bu parlaklığı kullanma gününüz.")
                    
                    # SOMATİK UYUM (Sadece ihtiyaç anında)
                    if anlik_f0 > 230:
                        st.subheader("🧘 Somatik Uyum ve Arınma")
                        if os.path.exists("rahatlama .mp3"):
                            st.audio("rahatlama .mp3")
                        else:
                            st.warning("Somatik kayıt bulunamadı.")
            except Exception as e:
                st.error("Analiz verisi işlenemedi.")
