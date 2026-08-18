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

# ŞIK VE KURUMSAL ARAYÜZ STİLLERİ (Sıcak Tonlar, Krem & Altın & Lacivert)
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
    Bu terminal, biyometrik verilerinizi size özel kalibrasyonla harmanlayarak içsel dengenizi keşfetmeniz için tasarlanmıştır.
</div>
""", unsafe_allow_html=True)

# SEKME YAPISI
tab1, tab3, tab2 = st.tabs(["🔬 Biyometrik Analiz", "📜 Günlük & Haftalık Arşiv", "📖 Bilimsel Altyapı & Hakkında"])

with tab2:
    st.subheader("Ruhun Mimarisi ve VBAR Nedir?")
    st.write("""
    **VBAR (Voice-Based Assessment & Regulation)**, insan sesindeki akustik mikro titreşimleri analiz ederek sinir sisteminin o anki yükünü ve gerilim seviyesini kişiye özel referans çizgisiyle ölçen yenilikçi bir araçtır.
    """)
    
    st.markdown("### 🧬 Kişiselleştirilmiş Kalibrasyon Prensibi")
    st.markdown("""
    * **Kişisel Merkez Çizgisi:** Her bireyin vokal anatomisi farklıdır. Sistem, ilk kayıtlarınızı baz alarak sizin **kendi doğal vokal tabanınızı** oluşturur.
    * **Dinamik Eşik Analizi:** Yapılan günlük ölçümler ortak bir sabitle değil, tamamen sizin kendi sakin halinizin ortalamasıyla kıyaslanır.
    """)

# Durum yönetimi başlatma
if "f0_val" not in st.session_state: st.session_state.f0_val = 0.0
if "zcr_val" not in st.session_state: st.session_state.zcr_val = 0.0
if "olcum_gecmisi" not in st.session_state: st.session_state.olcum_gecmisi = []
if "kisisel_baz_zcr" not in st.session_state: st.session_state.kisisel_baz_zcr = None

with tab3:
    st.subheader("📜 Zaman Akışı ve Haftalık Değerlendirme Arşivi")
    st.write("Bu alanda günlük ölçümleriniz ve kişisel vokal eğiliminiz analiz edilir.")
    
    if len(st.session_state.olcum_gecmisi) == 0:
        st.info("Henüz kaydedilmiş bir ölçüm bulunmuyor. 'Biyometrik Analiz' sekmesinden ilk ölçümünüzü gerçekleştirebilirsiniz.")
    else:
        simdi_dt = datetime.now()
        yedi_gun_once = simdi_dt - timedelta(days=7)
        
        haftalik_kayitlar = [
            k for k in st.session_state.olcum_gecmisi 
            if datetime.strptime(k['zaman'], "%d.%m.%Y %H:%M") >= yedi_gun_once
        ]
        
        if haftalik_kayitlar:
            ort_f0 = np.mean([k['f0'] for k in haftalik_kayitlar])
            ort_zcr = np.mean([k['zcr'] for k in haftalik_kayitlar])
            
            # Kişisel baza göre akıllı yorumlama
            baz_deger = st.session_state.kisisel_baz_zcr if st.session_state.kisisel_baz_zcr else 0.12
            sapma_orani = ort_zcr - baz_deger
            
            st.markdown("### 📈 Son 7 Günlük Kişisel Vokal Özeti")
            st.markdown(f"""
            <div class="summary-card">
                <b>Kişisel Vokal Tabanınız (Baz):</b> {baz_deger:.4f}<br>
                <b>Haftalık Ortalama Gerginlik İndeksi:</b> {ort_zcr:.4f}<br>
                <hr style='border: 0.5px solid #c5a083; margin: 10px 0;'>
                <b>🧠 Kişiselleştirilmiş Öz-Gözlem Yorumu:</b><br>
                { "Kişisel merkez çizginizin üzerine çıktığınız, zihinsel eforun ve temponun bu hafta yoğunlaştığı bir döngüdesiniz. Vokal tonunuz dinlenmeye ve somatik akışa alan açmanız gerektiğini fısıldıyor." if sapma_orani > 0.03 else "Haftalık vokal akışınız, kendi kişisel merkez çizginizle mükemmel bir uyum ve denge içinde seyretmiş. İçsel merkezlenmeniz oldukça kararlı." }
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown("---")
        st.markdown("### 📋 Tüm Günlük Ölçüm Kayıtları")
        for idx, kayit in enumerate(reversed(st.session_state.olcum_gecmisi), 1):
            st.markdown(f"""
            <div class="history-card">
                <b>Ölçüm #{len(st.session_state.olcum_gecmisi) - idx + 1}</b> — <i>{kayit['zaman']}</i><br>
                🔹 <b>Temel Frekans (F0):</b> {kayit['f0']:.1f} Hz | 🔹 <b>Gerginlik İndeksi:</b> {kayit['zcr']:.4f}
            </div>
            """, unsafe_allow_html=True)

with tab1:
    st.subheader("1. Aşama: Ses Verisi Girişi ve Kalibrasyon")
    
    if st.session_state.kisisel_baz_zcr is None:
        st.info("🎯 **İlk Keşif:** Sisteme hoş geldiniz. Size özel vokal kalibrasyonunun yapılabilmesi için lütfen ilk doğal ses kaydınızı gerçekleştirin.")
    
    upload_option = st.radio("Ses Verisi Sağlama Yöntemi:", ["Mikrofon ile Kayıt Yap", "Ses Dosyası Yükle (.mp3, .wav)"])

    audio_bytes = None

    if upload_option == "Mikrofon ile Kayıt Yap":
        audio_file = st.audio_input("Lütfen derin bir nefes alıp 5-10 saniye doğal tonunuzla konuşun")
        if audio_file:
            audio_bytes = audio_file.read()
    else:
        uploaded_file = st.file_uploader("Ses dosyanızı yükleyin", type=["mp3", "wav", "m4a"])
        if uploaded_file:
            audio_bytes = uploaded_file.read()

    if audio_bytes:
        st.audio(audio_bytes, format="audio/mp3")
        
        button_label = "🎯 Kalibrasyonu Tamamla ve Analizi Başlat" if st.session_state.kisisel_baz_zcr is None else "🚀 Gürültü Filtreli Analizi Başlat"
        
        if st.button(button_label):
            with st.spinner("Sesiniz arındırılıyor ve biyometrik veriler analiz ediliyor..."):
                y, sr = librosa.load(io.BytesIO(audio_bytes), sr=16000)
                y_denoised = nr.reduce_noise(y=y, sr=sr, prop_decrease=0.7)
                
                pitches, _ = librosa.piptrack(y=y_denoised, sr=sr, fmin=80, fmax=400)
                anlik_f0 = float(np.nanmean(pitches[pitches > 0])) if np.any(pitches > 0) else 210.0
                anlik_zcr = float(np.mean(librosa.feature.zero_crossing_rate(y_denoised)))
                
                st.session_state.f0_val = anlik_f0
                st.session_state.zcr_val = anlik_zcr
                
                # Eğer daha önce kalibrasyon yapılmadıysa, ilk kayıt KİŞİSEL BAZ çizgisi olur
                if st.session_state.kisisel_baz_zcr is None:
                    st.session_state.kisisel_baz_zcr = anlik_zcr
                
                simdi = datetime.now().strftime("%d.%m.%Y %H:%M")
                st.session_state.olcum_gecmisi.append({
                    "zaman": simdi,
                    "f0": st.session_state.f0_val,
                    "zcr": st.session_state.zcr_val
                })
            
            st.markdown(f"""
            <div class="report-box">
                <h3 style="color: #1b263b; margin-top: 0;">Kişiselleştirilmiş Biyometrik Ölçüm Raporu</h3>
                <p><b>Temel Frekans (F0):</b> {st.session_state.f0_val:.1f} Hz</p>
                <p><b>Gerginlik İndeksi (ZCR):</b> {st.session_state.zcr_val:.4f}</p>
                <p><b>Kişisel Vokal Bazınız:</b> {st.session_state.kisisel_baz_zcr:.4f}</p>
                <p style="font-size: 0.85em; color: #666;"><i>Bu ölçüm kişisel arşivinize kaydedildi.</i></p>
            </div>
            """, unsafe_allow_html=True)
            
            # Kişisel baza göre anlık somatik uyarı
            if st.session_state.zcr_val > (st.session_state.kisisel_baz_zcr * 1.25):
                st.warning("⚠️ Kişisel merkez çizginizin üzerinde gerginlik tespit edildi. Dinlendirici somatik akış başlatılıyor:")
                if os.path.exists("rahatlama .mp3"):
                    st.audio("rahatlama .mp3", format="audio/mp3")
                else:
                    st.info("💡 Rahatlama ses dosyası aranıyor...")
            else:
                st.success("✅ Vokal enerjiniz kendi doğal akışınızla uyum içinde.")

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
                govde = f"Ad Soyad: {ad_soyad}\nE-posta: {kullanici_mail}\nDoğum Tarihi: {dogum_tarihi_str}\nDoğum Saati: {dogum_saati}\n\nÖlçüm Sonuçları:\n- F0: {st.session_state.f0_val:.1f} Hz\n- Gerginlik: {st.session_state.zcr_val:.4f}"
                mailto_link = f"mailto:ruhunnmimarisi@gmail.com?subject={urllib.parse.quote(konu)}&body={urllib.parse.quote(govde)}"
                st.markdown(f'<a href="{mailto_link}" target="_blank" style="display:inline-block;background:#1b263b;color:#fff;padding:10px 20px;border-radius:8px;font-weight:bold;text-decoration:none;margin-top:10px;">📬 E-Posta Uygulamasını Aç ve Gönder</a>', unsafe_allow_html=True)
            else:
                st.error("Lütfen adınızı ve e-posta adresinizi eksiksiz doldurun.")
