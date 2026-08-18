import streamlit as st
import numpy as np
import librosa
import soundfile as sf
import tempfile
import os

# Sayfa Yapılandırması
st.set_page_config(
    page_title="Ruhun Mimarisi | Vokal Terminal",
    page_icon="✨",
    layout="centered"
)

# Stil ve Tasarım (Butik, sakin ve karanlık/aydınlık uyumlu estetik)
st.markdown("""
    <style>
    .main {
        background-color: #fcfbf9;
        font-family: 'Helvetica Neue', sans-serif;
    }
    .title-text {
        text-align: center;
        color: #2c3e50;
        font-weight: 300;
        letter-spacing: 2px;
    }
    .subtitle-text {
        text-align: center;
        color: #7f8c8d;
        font-size: 15px;
        margin-bottom: 30px;
    }
    .card-box {
        background-color: #ffffff;
        padding: 25px;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.03);
        margin-bottom: 20px;
        border-left: 4px solid #d4ac0d;
    }
    </style>
""", unsafe_allow_html=True)

# Başlık Bölümü
st.markdown("<h1 class='title-text'>Ruhun Mimarisi</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle-text'>Sesinin Vokal İmzası ve İçsel Yolculuk Terminali</p>", unsafe_allow_html=True)

# Bilgilendirme
st.info("💡 **Gizlilik İlkesi:** Kaydettiğin ses dosyaları sunucularda asla saklanmaz. Ölçüm bittiği anda cihazdan ve sistemden tamamen temizlenir.")

# Ses Kaydı veya Yükleme Alanı
st.markdown("### 🎙️ Vokal Kaydı")
audio_file = st.file_uploader("Ses dosyanızı yükleyin (WAV / MP3)", type=["wav", "mp3", "m4a"])

if audio_file is not None:
    # Geçici dosya oluşturup hemen analiz edip silme mantığı (Sunucuda yer tutmaz)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
        tmp_file.write(audio_file.read())
        tmp_path = tmp_file.name

    try:
        # Librosa ile saf akustik verileri okuma
        y, sr = librosa.load(tmp_path, sr=None)
        
        # Temel Frekans (F0) ve Enerji (RMS) hesaplama
        f0, voiced_flag, voiced_probs = librosa.pyin(y, fmin=librosa.note_to_hz('C2'), fmax=librosa.note_to_hz('C7'))
        valid_f0 = f0[~np.isnan(f0)]
        
        avg_pitch = np.mean(valid_f0) if len(valid_f0) > 0 else 0
        rms_energy = np.mean(librosa.feature.rms(y=y))
        
        # Ekran çıktısı (Soğuk grafikler yerine dürüst akustik imza)
        st.markdown("---")
        st.markdown("### 📊 Bugünkü Vokal İmzanız")
        col1, col2 = st.columns(2)
        with col1:
            st.metric(label="Ortalama Titreşim (F0)", value=f"{avg_pitch:.1f} Hz")
        with col2:
            st.metric(label="Vokal Enerji Seviyesi", value=f"{rms_energy:.3f}")
            
    except Exception as e:
        st.error(f"Analiz sırasında bir hata oluştu: {e}")
        
    finally:
        # İşlem bittiği an geçici dosyayı sunucudan imha et
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

st.markdown("---")

# Rehberlik Kapıları Alanı (Yapay zekanın cümle uydurmadığı, senin kapıların)
st.markdown("### 🚪 Rehberlik Kapıları")
st.write("O anki içsel durumuna en yakın olan eşiği seçebilir, derinleşmek istediğinde rehberlik talep edebilirsin.")

kapim = st.selectbox(
    "Bugün hangi eşikte duruyorsun?",
    [
        "Seçiniz...",
        "1. Kapı: İçsel Sessizlik ve Topraklanma",
        "2. Kapı: Zihinsel Yoğunluğu ve Yükü Arındırma",
        "3. Kapı: Sınırlar ve Öz-Şefkat Eşiği"
    ]
)

if kapim != "Seçiniz...":
    st.markdown("<div class='card-box'>", unsafe_allow_html=True)
    if "1. Kapı" in kapim:
        st.write("🌿 **İçsel Sessizlik:** Zihin dışarıdaki gürültülerle dolduğunda, sesin titreşimi de hızlanır. Bugün biraz durmak, derin nefeslerle köklenmek ve dış dünyayı sessize almak için doğru bir eşikte olabilirsin.")
    elif "2. Kapı" in kapim:
        st.write("🌊 **Zihinsel Arınma:** Omuzlarındaki yükleri taşımak yorucu olabilir. Sesindeki enerji, bırakılması gereken eski bir döngünün hafifleme arzusunu fısıldıyor.")
    elif "3. Kapı" in kapim:
        st.write("⚖️ **Sınırlar ve Öz-Şefkat:** Kendi alanını korumak ve kalbinin sesini duymak dışarıdaki sesleri kısmaktan geçer. Önce kendi merkezin.")
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Mail üzerinden köprü kurma alanı
    with st.expander("✨ Bu analizin ve sesinin derinlemesine yorumlanmasını ister misin?"):
        st.write("Bu sadece bir eşikti. Haritanın bütüncül hikayesini ve kişisel rehberlik raporunu doğrudan **Meral Erdil**'in kaleme almasını istersen, katkı bedeli ve talep için aşağıdaki kanaldan ulaşabilirsin:")
        st.markdown("📩 **İletişim ve Talep:** `meralerdil.iletisim@gmail.com` *(Örn: Doğum bilgilerini ve ses analiz sonucunu maille ileterek detaylı rehberlik talep edebilirsin.)*")

# Alt Bilgi
st.markdown("---")
st.markdown("<p style='text-align: center; color: #aaa; font-size: 12px;'>Ruhun Mimarisi © 2026 | Tüm Hakları Saklıdır.</p>", unsafe_allow_html=True)
