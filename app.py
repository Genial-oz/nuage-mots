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

st.set_page_config(page_title="Nuage de mots", layout="wide")

# --- LISTE DE NETTOYAGE FRANÇAIS (Stopwords) ---
STOPWORDS_FR = set([
    "le", "la", "les", "du", "des", "de", "un", "une", "et", "est", "sont", "pour", "dans", "avec", 
    "sur", "plus", "fait", "tout", "tous", "cette", "ces", "mon", "ton", "son", "notre", "votre", 
    "leur", "aux", "pas", "plus", "très", "donc", "mais", "car", "chez", "être", "avoir", "faire",
    "nous", "vous", "ils", "elles", "que", "qui", "quoi", "dont", "où", "par", "pour", "dans", "ce", "ci",
    "une", "les", "des", "été", "être", "avoir", "plus", "avec", "dans"
])
ALL_STOPWORDS = STOPWORDS.union(STOPWORDS_FR)

# --- STYLE CSS ---
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; background-color: #007bff; color: white; height: 3em; }
    .stDownloadButton>button { background-color: #28a745 !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("☁️ Nuage de mots")

# --- GÉNÉRATEUR DE TEST ---
with st.expander("🛠️ Générer un fichier de test (Vérification du filtrage strict)"):
    def get_test_excel():
        phrases = [
            "L'emploi des agents est une priorité pour le service des ressources humaines",
            "La formation sur la sécurité est obligatoire pour tous les nouveaux arrivants",
            "Le rapport social unique présente des données sur les effectifs et la santé",
            "L'absentéisme est en baisse grâce à la prévention sur les postes de travail"
        ] * 40 
        df_test = pd.DataFrame(phrases, columns=["Texte_A_Analyser"])
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_test.to_excel(writer, index=False)
        return output.getvalue()

    st.download_button("📥 Télécharger test_rsu_propre.xlsx", get_test_excel(), "test_rsu.xlsx")

st.divider()

# --- SIDEBAR ---
with st.sidebar:
    st.header("🎨 Réglages Visuels")
    max_w = st.slider("Nombre max de mots", 10, 150, 50)
    palette = st.selectbox("Palette de couleurs", ["viridis", "plasma", "magma", "coolwarm", "Spectral"])
    bg_col = st.color_picker("Couleur de fond", "#ffffff")
    
    st.header("🎞️ Paramètres Vidéo")
    fps = st.slider("Vitesse (FPS)", 5, 30, 15)
    pause_finale = st.slider("Pause finale (sec)", 1, 15, 5)
    st.warning("⚠️ Seuls les mots de 4 lettres ou plus seront affichés.")

# --- TRAITEMENT ---
uploaded_file = st.file_uploader("📂 Chargez votre fichier Excel (.xlsx)", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    target_column = st.selectbox("Sélectionnez la colonne à analyser :", df.columns)
    
    # --- NETTOYAGE AVANCÉ ---
    text_list = df[target_column].dropna().astype(str).tolist()
    full_text = " ".join(text_list).lower()
    
    # 1. On remplace les l', d', j', n' par un espace pour isoler le mot suivant
    full_text = re.sub(r"\b[ldjns]['’]", " ", full_text)
    
    # 2. On supprime la ponctuation
    full_text = re.sub(r'[^\w\s]', ' ', full_text)

    col1, col2 = st.columns(2)
    with col1: btn_static = st.button("🚀 Vue Fixe & Data")
    with col2: btn_video = st.button("🎬 Créer l'Animation")

    if btn_static:
        # min_word_length=4 est la clé ici
        wc = WordCloud(
            background_color=bg_col, max_words=max_w, colormap=palette, 
            width=1200, height=600, stopwords=ALL_STOPWORDS,
            min_word_length=4, collocations=True 
        ).generate(full_text)
        
        tab1, tab2 = st.tabs(["🖼️ Image Fixe", "📊 Analyse Interactive"])
        with tab1:
            fig, ax = plt.subplots(figsize=(12, 6))
            ax.imshow(wc, interpolation='bilinear')
            ax.axis("off")
            st.pyplot(fig)
        with tab2:
            df_plot = pd.DataFrame(list(wc.words_.items()), columns=['Mot', 'Importance']).head(max_w)
            st.plotly_chart(px.bar(df_plot, x='Importance', y='Mot', orientation='h', color='Importance', color_continuous_scale=palette))

    if btn_video:
        with st.spinner("🎬 Compilation de la vidéo HD..."):
            # Application du filtrage strict aussi pour la vidéo
            proc_tags = WordCloud(stopwords=ALL_STOPWORDS, min_word_length=4).process_text(full_text)
            sorted_words = sorted(proc_tags.items(), key=lambda x: x[1], reverse=True)[:max_w]
            
            video_filename = "animation_propre.mp4"
            video_out = cv2.VideoWriter(video_filename, cv2.VideoWriter_fourcc(*'mp4v'), fps, (1280, 720))

            words_to_show = []
            for word, freq in sorted_words:
                words_to_show.append(word)
                wc_frame = WordCloud(background_color=bg_col, max_words=max_w, colormap=palette, 
                                     width=1280, height=720, stopwords=ALL_STOPWORDS, min_word_length=4).generate(" ".join(words_to_show))
                frame = cv2.cvtColor(np.array(wc_frame.to_image()), cv2.COLOR_RGB2BGR)
                for _ in range(3): video_out.write(frame)

            for _ in range(fps * pause_finale): video_out.write(frame)
            video_out.release()
            st.video(video_filename)
else:
    st.info("👋 Chargez un fichier Excel pour commencer l'analyse sans articles.")