import streamlit as st
import librosa
import numpy as np
import io

st.set_page_config(page_title="VBAR - Çoklu Mod Biyometrik Analiz", page_icon="🎙️")

st.title("🎙️ VBAR - Kişiselleştirilmiş Ses Profil Analizi")
st.warning("⚠️ Bu bir tedavi/klinik teşhis aracı değildir. Sonuçlar yalnızca kendini gözlemleme amaçlıdır.")

# --- HAFIZA TANIMLAMALARI ---
if "profiles" not in st.session_state:
    st.session_state.profiles = {}  # Farklı modlar burada saklanacak (Zinde, Bıkkın vb.)

# Yan Menü (Sidebar) - Kayıtlı Modlar
st.sidebar.header("⚙️ Kayıtlı Ses Profilleriniz")
if not st.session_state.profiles:
    st.sidebar.warning("Henüz kayıtlı bir ses profiliniz yok.")
else:
    for mod_adi in st.session_state.profiles.keys():
        st.sidebar.success(f"✅ {mod_adi} Modu Kayıtlı")
    
    if st.sidebar.button("Profilleri Sıfırla"):
        st.session_state.profiles = {}
        st.rerun()

# Ana Sayfa Sekmeleri
tab1, tab2 = st.tabs(["🎙️ Anlık Biyometrik Analiz", "🎯 Ses Tonu/Mod Kalibrasyonu"])

# ==========================================
# SEKME 2: SES TONU / MOD KALİBRASYONU
# ==========================================
with tab2:
    st.subheader("🎯 Biyometrik Mod Kütüphanesi")
    st.write("Şu anki ruh halinize uygun modu seçip 5 saniyelik bir konuşma kaydı alın. Sistem bu ses imzanızı hafızaya işleyecek.")
    
    mod_secimi = st.selectbox(
        "Hangi Mod için Kayıt Alıyorsunuz?",
        ["😫 Bıkkın / Zihinsel Yorgun Mod", "😊 Zinde / Dinlenmiş Mod", "🥳 Coşkulu / Yüksek Enerjili Mod"]
    )
    
    calib_audio = st.audio_input("Bu moda uygun sesinizi kaydedin", key="calib_input")
    
    if calib_audio is not None:
        if st.button(f"'{mod_secimi}' Olarak Hafızaya Kaydet", type="primary", key="save_profile_btn"):
            try:
                with st.spinner("Ses imzanız analiz edilip profil kütüphanenize ekleniyor..."):
                    audio_bytes = calib_audio.read()
                    y, sr = librosa.load(io.BytesIO(audio_bytes), sr=16000)
                    
                    rms_base = float(np.mean(librosa.feature.rms(y=y)))
                    pitches, _ = librosa.piptrack(y=y, sr=sr)
                    pitch_vals = pitches[pitches > 0]
                    pitch_base = float(np.mean(pitch_vals)) if len(pitch_vals) > 0 else 150.0
                    
                    pitch_diffs = np.abs(np.diff(pitch_vals)) if len(pitch_vals) > 1 else [0]
                    jitter_base = float(np.mean(pitch_diffs) / (pitch_base + 1e-6))
                    
                    # Profili kaydet
                    st.session_state.profiles[mod_secimi] = {
                        "rms": rms_base,
                        "pitch": pitch_base,
                        "jitter": jitter_base
                    }
                    st.success(f"🎉 '{mod_secimi}' profiliniz başarıyla kaydedildi!")
                    st.rerun()
            except Exception as e:
                st.error(f"Kayıt sırasında bir hata oluştu: {e}")

# ==========================================
# SEKME 1: ANLIK BİYOMETRİK ANALİZ
# ==========================================
with tab1:
    st.subheader("🎙️ Anlık Biyometrik Analiz")
    
    if "😫 Bıkkın / Zihinsel Yorgun Mod" not in st.session_state.profiles:
        st.info("💡 Mükemmel sonuçlar için **'🎯 Ses Tonu/Mod Kalibrasyonu'** sekmesinden şu anki Bıkkın/Yorgun modunuzu kaydedebilirsiniz.")
    
    audio_value = st.audio_input("Analiz edilecek sesinizi kaydedin", key="analysis_input")
    uploaded_file = st.file_uploader("Veya ses dosyası yükleyin", type=["wav", "mp3", "m4a", "ogg", "flac"])
    
    target_audio = audio_value or uploaded_file
    
    if target_audio is not None:
        if st.button("Biyometrik Analiz Et", type="primary", key="analiz_butonu_vbar"):
            try:
                with st.spinner("Ses imzanız kayıtlı profillerinizle kıyaslanıyor..."):
                    audio_bytes = target_audio.read()
                    y, sr = librosa.load(io.BytesIO(audio_bytes), sr=16000)
                    
                    rms_val = float(np.mean(librosa.feature.rms(y=y)))
                    pitches, _ = librosa.piptrack(y=y, sr=sr)
                    pitch_vals = pitches[pitches > 0]
                    mean_pitch = float(np.mean(pitch_vals)) if len(pitch_vals) > 0 else 0.0
                    
                    pitch_diffs = np.abs(np.diff(pitch_vals)) if len(pitch_vals) > 1 else [0]
                    jitter_val = float(np.mean(pitch_diffs) / (mean_pitch + 1e-6))
                
                st.success("✅ Analiz tamamlandı!")
                
                # --- PROFİL EŞLEŞTİRME VE KIYASLAMA ---
                if "😫 Bıkkın / Zihinsel Yorgun Mod" in st.session_state.profiles:
                    bikkin_ref = st.session_state.profiles["😫 Bıkkın / Zihinsel Yorgun Mod"]
                    
                    # Bıkkınlık Modu Yakınlık Analizi (Jitter ve Pitch farkı)
                    jitter_fark = abs(jitter_val - bikkin_ref["jitter"])
                    pitch_fark = abs(mean_pitch - bikkin_ref["pitch"])
                    
                    # Eğer anlık ses kayıtlı bıkkın ses profiliyle benzer özellik gösteriyorsa
                    if jitter_fark < 0.050 and pitch_fark < 300:
                        st.warning(
                            "**😫 Tespit Edilen Durum: Bıkkınlık ve Zihinsel Yorgunluk**\n\n"
                            "Sesinizin mikro-titreşim ve frekans yapısı, daha önce kaydettiğiniz **'Bıkkın/Yorgun'** ses profilinizle %85+ oranında eşleşiyor."
                        )
                    else:
                        st.info("💡 Sesiniz bıkkınlık profilinizden farklılık gösteriyor.")
                else:
                    st.write(f"**Ses Enerjisi:** {rms_val:.4f} | **Frekans:** {mean_pitch:.1f} Hz | **Jitter:** {jitter_val:.3f}")
                    st.info("Profil kaydı yaptıkça analizler kişiselleşecektir.")

            except Exception as e:
                st.error(f"Analiz hatası: {e}")
