import streamlit as st
import librosa
import numpy as np
import io
import os
import urllib.parse
import noisereduce as nr
from datetime import datetime, timedelta

# --- SAYFA YAPILANDIRMASI ---
st.set_page_config(page_title="Ruhun Mimarisi | VBAR Biyometrik Analiz", layout="centered", page_icon="🔬")

# ŞIK VE KURUMSAL ARAYÜZ STİLLERİ
st.markdown("""
<style>
    .stApp {
        background-color: #fcfbfa;
        color: #2c2c2c;
    }
    .report-box {
        border: 1px solid #d4af37;
        padding: 20px;
        border-radius: 12px;
        background: #ffffff;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        margin-top: 15px;
    }
    .history-card {
        border-left: 3px solid #d4af37;
        padding: 10px 15px;
        background: #fffdf9;
        margin-bottom: 10px;
        border-radius: 6px;
        font-size: 0.95em;
    }
    .summary-card {
        background: #f4efe6;
        border: 1px solid #c5a083;
        padding: 15px;
        border-radius: 10px;
        margin-top: 15px;
        color: #3a3229;
    }
    .welcome-card {
        background: #fff8e8;
        border-left: 4px solid #d4af37;
        padding: 15px;
        border-radius: 8px;
        font-style: italic;
        color: #4a4a4a;
        margin-bottom: 20px;
    }
    .stButton>button {
        background-color: #1b263b;
        color: #ffffff;
        border-radius: 8px;
        border: none;
        font-weight: bold;
        padding: 10px 20px;
    }
    .stButton>button:hover {
        background-color: #d4af37;
        color: #000000;
    }
</style>
""", unsafe_allow_html=True)

# 1. GÖRSEL BANNER
if os.path.exists("1783526207831.png"):
    st.image("1783526207831.png", use_container_width=True)
else:
    st.title("🔬 Ruhun Mimarisi | VBAR Terminali")

# KARŞILAMA VE VİZYON
st.markdown("""
<div class="welcome-card">
    "Sesiniz; zihninizin, duygularınızın ve sinir sistemi durumunuzun en saf fiziksel imzasıdır." 
    Gelişmiş spektral akustik motoru ile sesinizdeki tüm enerji ve gerilim dalgalanmaları hassasiyetle taranır.
</div>
""", unsafe_allow_html=True)

# SEKME YAPISI
tab1, tab3, tab2 = st.tabs(["🔬 Gelişmiş Biyometrik Analiz", "📜 Günlük & Haftalık Arşiv", "📖 Bilimsel Altyapı & Hakkında"])

with tab2:
    st.subheader("Ruhun Mimarisi ve VBAR Nedir?")
    st.write("""
    **VBAR (Voice-Based Assessment & Regulation)**, insan sesindeki mikro akustik değişimleri, enerji yoğunluğunu ve spektral dalgalanmaları analiz ederek gerilim seviyenizi objektif olarak raporlayan profesyonel bir araçtır.
    """)
    
    st.markdown("### 🧬 Gelişmiş Akustik Analiz Prensibi")
    st.markdown("""
    * **Spektral Ağırlık ve Enerji (Spectral Centroid & RMS):** Sesin sadece tınısına değil, öfke ve yüksek efor anlarında frekans spektrumunda oluşan yukarı yönlü kaymalara odaklanır.
    * **Haftalık Aritmetik Ortalama:** Tüm duygu durum ve gerilim dalgalanmalarınız zaman akışında toplanarak haftalık gerçek ortalamanızı belirler.
    """)

# Durum yönetimi başlatma
if "f0_val" not in st.session_state: st.session_state.f0_val = 0.0
if "gerilim_val" not in st.session_state: st.session_state.gerilim_val = 0.0
if "olcum_gecmisi" not in st.session_state: st.session_state.olcum_gecmisi = []

with tab3:
    st.subheader("📜 Zaman Akışı ve Haftalık Aritmetik Ortalama Arşivi")
    st.write("Bu alanda gelişmiş akustik motorla ölçülen tüm kayıtlarınız listelenir.")
    
    if len(st.session_state.olcum_gecmisi) == 0:
        st.info("Henüz kaydedilmiş bir ölçüm bulunmuyor. 'Gelişmiş Biyometrik Analiz' sekmesinden ilk ses kaydınızı gerçekleştirebilirsiniz.")
    else:
        simdi_dt = datetime.now()
        yedi_gun_once = simdi_dt - timedelta(days=7)
        
        haftalik_kayitlar = [
            k for k in st.session_state.olcum_gecmisi 
            if datetime.strptime(k['zaman'], "%d.%m.%Y %H:%M") >= yedi_gun_once
        ]
        
        if haftalik_kayitlar:
            ort_f0 = np.mean([k['f0'] for k in haftalik_kayitlar])
            ort_gerilim = np.mean([k['gerilim'] for k in haftalik_kayitlar])
            
            st.markdown("### 📈 Son 7 Günlük Gelişmiş Akustik Özet")
            st.markdown(f"""
            <div class="summary-card">
                <b>Toplam Kayıt Sayısı (Son 7 Gün):</b> {len(haftalik_kayitlar)}<br>
                <b>Haftalık Ortalama Temel Frekans (F0):</b> {ort_f0:.1f} Hz<br>
                <b>Haftalık Ortalama Gerilim / Enerji İndeksi:</b> {ort_gerilim:.2f}<br>
                <hr style='border: 0.5px solid #c5a083; margin: 10px 0;'>
                <b>🧠 Bütüncül Akustik Yorum:</b><br>
                { "Haftalık enerji ve gerilim ortalamanız yüksek seyretmiş. Ses dalgalarınızdaki spektral yoğunluk, yoğun bir tempoda olduğunuzu gösteriyor." if ort_gerilim > 6.0 else "Haftalık akustik ortalamanız oldukça dengeli, huzurlu ve akışında bir seyir izlemiş." }
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown("---")
        st.markdown("### 📋 Tüm Ölçüm Kayıtları Arşivi")
        
        col_sil, _ = st.columns([1, 3])
        with col_sil:
            if st.button("🗑️ Arşivi Sıfırla"):
                st.session_state.olcum_gecmisi = []
                st.rerun()

        for idx, kayit in enumerate(reversed(st.session_state.olcum_gecmisi), 1):
            st.markdown(f"""
            <div class="history-card">
                <b>Ölçüm #{len(st.session_state.olcum_gecmisi) - idx + 1}</b> — <i>{kayit['zaman']}</i><br>
                🔹 <b>Temel Frekans (F0):</b> {kayit['f0']:.1f} Hz | ⚡ <b>Gerilim İndeksi:</b> {kayit['gerilim']:.2f}
            </div>
            """, unsafe_allow_html=True)

with tab1:
    st.subheader("1. Aşama: Gelişmiş Ses Verisi Girişi")
    
    upload_option = st.radio("Ses Verisi Sağlama Yöntemi:", ["Mikrofon ile Kayıt Yap", "Ses Dosyası Yükle (.mp3, .wav)"])

    audio_bytes = None

    if upload_option == "Mikrofon ile Kayıt Yap":
        audio_file = st.audio_input("Lütfen konuşun (öfke, sohbet, coşku veya doğal haliniz)")
        if audio_file:
            audio_bytes = audio_file.read()
    else:
        uploaded_file = st.file_uploader("Ses dosyanızı yükleyin", type=["mp3", "wav", "m4a"])
        if uploaded_file:
            audio_bytes = uploaded_file.read()

    if audio_bytes:
        st.audio(audio_bytes, format="audio/mp3")
        
        if st.button("🚀 Gelişmiş Spektral Analizi Başlat ve Arşive Ekle"):
            with st.spinner("Ses spektrumu, enerji dağılımı ve vokal tınılar analiz ediliyor..."):
                y, sr = librosa.load(io.BytesIO(audio_bytes), sr=16000)
                
                # SES KONTROLÜ (Boş kayıt koruması)
                rms_enerji_kontrol = np.mean(librosa.feature.rms(y=y))
                
                if rms_enerji_kontrol < 0.01:
                    st.error("⚠️ Yetersiz ses algılandı! Lütfen mikrofonunuza yaklaşarak net bir şekilde konuşun.")
                else:
                    # Gürültü azaltma
                    y_denoised = nr.reduce_noise(y=y, sr=sr, prop_decrease=0.7)
                    
                    # 1. Temel Frekans (F0)
                    pitches, _ = librosa.piptrack(y=y_denoised, sr=sr, fmin=80, fmax=400)
                    anlik_f0 = float(np.nanmean(pitches[pitches > 0])) if np.any(pitches > 0) else 210.0
                    
                    # 2. Gelişmiş Mühendislik Metrikleri (RMS Enerji + Spektral Ağırlık / Centroid)
                    rms_val = np.mean(librosa.feature.rms(y=y_denoised))
                    spectral_centroid = np.mean(librosa.feature.spectral_centroid(y=y_denoised, sr=sr))
                    
                    # Öfke ve gerginlik anlarında spektral merkez yukarı kayar ve enerji artar
                    # Bu formül sesin sertliğini, dinamik patlamalarını ve frekans yükselmesini doğrudan yakalar
                    gelismis_gerilim = float((rms_val * 50) + (spectral_centroid / 400))
                    
                    st.session_state.f0_val = anlik_f0
                    st.session_state.gerilim_val = gelismis_gerilim
                    
                    simdi = datetime.now().strftime("%d.%m.%Y %H:%M")
                    st.session_state.olcum_gecmisi.append({
                        "zaman": simdi,
                        "f0": st.session_state.f0_val,
                        "gerilim": st.session_state.gerilim_val
                    })
                
                    st.markdown(f"""
                    <div class="report-box">
                        <h3 style="color: #1b263b; margin-top: 0;">Gelişmiş Akustik Biyometrik Rapor</h3>
                        <p><b>Temel Frekans (F0):</b> {st.session_state.f0_val:.1f} Hz</p>
                        <p><b>Gerilim / Enerji İndeksi:</b> {st.session_state.gerilim_val:.2f}</p>
                        <p style="font-size: 0.85em; color: #666;"><i>Bu ölçüm spektral analiz motoruyla hesaplanarak arşive eklendi.</i></p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Kıyaslama
                    tum_gerilimler = [k['gerilim'] for k in st.session_state.olcum_gecmisi]
                    genel_ortalama_gerilim = np.mean(tum_gerilimler)
                    
                    if st.session_state.gerilim_val > (genel_ortalama_gerilim * 1.15):
                        st.warning("⚠️ Bu kayıtta yüksek spektral enerji ve gerilim saptandı. Dinlendirici somatik akış önerilir:")
                        if os.path.exists("rahatlama .mp3"):
                            st.audio("rahatlama .mp3", format="audio/mp3")
                        else:
                            st.info("💡 Rahatlama ses dosyası aranıyor...")
                    else:
                        st.success("✅ Bu kayıttaki akustik enerji kendi genel ortalamanızla uyum içinde.")

    st.markdown("---")
    st.subheader("📩 Uzman Raporu Talep Et")
    with st.form("iletisim_formu"):
        ad_soyad = st.text_input("Adınız Soyadınız")
        kullanici_mail = st.text_input("E-posta Adresiniz")
        
        st.markdown("<b>Doğum Tarihiniz:</b>", unsafe_allow_html=True)
        col_g, col_a, col_y = st.columns(3)
        with col_g:
            dogum_gun = st.selectbox("Gün", list(range(1, 32)))
        with col_a:
            dogum_ay = st.selectbox("Ay", ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"])
        with col_y:
            dogum_yil = st.selectbox("Yıl", list(range(2024, 1930, -1)))
            
        dogum_saati = st.text_input("Doğum Saati (Örn: 14:30)")
            
        submitted = st.form_submit_button("Raporu Hazırla")
        
        if submitted:
            if ad_soyad and kullanici_mail:
                dogum_tarihi_str = f"{dogum_gun} {dogum_ay} {dogum_yil}"
                konu = f"VBAR Analiz Talebi - {ad_soyad}"
                govde = f"Ad Soyad: {ad_soyad}\nE-posta: {kullanici_mail}\nDoğum Tarihi: {dogum_tarihi_str}\nDoğum Saati: {dogum_saati}\n\nSon Ölçüm:\n- F0: {st.session_state.f0_val:.1f} Hz\n- Gerilim İndeksi: {st.session_state.gerilim_val:.2f}"
                mailto_link = f"mailto:ruhunnmimarisi@gmail.com?subject={urllib.parse.quote(konu)}&body={urllib.parse.quote(govde)}"
                st.markdown(f'<a href="{mailto_link}" target="_blank" style="display:inline-block;background:#1b263b;color:#fff;padding:10px 20px;border-radius:8px;font-weight:bold;text-decoration:none;margin-top:10px;">📬 E-Posta Uygulamasını Aç ve Gönder</a>', unsafe_allow_html=True)
            else:
                st.error("Lütfen adınızı ve e-posta adresinizi eksiksiz doldurun.")
