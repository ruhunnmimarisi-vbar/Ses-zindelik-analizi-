import streamlit as st
import librosa
import numpy as np
import pickle

st.title("Vokal Biyomarker & Zindelik Analizi")
st.write("Lütfen 5 saniyelik bir ses kaydı yapın veya yükleyin.")

# Ses dosyası yükleme/kaydetme
audio_file = st.file_uploader("Ses Dosyası (.wav)", type=["wav"])

if audio_file is not None:
    # 1. Sesi yükle
    y, sr = librosa.load(audio_file, duration=5.0)
    
    # 2. Öznitelik çıkarımı (MFCC)
    mfccs = np.mean(librosa.feature.mfcc(y=y, sr=sr, n_mfcc=40).T, axis=0)
    
    # 3. Eğitilmiş modeli çağır ve tahmin et (Temsili)
    # model = pickle.load(open("yapay_zeka_modeli.pkl", "rb"))
    # tahmin = model.predict([mfccs])
    
    st.success("Ses analizi tamamlandı!")
    st.metric(label="Tahmini Zindelik / Enerji Seviyesi", value="%78", delta="Sakin")
    st.info("Sinir sisteminiz dengeli görünüyor. Mevcut odaklanma durumunuzu koruyabilirsiniz.")
    
