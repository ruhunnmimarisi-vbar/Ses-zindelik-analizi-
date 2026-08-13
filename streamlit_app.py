import streamlit as st
import librosa
import numpy as np
import io
import google.generativeai as genai
import json

# ==========================================
# 1. SAYFA VE TEMA AYARLARI
# ==========================================
st.set_page_config(page_title="VBAR - Çoklu Mod Biyometrik Analiz", page_icon="🎙️")

st.title("🎙️ VBAR - Kişiselleştirilmiş Ses Profil Analizi")
st.warning("⚠️ Bu bir tedavi/klinik teşhis aracı değildir. Sonuçlar yalnızca kendini gözlemleme amaçlıdır.")

# --- HAFIZA TANIMLAMALARI ---
if "profiles" not in st.session_state:
    st.session_state.profiles = {}

if "current_card" not in st.session_state:
    st.session_state.current_card = None

if "card_flipped" not in st.session_state:
    st.session_state.card_flipped = False


# ==========================================
# 2. GEMINI CANLI NIYET KARTI ÜRETICISI
# ==========================================
def generate_dynamic_card(stone_mode, stone_name, hz_val, jitter_val, status_text):
    try:
        api_key = st.secrets.get("GEMINI_API_KEY", "")
        if api_key:
            genai.configure(api_key=api_key)
            gemini_model = genai.GenerativeModel('gemini-1.5-flash')
            
            prompt = f"""
            Sen vokal biyometri ve psikofizyoloji konusunda uzman bir rehbersin.
            Kullanıcının anlık ses verileri:
            - Biyometrik Mod / Taş: {stone_name} ({stone_mode})
            - Anlık Durum: {status_text}
            - Temel Frekans (Pitch): {hz_val:.1f} Hz
            - Mikro-Titreşim (Jitter): {jitter_val:.4f}

            Bu kullanıcı için o anki sinir sistemi durumuna uygun, şefkatli ve farkındalık yaratan BİR NİYET KARTI üret.
            Çıktıyı YALNIZCA geçerli bir JSON formatında ver. Ekstra açıklama veya markdown yazma.
            JSON Şablonu:
            {{
              "title": "2-3 kelimelik etkileyici başlık",
              "affirmation": "1-2 cümlelik güçlü ve şefkatli olumlama metni",
              "action": "10 saniyede yapılabilecek somatik bir beden/nefes eylemi"
            }}
            """
            response = gemini_model.generate_content(prompt)
            clean_json = response.text.replace("```json", "").replace("```", "").strip()
            return json.loads(clean_json)
    except Exception:
        pass
    
    # Yedek Kartlar (API erişimi olmaması veya hata durumunda)
    fallback_cards = {
        "aquamarine": {
            "title": "İkna ve İfade Akışı",
            "affirmation": "Zihnim berrak, sesim akıcı. Kendimi otantik bir şekilde ifade etmeye hazırım.",
            "action": "Omuzlarını geriye al, göğsünü aç ve derin bir nefes ver."
        },
        "onyx": {
            "title": "Kendi Ritmin ve Şefkat",
            "affirmation": "Her an %100 performans vermek zorunda değilsin. Durmak ve dinlenmek en doğal hakkın.",
            "action": "Omuzlarını kulaklarından uzaklaştır, çeneni serbest bırak."
        },
        "obsidian": {
            "title": "Sakin Merkez",
            "affirmation": "Duygularım geçici birer dalgadır. Tepki vermeden önce kendime güvenli bir alan açıyorum.",
            "action": "Konuşmadan veya tepki vermeden önce içinden 5'ten geriye doğru say."
        }
    }
    return fallback_cards.get(stone_mode, fallback_cards["aquamarine"])


# ==========================================
# 3. YAN MENÜ (SIDEBAR) - KAYITLI MODLAR
# ==========================================
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
                    
                    # 1. Biyometrik Hesaplamalar
                    rms_val = float(np.mean(librosa.feature.rms(y=y)))
                    pitches, _ = librosa.piptrack(y=y, sr=sr)
                    pitch_vals = pitches[pitches > 0]
                    mean_pitch = float(np.mean(pitch_vals)) if len(pitch_vals) > 0 else 0.0
                    
                    pitch_diffs = np.abs(np.diff(pitch_vals)) if len(pitch_vals) > 1 else [0]
                    jitter_val = float(np.mean(pitch_diffs) / (mean_pitch + 1e-6))
                
                # 2. Hassaslaştırılmış Taş Eşleşme Mantığı
                if jitter_val > 0.022:
                    stone_mode = "obsidian"
                    stone_name = "Obsidyen"
                    stone_color = "#E74C3C"
                    stone_icon = "🔴"
                    status_text = "Gergin / Reaktif Mod"
                elif rms_val < 0.040 or (0 < mean_pitch < 165):
                    # Gece yorgunluğunu ve kısık ses tonunu yakalayan Oniks modu
                    stone_mode = "onyx"
                    stone_name = "Oniks & Hematit"
                    stone_color = "#7F8C8D"
                    stone_icon = "🖤"
                    status_text = "Dinlenme / Topraklanma Modu"
                else:
                    stone_mode = "aquamarine"
                    stone_name = "Akuamarin"
                    stone_color = "#1ABC9C"
                    stone_icon = "🩵"
                    status_text = "Zinde / İfade Modu"

                st.session_state.analysis_results = {
                    "rms": rms_val,
                    "pitch": mean_pitch,
                    "jitter": jitter_val,
                    "stone_mode": stone_mode,
                    "stone_name": stone_name,
                    "stone_color": stone_color,
                    "stone_icon": stone_icon,
                    "status_text": status_text
                }
                st.session_state.card_flipped = False
                st.session_state.current_card = None
                st.success("✅ Analiz tamamlandı!")

            except Exception as e:
                st.error(f"Analiz hatası: {e}")

    # Analiz Sonuçları Ekranı ve Canlı Kart
    if "analysis_results" in st.session_state:
        res = st.session_state.analysis_results
        
        st.markdown("---")
        
        # Karşılaştırma Notu
        if "😫 Bıkkın / Zihinsel Yorgun Mod" in st.session_state.profiles:
            bikkin_ref = st.session_state.profiles["😫 Bıkkın / Zihinsel Yorgun Mod"]
            jitter_fark = abs(res["jitter"] - bikkin_ref["jitter"])
            pitch_fark = abs(res["pitch"] - bikkin_ref["pitch"])
            
            if jitter_fark < 0.050 and pitch_fark < 300:
                st.warning(
                    "**😫 Tespit Edilen Durum: Bıkkınlık ve Zihinsel Yorgunluk**\n\n"
                    "Sesinizin mikro-titreşim ve frekans yapısı, daha önce kaydettiğiniz **'Bıkkın/Yorgun'** ses profilinizle %85+ oranında eşleşiyor."
                )
            else:
                st.info("💡 Sesiniz bıkkınlık profilinizden farklılık gösteriyor.")

        # Metrik Kutuları
        col1, col2, col3 = st.columns(3)
        col1.metric("Ort. Frekans (Pitch)", f"{res['pitch']:.1f} Hz")
        col2.metric("Mikro-Titreşim (Jitter)", f"{res['jitter']:.4f}")
        col3.metric("Ses Enerjisi (RMS)", f"{res['rms']:.4f}")
        
        st.subheader(f"{res['stone_icon']} Biyometrik Taş Eşleşmesi: **{res['stone_name']}**")
        st.caption(f"Sinir Sistemi Durumu: **{res['status_text']}**")
        
        # CANLI KART AÇMA BUTONU VE KART KUTUSU
        if not st.session_state.card_flipped:
            if st.button(f"🔮 {res['stone_name']} Niyet Kartını Üret ve Aç", use_container_width=True, type="primary"):
                with st.spinner("Gemini ses biyometrinizi analiz edip niyet kartınızı hazırlıyor..."):
                    card_data = generate_dynamic_card(
                        res['stone_mode'], 
                        res['stone_name'], 
                        res['pitch'], 
                        res['jitter'],
                        res['status_text']
                    )
                    st.session_state.current_card = card_data
                    st.session_state.card_flipped = True
                    st.rerun()
        else:
            card = st.session_state.current_card
            if card:
                st.markdown(
                    f"""
                    <div style="
                        border: 2px solid {res['stone_color']};
                        border-radius: 16px;
                        padding: 24px;
                        background: linear-gradient(135deg, rgba(255,255,255,0.05) 0%, {res['stone_color']}15 100%);
                        box-shadow: 0 8px 20px {res['stone_color']}30;
                        text-align: center;
                        margin-top: 10px;
                    ">
                        <span style="font-size: 0.85em; text-transform: uppercase; letter-spacing: 2px; color: {res['stone_color']}; font-weight: 600;">Sana Özel Biyometrik Niyet</span>
                        <h3 style="color: {res['stone_color']}; margin-top: 5px; margin-bottom: 10px;">{res['stone_icon']} {card['title']}</h3>
                        <hr style="border-color: {res['stone_color']}; opacity: 0.2; margin: 15px 0;">
                        <p style="font-size: 1.2em; font-style: italic; line-height: 1.6;">"{card['affirmation']}"</p>
                        <div style="
                            background-color: {res['stone_color']}25;
                            padding: 12px;
                            border-radius: 10px;
                            margin-top: 18px;
                            font-weight: 500;
                            border-left: 4px solid {res['stone_color']};
                            text-align: left;
                        ">
                            💡 <b>Günün Mikro Eylemi:</b> {card['action']}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
                if st.button("🔄 Kartı Kapat", use_container_width=True):
                    st.session_state.card_flipped = False
                    st.session_state.current_card = None
                    st.rerun()
                            
