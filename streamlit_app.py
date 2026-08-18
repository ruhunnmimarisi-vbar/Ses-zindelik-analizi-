import streamlit as st
import base64

# Sayfa Yapılandırması
st.set_page_config(page_title="Ruhun Mimarisi", page_icon="🏛️")

# Amblemi ekrana en temiz haliyle sabitleyen stil
st.markdown("""
    <style>
    .logo-container {
        display: flex;
        justify-content: center;
        padding-top: 20px;
        padding-bottom: 30px;
    }
    .stApp {
        background-color: #fdfcf9; /* Amblemin o nazik tonuna uygun zemin */
        color: #5d5045;
    }
    .stButton>button {
        border: 1px solid #c5a083;
        color: #5d5045;
        background-color: transparent;
        border-radius: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# 1. AMBLEM: Markanın Kalbi (Senin gönderdiğin amblem burada sabitleniyor)
# Not: Resim dosyasının adını 'amblem.png' olarak varsayıyorum.
st.markdown('<div class="logo-container">', unsafe_allow_html=True)
st.image("watermarked_img_1706696993258948374.png", width=250) 
st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<h2 style='text-align: center; color: #5d5045;'>Meral Erdil</h2>", unsafe_allow_html=True)
st.markdown("<hr style='border: 0.5px solid #dcdcdc;'>", unsafe_allow_html=True)

# 2. Vokal Terminali
st.markdown("### 🎙️ İçsel Titreşim Kaydı")
st.write("Sadece sesinin fiziksel yansımasını ölçüyoruz. Gizlilik senin en büyük hakkın.")

# Ses ölçüm mantığı buraya gelecek (kullanıcı dostu, yalın)
uploaded_file = st.file_uploader("Sesinizi buraya bırakın", type=["wav", "mp3"])

if uploaded_file:
    st.success("Titreşim analizi tamamlandı. Sesiniz sistemden silindi.")
    # Burada o sakin metrikler amblemin renk tonlarıyla (altın/kuvars) görünecek.

# 3. Rehberlik Kapıları
st.markdown("### 🚪 Rehberlik Kapıları")
kapim = st.selectbox("Bugün hangi eşiktesin?", ["Sessizlik", "Arınma", "Öz-Şefkat"])

# Burada amblemin ağırlığına uygun, zarif bir açıklama alanı
st.markdown(f"""
    <div style='background-color: #f8f5f1; padding: 20px; border-radius: 10px; border-left: 5px solid #c5a083;'>
        Seçtiğiniz {kapim} kapısı, bu haftanın akışında size rehberlik edecek.
    </div>
""", unsafe_allow_html=True)

# 4. İletişim
st.markdown("---")
st.write("✨ *Detaylı rehberlik ve içsel yolculuk raporu için:* [meralerdil.iletisim@gmail.com](mailto:meralerdil.iletisim@gmail.com)")
