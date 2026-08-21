import streamlit as st
import librosa
import numpy as np
import io
import os
import noisereduce as nr

# --- SAYFA YAPILANDIRMASI ---
st.set_page_config(page_title="Ruhun Mimarisi | VBAR Bütünsel Sentez", layout="centered", page_icon="🏛️")

# LOGO (Tam Genişlik / Büyük Görünüm)
if os.path.exists("1783526207831.png"):
    st.image("1783526207831.png", use_container_width=True)

st.title("🏛️ Ruhun Mimarisi | VBAR")
st.subheader("Bütünsel Ses, Enerji ve Farkındalık Analizi")

st.markdown("""
Ses tonunuzdaki akustik parametreleri (frekans, titreşim, gerilim) ve astrolojik altyapınızı sentezleyerek içsel ritminiz hakkında derinlemesine bir farkındalık aynası sunar.
""")

# --- KULLANICI GİRDİLERİ (BURÇ & ASTROLOJİ DETAYLARI) ---
with st.container(border=True):
    st.subheader("✨ Doğum Haritası & Astrolojik Veriler")
    
    col_b1, col_b2, col_b3 = st.columns(3)
    with col_b1:
        gun = st.number_input("Gün", min_value=1, max_value=31, value=29)
    with col_b2:
        ay = st.selectbox("Ay", ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"], index=11)
    with col_b3:
        yil = st.number_input("Yıl", min_value=1940, max_value=2015, value=1984)

    col_burc1, col_burc2 = st.columns(2)
    with col_burc1:
        gunes_burcu = st.selectbox("Güneş Burcu", ["Koç", "Boğa", "İkizler", "Yengeç", "Aslan", "Başak", "Terazi", "Akrep", "Yay", "Oğlak", "Kova", "Balık"], index=9)
    with col_burc2:
        yukselen_burcu = st.selectbox("Yükselen Burcu (Tahmini veya Bilinen)", ["Seçiniz...", "Koç", "Boğa", "İkizler", "Yengeç", "Aslan", "Başak", "Terazi", "Akrep", "Yay", "Oğlak", "Kova", "Balık"])

st.markdown("---")

# SES VERİSİ SAĞLAMA
upload_option = st.radio("Ses Verisi Sağlama Yöntemi:", ["Mikrofon ile Kayıt Yap", "Ses Dosyası Yükle"], key="veri_saglama_yontemi")
audio_bytes = None

if upload_option == "Mikrofon ile Kayıt Yap":
    audio_file = st.audio_input("Lütfen konuşun veya sesinizi kaydedin", key="mobil_mikrofon_input")
    if audio_file is not None:
        audio_bytes = audio_file.read()
else:
    uploaded_file = st.file_uploader("Ses dosyanızı seçin", type=["mp3", "wav", "m4a"], key="dosya_yukleme_input")
    if uploaded_file is not None:
        audio_bytes = uploaded_file.read()

st.markdown("---")

if audio_bytes is not None:
    if st.button("✨ Akustik ve Bütünsel Analizi Başlat", key="analiz_baslat_btn"):
        with st.spinner("Ses dalgalarınız, element dengeniz ve frekans akışınız çözümleniyor..."):
            try:
                # Akustik Hesaplamalar
                y, sr = librosa.load(io.BytesIO(audio_bytes), sr=16000)
                y_denoised = nr.reduce_noise(y=y, sr=sr, prop_decrease=0.7)
                pitches, _ = librosa.piptrack(y=y_denoised, sr=sr, fmin=80, fmax=400)
                
                anlik_f0 = float(np.nanmean(pitches[pitches > 0])) if np.any(pitches > 0) else 210.0
                rms_val = float(np.mean(librosa.feature.rms(y=y_denoised)))
                cent_val = float(np.mean(librosa.feature.spectral_centroid(y=y_denoised, sr=sr)))
                gerilim = (rms_val * 50) + (cent_val / 400)

                # Sonuç Paneli
                with st.container(border=True):
                    st.subheader("🔬 Akustik Biyometrik Rapor")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Ortalama Ses Frekansı (F0)", f"{anlik_f0:.1f} Hz")
                    with col2:
                        st.metric("Gerilim / Enerji İndeksi", f"{gerilim:.2f}")

                # Derinlemesine Bütünsel Yorumlar ve Yönlendirmeler
                with st.container(border=True):
                    st.subheader("🌿 Ruhun Mimarisi | Derinlemesine Bütünsel Sentez")
                    
                    elementler = {
                        "Koç": "Ateş", "Aslan": "Ateş", "Yay": "Ateş",
                        "Boğa": "Toprak", "Başak": "Toprak", "Oğlak": "Toprak",
                        "İkizler": "Hava", "Terazi": "Hava", "Kova": "Hava",
                        "Yengeç": "Su", "Akrep": "Su", "Balık": "Su"
                    }
                    element = elementler.get(gunes_burcu, "Toprak")

                    st.markdown(f"**Astrolojik Matris:** Güneş Burcu: **{gunes_burcu}** ({element} Elementi) | Yükselen: **{yukselen_burcu}**")
                    
                    if anlik_f0 < 150:
                        ses_analizi = "Ses tonunuz derin, köklenen, otoriter ve içsel sükûnet arayan bir frekansta."
                    elif anlik_f0 < 250:
                        ses_analizi = "Ses tonunuz dengeli, akışta, merkezlenen ve şefkatli bir ifade alanı sunuyor."
                    else:
                        ses_analizi = "Ses tonunuz yüksek canlılığa sahip, dinamik, ilham veren ve zihinsel hareketliliği yansıtıyor."

                    st.markdown(f"**Akustik Yansıma:** {ses_analizi}")

                    # Taş ve Şifa Önerileri
                    taslar = {"Toprak": "Onyx / Hematit", "Ateş": "Kırmızı Agat / Obsidyen", "Hava": "Labradorit", "Su": "Lapis Lazuli / Akuamarin"}
                    onerilen_tas = taslar.get(element, "Onyx")
                    st.markdown(f"**Destekleyici Doğal Taş:** {onerilen_tas}")

                # --- DURUMSAL SOMATİK UYUM ALANI (Gerilim/Enerji İndeksine Göre Belirir) ---
                if gerilim > 4.5 or anlik_f0 > 230:
                    with st.container(border=True):
                        st.subheader("🧘 Somatik Uyum ve Akış Alanı")
                        st.info("Yüksek enerji veya zihinsel hareketlilik tespit edildi. Bu alanı dengelemek için aşağıdaki somatik ses çalışmasından faydalanabilirsiniz.")
                        if os.path.exists("rahatlama .mp3"):
                            st.audio("rahatlama .mp3", format="audio/mp3")
                        else:
                            st.warning("Somatik ses dosyası (rahatlama .mp3) sunucu dizininde bulunamadı.")
                else:
                    st.success("✨ Enerji akışınız ve ses frekansınız oldukça dengeli ve sakin bir çizgide ilerliyor.")

            except Exception as e:
                st.error(f"Analiz sırasında bir hata oluştu: {e}")
