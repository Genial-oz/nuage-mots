# [ANCRE_DEBUT_IMPORTS]
import streamlit as st
import pandas as pd
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
import io
import numpy as np
import cv2 
import os
import plotly.express as px
import re
# [ANCRE_FIN_IMPORTS]

# Configuration de la page
st.set_page_config(page_title="Nuage de mots", layout="wide")

# --- INITIALISATION DE LA SESSION ---
if 'manual_stopwords' not in st.session_state:
    st.session_state.manual_stopwords = set()

# --- LISTE DE NETTOYAGE FRANÇAIS ---
STOPWORDS_FR = {
    "le", "la", "les", "du", "des", "de", "un", "une", "et", "est", "sont", "pour", "dans", "avec", 
    "sur", "plus", "fait", "tout", "tous", "cette", "ces", "mon", "ton", "son", "notre", "votre", 
    "leur", "aux", "pas", "plus", "très", "donc", "mais", "car", "chez", "être", "avoir", "faire",
    "nous", "vous", "ils", "elles", "que", "qui", "quoi", "dont", "où", "par", "pour", "dans", "ce", "ci",
    "été", "étée", "était", "étaient", "grâce", "grace", "selon", "entre", "lors", "ceux", "celles",
    "chaque", "certains", "certaines", "après", "avant", "depuis", "durant", "pendant", "environ", 
    "presque", "toujours", "souvent", "parfois", "jamais", "année", "annuel", "mensuel", "période", 
    "actuel", "suite", "cadre", "effet", "également", "ainsi", "alors", "encore", "déjà", "enfin", 
    "notamment", "particulièrement", "assez", "beaucoup", "autre", "autres", "comme", "quand", 
    "si", "bien", "peut", "peuvent", "doit", "doivent", "aussi"
}

# --- STYLE CSS ---
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; background-color: #007bff; color: white; height: 3em; }
    .stDownloadButton>button { background-color: #28a745 !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("☁️ Nuage de mots")

# --- ÉTAPE 1 : CHARGEMENT DU FICHIER PRINCIPAL ---
uploaded_file = st.file_uploader("📂 Parcourir les fichiers (Fichier Excel principal .xlsx)", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    target_column = st.selectbox("Sélectionnez la colonne à analyser :", df.columns)

    st.divider()

    # --- ÉTAPE 2 : GESTION DES MOTS INTERDITS ---
    st.header("🚫 Gestion des exclusions")
    col_ex1, col_ex2 = st.columns(2)
    with col_ex1:
        manual_input = st.text_input("Taper des mots à bannir (virgules) :")
        if manual_input:
            words_to_add = [w.strip().lower() for w in manual_input.split(",") if w.strip()]
            st.session_state.manual_stopwords.update(words_to_add)
    with col_ex2:
        file_stop = st.file_uploader("Excel de mots interdits", type=["xlsx"], key="stop_file")
        if file_stop:
            df_stop = pd.read_excel(file_stop)
            stop_list = df_stop.iloc[:, 0].dropna().astype(str).str.lower().tolist()
            st.session_state.manual_stopwords.update(stop_list)

    if st.session_state.manual_stopwords:
        with st.expander(f"📋 Liste des mots exclus ({len(st.session_state.manual_stopwords)})"):
            st.write(", ".join(sorted(st.session_state.manual_stopwords)))
            if st.button("🗑️ Réinitialiser"):
                st.session_state.manual_stopwords = set()
                st.rerun()

    st.divider()

    # --- ÉTAPE 3 : ANALYSE ET GÉNÉRATION ---
    FINAL_STOPWORDS = STOPWORDS.union(STOPWORDS_FR).union(st.session_state.manual_stopwords)
    text_list = df[target_column].dropna().astype(str).tolist()
    full_text = " ".join(text_list).lower()
    full_text = re.sub(r"\b[ldjns]['’]", " ", full_text)
    full_text = re.sub(r'[^\w\s]', ' ', full_text)

    # Analyse fréquences
    st.subheader("📊 Analyse des fréquences")
    top_n = st.number_input("Top mots :", 5, 100, 10)
    temp_wc = WordCloud(stopwords=FINAL_STOPWORDS, min_word_length=4).process_text(full_text)
    sorted_freq = sorted(temp_wc.items(), key=lambda x: x[1], reverse=True)[:top_n]
    
    cols = st.columns(5) 
    for i, (word, count) in enumerate(sorted_freq):
        with cols[i % 5]:
            st.markdown(f"**{word}** ({count})")
            if st.button(f"Exclure", key=f"btn_{word}"):
                st.session_state.manual_stopwords.add(word)
                st.rerun()

    st.divider()

    col_btn1, col_btn2 = st.columns(2)
    with col_btn1: btn_static = st.button("🚀 Vue Fixe")
    with col_btn2: btn_video = st.button("🎬 Créer l'Animation")

    with st.sidebar:
        st.header("🎨 Réglages")
        max_w = st.slider("Mots max", 10, 150, 50)
        palette = st.selectbox("Palette", ["viridis", "plasma", "magma", "coolwarm", "Spectral"])
        bg_col = st.color_picker("Fond", "#ffffff")
        fps = st.slider("Vitesse (FPS)", 5, 30, 15)
        pause_f = st.slider("Pause finale (sec)", 1, 15, 5)

    if btn_static:
        wc = WordCloud(background_color=bg_col, max_words=max_w, colormap=palette, width=1200, height=600, stopwords=FINAL_STOPWORDS, min_word_length=4).generate(full_text)
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.imshow(wc, interpolation='bilinear')
        ax.axis("off")
        st.pyplot(fig)

    if btn_video:
        with st.spinner("🎬 Génération de l'animation en cours..."):
            proc_tags = WordCloud(stopwords=FINAL_STOPWORDS, min_word_length=4).process_text(full_text)
            sorted_words = sorted(proc_tags.items(), key=lambda x: x[1], reverse=True)[:max_w]
            
            # Utilisation de mp4v (plus robuste à la création)
            video_filename = "animation.mp4"
            fourcc = cv2.VideoWriter_fourcc(*'mp4v') 
            video_out = cv2.VideoWriter(video_filename, fourcc, fps, (1280, 720))
            
            words_to_show = []
            last_frame = None
            for word, freq in sorted_words:
                words_to_show.append(word)
                wc_frame = WordCloud(background_color=bg_col, max_words=max_w, colormap=palette, 
                                     width=1280, height=720, stopwords=FINAL_STOPWORDS, 
                                     min_word_length=4).generate(" ".join(words_to_show))
                
                # Conversion propre Image -> Array -> BGR pour OpenCV
                frame = cv2.cvtColor(np.array(wc_frame.to_image()), cv2.COLOR_RGB2BGR)
                for _ in range(3): # Répéter l'image pour fluidité
                    video_out.write(frame)
                last_frame = frame
            
            # Pause finale
            if last_frame is not None:
                for _ in range(fps * pause_f):
                    video_out.write(last_frame)
            
            video_out.release()
            
            # Vérification et Affichage
            if os.path.exists(video_filename):
                with open(video_filename, "rb") as f:
                    v_bytes = f.read()
                st.video(v_bytes) # L'affichage binaire aide Streamlit Cloud
                st.download_button("📥 Télécharger la vidéo", v_bytes, "animation.mp4")
            else:
                st.error("Erreur lors de la création du fichier vidéo.")
else:
    st.info("👋 Veuillez charger votre fichier Excel principal.")