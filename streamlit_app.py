import streamlit as st
import librosa
import numpy as np
import io
import os
import noisereduce as nr

# --- SAYFA YAPILANDIRMASI ---
st.set_page_config(page_title="Ruhun Mimarisi | VBAR Bütünsel Sentez", layout="centered", page_icon="🏛️")

# LOGO (Tam Genişlik)
if os.path.exists("1783526207831.png"):
    st.image("1783526207831.png", use_container_width=True)

st.title("🏛️ Ruhun Mimarisi | VBAR")
st.subheader("Bütünsel Ses, Enerji ve Farkındalık Analizi")

st.markdown("""
Sesinizin akustik tınısı ile doğum haritanızın kozmik frekansını sentezleyerek içsel ritminiz ve zindeliğiniz hakkında derinlemesine bir farkındalık aynası sunar.
""")

# --- OTOMATİK BURÇ HESAPLAMA FONKSİYONU ---
def burc_hesapla(gun, ay):
    ay_listesi = ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"]
    ay_idx = ay_listesi.index(ay) + 1
    
    if (ay_idx == 3 and gun >= 21) or (ay_idx == 4 and gun <= 20): return "Koç", "Ateş"
    elif (ay_idx == 4 and gun >= 21) or (ay_idx == 5 and gun <= 20): return "Boğa", "Toprak"
    elif (ay_idx == 5 and gun >= 21) or (ay_idx == 6 and gun <= 20): return "İkizler", "Hava"
    elif (ay_idx == 6 and gun >= 21) or (ay_idx == 7 and gun <= 22): return "Yengeç", "Su"
    elif (ay_idx == 7 and gun >= 23) or (ay_idx == 8 and gun <= 22): return "Aslan", "Ateş"
    elif (ay_idx == 8 and gun >= 23) or (ay_idx == 9 and gun <= 22): return "Başak", "Toprak"
    elif (ay_idx == 9 and gun >= 23) or (ay_idx == 10 and gun <= 22): return "Terazi", "Hava"
    elif (ay_idx == 10 and gun >= 23) or (ay_idx == 11 and gun <= 21): return "Akrep", "Su"
    elif (ay_idx == 11 and gun >= 22) or (ay_idx == 12 and gun <= 21): return "Yay", "Ateş"
    elif (ay_idx == 12 and gun >= 22) or (ay_idx == 1 and gun <= 19): return "Oğlak", "Toprak"
    elif (ay_idx == 1 and gun >= 20) or (ay_idx == 2 and gun <= 18): return "Kova", "Hava"
    else: return "Balık", "Su"

# --- KULLANICI GİRDİLERİ ---
with st.container(border=True):
    st.subheader("✨ Doğum Bilgileri")
    col_b1, col_b2, col_b3 = st.columns(3)
    with col_b1:
        gun = st.number_input("Gün", min_value=1, max_value=31, value=29)
    with col_b2:
        ay = st.selectbox("Ay", ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"], index=11)
    with col_b3:
        yil = st.number_input("Yıl", min_value=1940, max_value=2015, value=1984)

    hesaplanan_burc, element = burc_hesapla(gun, ay)
    st.info(f"Kozmik İmza: **{hesaplanan_burc}** burcu ({element} elementi)")

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
        with st.spinner("Ses dalgalarınız ve kozmik frekansınız çözümleniyor..."):
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

                # Derinlemesine Özgün Yorum Alanı
                with st.container(border=True):
                    st.subheader("🌿 Ruhun Mimarisi | Derinlemesine Bütünsel Sentez")
                    
                    if anlik_f0 < 150:
                        tiz_yorumu = "Sesiniz köklü, derin ve yeryüzüyle güçlü bir bağ kuran tona sahip. İçsel bir sükûnet arayışındasınız."
                    elif anlik_f0 < 250:
                        tiz_yorumu = "Sesiniz akışkan, dengeli ve merkezinde duran şefkatli bir frekans yayıyor. Zihin ve beden uyum içinde."
                    else:
                        tiz_yorumu = "Sesiniz yüksek bir canlılık, ilham ve zihinsel hareketlilik barındırıyor. Kabuğuna sığmayan bir enerji akışınız var."

                    element_yorumlari = {
                        "Toprak": f"{hesaplanan_burc} enerjisinin o sağlam, yapılandırıcı ve kararlı duruşu, sesinizin yeryüzü tonlarıyla bütünleşiyor. Sınırlarınızı korumak ve somatik olarak bedene yerleşmek bugün sizin için şifalı.",
                        "Ateş": f"{hesaplanan_burc} burcunun içsel ateşindeki yaratıcı kıvılcım ses tonunuza yansıyor. Tutkulu ve yönlendirici bir enerji taşıyorsunuz.",
                        "Hava": f"{hesaplanan_burc} enerjisiyle zihinsel çeviklik ve bilgi akışı ön planda. Kelimeleriniz rüzgar gibi özgür ve akışkan.",
                        "Su": f"{hesaplanan_burc} burcunun getirdiği duygusal derinlik ve sezgisel akış sesinizin tınısına yankı katıyor. İç dünyanız oldukça zengin."
                    }

                    st.markdown(f"**Akustik Yankı:** {tiz_yorumu}")
                    st.markdown(f"**Elementsel Rehberlik ({element}):** {element_yorumlari.get(element, '')}")
                    
                    taslar = {"Toprak": "Onyx ve Hematit", "Ateş": "Kırmızı Agat ve Obsidyen", "Hava": "Labradorit", "Su": "Lapis Lazuli ve Akuamarin"}
                    st.markdown(f"**Şifalı Taş Frekansı:** Bu dönemde enerjinizi dengelemek için **{taslar.get(element, 'Onyx')}** enerjisinden destek alabilirsiniz.")

                # --- DURUMSAL SOMATİK UYUM ALANI ---
                if gerilim > 4.5 or anlik_f0 > 230:
                    with st.container(border=True):
                        st.subheader("🧘 Somatik Uyum ve Arınma Alanı")
                        st.info("Sesinizdeki yüksek gerilim veya hareketlilik, zihinsel bir mola vermeniz gerektiğine işaret ediyor. Bu akışı dengelemek için aşağıdaki çalışmayı dinleyebilirsiniz:")
                        if os.path.exists("rahatlama .mp3"):
                            st.audio("rahatlama .mp3", format="audio/mp3")
                        else:
                            st.warning("Somatik ses dosyası (rahatlama .mp3) bulunamadı.")
                else:
                    st.success("✨ Enerji alanınız oldukça sakin ve akışta. Bu merkezî huzuru korumaya özen gösterin.")

            except Exception as e:
                st.error(f"Analiz sırasında bir hata oluştu: {e}")
