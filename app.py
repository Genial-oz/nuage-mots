# [ANCRE_DEBUT_IMPORTS]
import streamlit as st
import pandas as pd
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
import io
import numpy as np
import os
import plotly.express as px
import re
import imageio
from PIL import Image, ImageDraw
# [ANCRE_FIN_IMPORTS]

# Configuration de la page
st.set_page_config(page_title="Nuage de mots Pro", layout="wide")

# --- INITIALISATION DE LA SESSION ---
if 'manual_stopwords' not in st.session_state:
    st.session_state.manual_stopwords = set()

# --- LISTE DE NETTOYAGE FRANÇAIS ---
STOPWORDS_FR = {"le", "la", "les", "du", "des", "de", "un", "une", "et", "est", "sont", "pour", "dans", "avec", "sur", "plus", "fait", "tout", "tous", "cette", "ces", "mon", "ton", "son", "notre", "votre", "leur", "aux", "pas", "plus", "très", "donc", "mais", "car", "chez", "être", "avoir", "faire", "nous", "vous", "ils", "elles", "que", "qui", "quoi", "dont", "où", "par", "pour", "dans", "ce", "ci", "été", "étée", "était", "étaient", "grâce", "grace", "selon", "entre", "lors", "ceux", "celles", "chaque", "certains", "certaines", "après", "avant", "depuis", "durant", "pendant", "environ", "presque", "toujours", "souvent", "parfois", "jamais", "année", "annuel", "mensuel", "période", "actuel", "suite", "cadre", "effet", "également", "ainsi", "alors", "encore", "déjà", "enfin", "notamment", "particulièrement", "assez", "beaucoup", "autre", "autres", "comme", "quand", "si", "bien", "peut", "peuvent", "doit", "doivent", "aussi"}

# --- FONCTION POUR GÉNÉRER DES FORMES ---
def get_shape_mask(shape_name):
    size = (800, 800)
    img = Image.new("L", size, 255) 
    draw = ImageDraw.Draw(img)
    if shape_name == "Cercle":
        draw.ellipse([50, 50, 750, 750], fill=0)
    elif shape_name == "Carré":
        draw.rectangle([100, 100, 700, 700], fill=0)
    elif shape_name == "Cœur":
        draw.polygon([(400, 750), (50, 400), (150, 150), (400, 300), (650, 150), (750, 400)], fill=0)
    elif shape_name == "Étoile":
        draw.polygon([(400, 50), (500, 300), (750, 300), (550, 450), (650, 750), (400, 600), (150, 750), (250, 450), (50, 300), (300, 300)], fill=0)
    elif shape_name == "Bulle":
        draw.ellipse([100, 100, 700, 600], fill=0)
        draw.polygon([(200, 550), (100, 750), (350, 580)], fill=0)
    return np.array(img)

# --- STYLE CSS ---
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; background-color: #007bff; color: white; height: 3em; }
    .stDownloadButton>button { background-color: #28a745 !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("☁️ Nuage de mots")

# --- ÉTAPE 1 : CHARGEMENT DU FICHIER ---
uploaded_file = st.file_uploader("📂 Parcourir les fichiers (Excel .xlsx)", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    target_column = st.selectbox("Sélectionnez la colonne à analyser :", df.columns)

    st.divider()

    # --- ÉTAPE 2 : GESTION DES MOTS INTERDITS ---
    st.header("🚫 Gestion des exclusions")
    col_ex1, col_ex2 = st.columns(2)

    with col_ex1:
        manual_input = st.text_input("Taper des mots à bannir (séparés par des virgules) :")
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
        with st.expander(f"📋 Liste actuelle des mots exclus ({len(st.session_state.manual_stopwords)})"):
            st.write(", ".join(sorted(st.session_state.manual_stopwords)))
            if st.button("🗑️ Réinitialiser la liste"):
                st.session_state.manual_stopwords = set()
                st.rerun()

    st.divider()

    # --- ÉTAPE 3 : ANALYSE ET FILTRAGE ---
    FINAL_STOPWORDS = STOPWORDS.union(STOPWORDS_FR).union(st.session_state.manual_stopwords)
    text_list = df[target_column].dropna().astype(str).tolist()
    full_text = " ".join(text_list).lower()
    full_text = re.sub(r"\b[ldjns]['’]", " ", full_text)
    full_text = re.sub(r'[^\w\s]', ' ', full_text)

    st.subheader("📊 Analyse des fréquences")
    top_n = st.number_input("Nombre de mots dans le Top :", 5, 100, 10)
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

    # --- RÉGLAGES SIDEBAR ---
    with st.sidebar:
        st.header("🎨 Réglages Visuels")
        shape_choice = st.selectbox("Forme du nuage", ["Rectangle", "Cercle", "Carré", "Cœur", "Étoile", "Bulle", "Image personnalisée"])
        
        custom_mask = None
        if shape_choice == "Image personnalisée":
            mask_file = st.file_uploader("Image (Noir sur blanc)", type=["png", "jpg", "jpeg"])
            if mask_file:
                custom_mask = np.array(Image.open(mask_file).convert("L"))
                custom_mask = np.where(custom_mask > 128, 255, 0)
        elif shape_choice != "Rectangle":
            custom_mask = get_shape_mask(shape_choice)

        max_w = st.slider("Nombre max de mots", 10, 200, 50)
        palette = st.selectbox("Palette de couleurs", ["viridis", "plasma", "magma", "coolwarm", "Spectral"])
        
        with st.expander("❓ Aide sur les palettes"):
            st.markdown("- **Viridis** : Pro (Violet-Jaune)\n- **Plasma** : Dynamique\n- **Magma** : Contrasté\n- **Coolwarm** : Équilibré\n- **Spectral** : Arc-en-ciel")
            
        bg_col = st.color_picker("Couleur de fond", "#ffffff")
        
        st.header("🎞️ Paramètres Vidéo")
        fps = st.slider("Vitesse (FPS)", 5, 30, 15)
        pause_finale = st.slider("Pause finale (sec)", 1, 15, 5)

    col_btn1, col_btn2 = st.columns(2)
    with col_btn1: btn_static = st.button("🚀 Générer Vue Fixe")
    with col_btn2: btn_video = st.button("🎬 Créer l'Animation")

    if btn_static:
        wc = WordCloud(background_color=bg_col, max_words=max_w, colormap=palette, 
                       width=1200, height=800, mask=custom_mask, 
                       stopwords=FINAL_STOPWORDS, min_word_length=4).generate(full_text)
        
        tab1, tab2 = st.tabs(["🖼️ Image Fixe", "📈 Graphique"])
        with tab1:
            fig, ax = plt.subplots(figsize=(12, 8))
            ax.imshow(wc, interpolation='bilinear')
            ax.axis("off")
            st.pyplot(fig)
            buf = io.BytesIO()
            fig.savefig(buf, format="png")
            st.download_button("📥 Télécharger PNG", buf.getvalue(), "nuage.png", "image/png")
        with tab2:
            df_plot = pd.DataFrame(list(wc.words_.items()), columns=['Mot', 'Importance']).head(max_w)
            st.plotly_chart(px.bar(df_plot, x='Importance', y='Mot', orientation='h', color='Importance', color_continuous_scale=palette))

    if btn_video:
        with st.spinner("🎬 Compilation vidéo..."):
            proc_tags = WordCloud(stopwords=FINAL_STOPWORDS, min_word_length=4).process_text(full_text)
            sorted_words = sorted(proc_tags.items(), key=lambda x: x[1], reverse=True)[:max_w]
            
            video_filename = "animation.mp4"
            frames = []
            words_to_show = []
            v_mask = custom_mask
            v_w, v_h = (800, 800) if v_mask is not None else (1280, 720)

            for word, _ in sorted_words:
                words_to_show.append(word)
                wc_frame = WordCloud(background_color=bg_col, max_words=max_w, colormap=palette, 
                                     width=v_w, height=v_h, mask=v_mask, 
                                     stopwords=FINAL_STOPWORDS, min_word_length=4).generate(" ".join(words_to_show))
                frames.append(np.array(wc_frame.to_image()))
            
            for _ in range(fps * pause_finale): frames.append(frames[-1])
            imageio.mimsave(video_filename, frames, fps=fps, codec='libx264')
            
            with open(video_filename, "rb") as f:
                v_bytes = f.read()
            st.video(v_bytes)
            st.download_button("📥 Télécharger la vidéo", v_bytes, "nuage_anime.mp4")
else:
    st.info("👋 Bonjour ! Veuillez charger votre fichier Excel.")