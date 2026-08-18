import streamlit as st
import numpy as np
import librosa
import os
import tempfile

# Sayfa Yapılandırması
st.set_page_config(page_title="Ruhun Mimarisi", page_icon="🏛️")

# Estetik Stil (Butik, temiz ve sakin)
st.markdown("""
    <style>
    .stApp { background-color: #fcfbf9; color: #5d5045; }
    .logo-container { display: flex; justify-content: center; padding: 20px; }
    </style>
""", unsafe_allow_html=True)

# 1. Amblem (Markanın mührü)
st.markdown('<div class="logo-container">', unsafe_allow_html=True)
st.image("1783526207831.png", width=200)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<h2 style='text-align: center; color: #5d5045;'>Vokal Terminali</h2>", unsafe_allow_html=True)

# 2. Gizlilik ve Hafiflik Prensibi (Sistem şişmez, veri birikmez)
st.info("💡 **Gizlilik İlkesi:** Ses dosyalarınız sunucuda tutulmaz, analiz anlık yapılır ve işlem sonunda tamamen imha edilir.")

# 3. Ses Analizi (Matematiksel veri - Yapay zeka uydurması yok)
uploaded_file = st.file_uploader("Sesinizi buraya bırakın", type=["wav", "mp3"])

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
            os.remove(tmp_path) # Dosyayı hemen sil (Hafıza şişmesini önle)

# 4. Rehberlik Kapıları (Senin kapıların)
st.markdown("### 🚪 Rehberlik Kapıları")
kapim = st.selectbox("Bugün hangi eşiktesin?", ["Sessizlik", "Arınma", "Öz-Şefkat"])

# 5. İletişim (Yalnızca mail köprüsü)
st.markdown("---")
st.write("✨ Detaylı rehberlik için: [ruhunnmimarisi@gmail.com](mailto:ruhunnmimarisi@gmail.com)")
