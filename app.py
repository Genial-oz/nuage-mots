# [ANCRE_DEBUT_IMPORTS]
import streamlit as st
import pandas as pd
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
import io
import random
import numpy as np
import cv2  # pip install opencv-python
import os
import plotly.express as px
# [ANCRE_FIN_IMPORTS]

# Configuration de la page
st.set_page_config(page_title="WordCloud Master Pro", layout="wide")

# --- STYLE CSS ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; background-color: #007bff; color: white; height: 3em; }
    .stDownloadButton>button { background-color: #28a745 !important; color: white !important; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

st.title("☁️ WordCloud Master Pro")
st.subheader("Analyse de texte, Visualisation et Animation Vidéo")

# --- SECTION 0 : GÉNÉRATEUR DE TEST ---
# [ANCRE_DEBUT_TEST_EXCEL]
with st.expander("🛠️ Générer un fichier Excel de test (500 lignes)"):
    def get_test_excel():
        mots_pondérés = (["Python"] * 150 + ["Data"] * 110 + ["IA"] * 80 + 
                         ["Streamlit"] * 60 + ["Analyse"] * 40 + ["Vidéo"] * 40 +
                         ["Code"] * 20 + ["Dashboard"] * 10)
        random.shuffle(mots_pondérés)
        df_test = pd.DataFrame(mots_pondérés, columns=["Texte_A_Analyser"])
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_test.to_excel(writer, index=False)
        return output.getvalue()

    st.download_button(
        label="📥 Télécharger le fichier de test.xlsx",
        data=get_test_excel(),
        file_name="test_wordcloud.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
# [ANCRE_FIN_TEST_EXCEL]

st.divider()

# --- SECTION 1 : BARRE LATÉRALE (RÉGLAGES) ---
# [ANCRE_DEBUT_SIDEBAR]
with st.sidebar:
    st.header("🎨 Réglages Visuels")
    max_w = st.slider("Nombre de mots", 10, 150, 50)
    palette = st.selectbox("Palette de couleurs", ["viridis", "plasma", "magma", "coolwarm", "Spectral"])
    bg_col = st.color_picker("Couleur de fond", "#ffffff")
    
    st.header("🎞️ Paramètres Vidéo")
    fps = st.slider("Images par seconde (Vitesse)", 5, 30, 15)
    pause_finale = st.slider("Pause sur l'image finale (sec)", 1, 10, 5)
    st.info("Note : La vidéo sera générée en résolution HD (1280x720).")
# [ANCRE_FIN_SIDEBAR]

# --- SECTION 2 : IMPORT ET ANALYSE ---
uploaded_file = st.file_uploader("📂 Étape 1 : Chargez votre fichier Excel", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    
    col_sel, col_btns = st.columns([2, 2])
    
    with col_sel:
        target_column = st.selectbox("Étape 2 : Colonne à analyser", df.columns)
    
    # Préparation du texte pour les moteurs
    text_data = df[target_column].dropna().astype(str).tolist()
    full_text = " ".join(text_data)

    with col_btns:
        st.write("##") # Calage
        c1, c2 = st.columns(2)
        with c1:
            generate_static = st.button("🚀 Vue Fixe / Data")
        with c2:
            generate_video = st.button("🎬 Créer la Vidéo")

    # --- PARTIE A : AFFICHAGE FIXE ET INTERACTIF ---
    if generate_static:
        wc_static = WordCloud(background_color=bg_col, max_words=max_w, colormap=palette, 
                              width=1200, height=600, stopwords=STOPWORDS).generate(full_text)
        
        tab1, tab2 = st.tabs(["🖼️ Image Fixe", "📊 Analyse Interactive (Plotly)"])
        
        with tab1:
            fig, ax = plt.subplots(figsize=(12, 6))
            ax.imshow(wc_static, interpolation='bilinear')
            ax.axis("off")
            st.pyplot(fig)
            
            # Export PNG
            buf = io.BytesIO()
            fig.savefig(buf, format="png")
            st.download_button("📥 Télécharger le PNG", buf.getvalue(), "nuage.png", "image/png")

        with tab2:
            # Graphique interactif des fréquences
            df_plot = pd.DataFrame(list(wc_static.words_.items()), columns=['Mot', 'Score']).head(max_w)
            df_plot['Importance (%)'] = (df_plot['Score'] * 100).round(2)
            
            fig_p = px.bar(df_plot, x='Importance (%)', y='Mot', orientation='h', 
                           color='Importance (%)', color_continuous_scale=palette,
                           title="Fréquence relative des mots")
            fig_p.update_layout(yaxis={'categoryorder':'total ascending'}, height=600)
            st.plotly_chart(fig_p, use_container_width=True)

    # --- PARTIE B : GÉNÉRATION DE L'ANIMATION VIDÉO ---
    if generate_video:
        with st.spinner("🎬 Compilation de la vidéo en cours..."):
            # Calcul des mots clés par ordre d'importance
            words_dict = WordCloud().process_text(full_text)
            sorted_words = sorted(words_dict.items(), key=lambda x: x[1], reverse=True)[:max_w]
            
            video_filename = "mon_nuage_anime.mp4"
            w, h = 1280, 720
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            video_out = cv2.VideoWriter(video_filename, fourcc, fps, (w, h))

            # 1. Animation : Apparition progressive
            words_to_draw = []
            for word, freq in sorted_words:
                words_to_draw.append(word)
                temp_text = " ".join(words_to_draw)
                
                # Génération de la frame
                wc_frame = WordCloud(background_color=bg_col, max_words=max_w, 
                                     colormap=palette, width=w, height=h).generate(temp_text)
                
                # Conversion Image -> OpenCV
                frame = np.array(wc_frame.to_image())
                frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                
                # On écrit chaque frame 3 fois pour fluidifier l'apparition
                for _ in range(3):
                    video_out.write(frame)

            # 2. Final : Pause sur le nuage complet
            for _ in range(fps * pause_finale):
                video_out.write(frame)
            
            video_out.release()

            # Résultat
            if os.path.exists(video_filename):
                st.success(f"✅ Vidéo générée avec succès !")
                with open(video_filename, "rb") as vf:
                    st.video(vf)
                    st.download_button("📥 Télécharger la vidéo MP4", vf, file_name="animation_nuage.mp4")
else:
    st.info("☝️ Commencez par charger un fichier Excel ou générez-en un de test ci-dessus.")