import streamlit as st
import numpy as np
import librosa
import os
import tempfile

# Sayfa Yapılandırması
st.set_page_config(page_title="Ruhun Mimarisi", page_icon="🏛️")

# Görsel ve Başlık Düzeni
st.image("1783526207831.png")

st.markdown("<h1 style='text-align: center;'>Vokal Terminali</h1>", unsafe_allow_html=True)

# Gizlilik Bilgilendirmesi
st.info("💡 **Gizlilik İlkesi:** Ses dosyalarınız sunucuda tutulmaz, analiz anlık yapılır ve işlem sonunda tamamen imha edilir.")

# Ses Yükleme
st.markdown("### Sesinizi buraya bırakın")
uploaded_file = st.file_uploader("Upload", type=["wav", "mp3"])

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
        tmp_file.write(uploaded_file.read())
        tmp_path = tmp_file.name
    
    try:
        y, sr = librosa.load(tmp_path, sr=None)
        rms = np.mean(librosa.feature.rms(y=y))
        st.success("Titreşim analizi tamamlandı.")
        st.metric(label="Vokal Enerji İmzası", value=f"{rms:.4f}")
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

# Rehberlik Kapıları
st.markdown("### 🚪 Rehberlik Kapıları")
kapim = st.selectbox("Bugün hangi eşiktesiniz?", ["Sessizlik", "Arınma", "Öz-Şefkat"])

# İletişim
st.markdown("---")
st.write("✨ Detaylı rehberlik için: [ruhunnmimarisi@gmail.com](mailto:ruhunnmimarisi@gmail.com)")
