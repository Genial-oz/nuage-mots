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
from PIL import Image, ImageDraw, ImageFont 
# [ANCRE_FIN_IMPORTS]

# [ANCRE_DEBUT_CONFIGURATION]
st.set_page_config(page_title="Nuage de mots Pro", page_icon="☁️", layout="wide", initial_sidebar_state="expanded")

if 'manual_stopwords' not in st.session_state:
    st.session_state.manual_stopwords = set()

STOPWORDS_FR = {"le", "la", "les", "du", "des", "de", "un", "une", "et", "est", "sont", "pour", "dans", "avec", "sur", "plus", "fait", "tout", "tous", "cette", "ces", "mon", "ton", "son", "notre", "votre", "leur", "aux", "pas", "plus", "très", "donc", "mais", "car", "chez", "être", "avoir", "faire", "nous", "vous", "ils", "elles", "que", "qui", "quoi", "dont", "où", "par", "pour", "dans", "ce", "ci", "été", "étée", "était", "étaient", "grâce", "grace", "selon", "entre", "lors", "ceux", "celles", "chaque", "certains", "certaines", "après", "avant", "depuis", "durant", "pendant", "environ", "presque", "toujours", "souvent", "parfois", "jamais", "année", "annuel", "mensuel", "période", "actuel", "suite", "cadre", "effet", "également", "ainsi", "alors", "encore", "déjà", "enfin", "notamment", "particulièrement", "assez", "beaucoup", "autre", "autres", "comme", "quand", "si", "bien", "peut", "peuvent", "doit", "doivent", "aussi"}
# [ANCRE_FIN_CONFIGURATION]

# [ANCRE_DEBUT_STYLE_CSS]
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        background-color: #0f172a; /* Slate 900 */
        color: #f8fafc; /* Slate 50 */
    }
    
    /* Forcer la couleur du texte (utile si Streamlit est en mode clair par défaut) */
    p, label, div[data-testid="stMarkdownContainer"] {
        color: #f8fafc !important;
    }
    
    /* Fixer spécifiquement la zone d'upload de fichier */
    [data-testid="stFileUploader"] section {
        background-color: rgba(30, 41, 59, 0.5) !important;
        border: 1px dashed rgba(255, 255, 255, 0.2) !important;
    }
    
    /* Forcer tout le texte du composant uploader en blanc (y compris les fichiers uploadés) */
    [data-testid="stFileUploader"] p, 
    [data-testid="stFileUploader"] span, 
    [data-testid="stFileUploader"] div,
    [data-testid="stFileUploader"] small {
        color: #f8fafc !important;
    }
    
    /* Fixer le bouton "Browse files" à l'intérieur de la zone d'upload */
    [data-testid="stFileUploader"] section button {
        background: linear-gradient(135deg, #06b6d4, #3b82f6) !important;
        color: white !important;
        border: none !important;
        font-weight: 600 !important;
    }
    
    [data-testid="stFileUploader"] section button * {
        color: white !important;
        background: transparent !important;
    }
    
    [data-testid="stFileUploader"] section button:hover {
        background: linear-gradient(135deg, #0891b2, #2563eb) !important;
    }
    
    /* Mettre en évidence les sélecteurs de couleur */
    [data-testid="stColorPicker"] {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.5) !important;
        border-radius: 8px;
        padding: 10px;
    }
    
    [data-testid="stColorPicker"] div[data-baseweb="block"],
    [data-testid="stColorPicker"] div[data-baseweb="input"] {
        border: 2px solid #f8fafc !important;
        border-radius: 6px !important;
    }
    
    /* Glassmorphism Containers */
    .stApp {
        background: radial-gradient(circle at top left, #1e293b, #0f172a);
    }
    
    div[data-testid="stVerticalBlock"] > div[style*="flex-direction: column;"] {
        background: rgba(30, 41, 59, 0.5);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
    }
    
    /* Custom Divider */
    hr {
        border: 0;
        height: 1px;
        background: linear-gradient(to right, rgba(6, 182, 212, 0), rgba(6, 182, 212, 0.5), rgba(6, 182, 212, 0));
        margin: 2rem 0;
    }
    
    /* Buttons */
    .stButton>button {
        width: 100%;
        border-radius: 12px;
        font-weight: 600;
        background: linear-gradient(135deg, #06b6d4, #3b82f6);
        color: white;
        border: none;
        height: 3.5em;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(6, 182, 212, 0.3);
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(6, 182, 212, 0.5);
        background: linear-gradient(135deg, #0891b2, #2563eb);
        color: white;
    }
    
    .stDownloadButton>button {
        background: linear-gradient(135deg, #8b5cf6, #d946ef) !important;
        box-shadow: 0 4px 15px rgba(139, 92, 246, 0.3) !important;
    }
    .stDownloadButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(139, 92, 246, 0.5) !important;
    }
    
    /* Headers */
    h1, h2, h3 {
        background: -webkit-linear-gradient(45deg, #06b6d4, #d946ef);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: rgba(15, 23, 42, 0.8);
        backdrop-filter: blur(20px);
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }
    </style>
    """, unsafe_allow_html=True)
# [ANCRE_FIN_STYLE_CSS]

# [ANCRE_DEBUT_LOGIQUE_METIER]
def get_shape_mask(shape_name, text_for_mask=""):
    size = (1000, 1000)
    img = Image.new("L", size, 255) 
    draw = ImageDraw.Draw(img)
    
    if shape_name == "Texte":
        text_to_draw = text_for_mask if text_for_mask else "ABC"
        font = None
        font_size = 900 
        
        font_paths = ["impact.ttf", "arialbd.ttf", "DejaVuSans-Bold.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"]
        
        for path in font_paths:
            try:
                temp_font = ImageFont.truetype(path, font_size)
                bbox = draw.textbbox((0, 0), text_to_draw, font=temp_font)
                w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
                
                while (w > size[0] - 40 or h > size[1] - 40) and font_size > 50:
                    font_size -= 10
                    temp_font = ImageFont.truetype(path, font_size)
                    bbox = draw.textbbox((0, 0), text_to_draw, font=temp_font)
                    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
                
                font = temp_font
                break
            except:
                continue
        
        if font is None:
            font = ImageFont.load_default()
            bbox = draw.textbbox((0, 0), text_to_draw, font=font)
            w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
            
        draw.text(((size[0]-w)/2, (size[1]-h)/2), text_to_draw, font=font, fill=0)
        
    elif shape_name == "Cercle":
        draw.ellipse([20, 20, 980, 980], fill=0)
    elif shape_name == "Carré":
        draw.rectangle([50, 50, 950, 950], fill=0)
    elif shape_name == "Cœur":
        draw.polygon([(500, 950), (20, 450), (150, 50), (500, 300), (850, 50), (980, 450)], fill=0)
    elif shape_name == "Étoile":
        draw.polygon([(500, 20), (625, 350), (980, 350), (720, 550), (820, 950), (500, 720), (180, 950), (280, 550), (20, 350), (375, 350)], fill=0)
    elif shape_name == "Bulle":
        draw.ellipse([50, 50, 950, 750], fill=0)
        draw.polygon([(250, 700), (100, 980), (450, 740)], fill=0)
    return np.array(img)
# [ANCRE_FIN_LOGIQUE_METIER]

# [ANCRE_DEBUT_SIDEBAR]
with st.sidebar:
    st.header("🎨 Réglages Visuels")
    shape_choice = st.selectbox("Forme du nuage", ["Rectangle", "Cercle", "Carré", "Cœur", "Étoile", "Bulle", "Texte", "Image personnalisée"])
    
    custom_mask = None
    if shape_choice == "Texte":
        mask_text = st.text_input("Mot(s) pour la forme :", "HELLO").upper()
        custom_mask = get_shape_mask("Texte", mask_text)
    elif shape_choice == "Image personnalisée":
        mask_file = st.file_uploader("Image (Noir sur blanc)", type=["png", "jpg", "jpeg"])
        if mask_file:
            custom_mask = np.array(Image.open(mask_file).convert("L"))
            custom_mask = np.where(custom_mask > 128, 255, 0)
    elif shape_choice != "Rectangle":
        custom_mask = get_shape_mask(shape_choice)

    max_w = st.slider("Nombre max de mots", 10, 500, 50)
    palette = st.selectbox("Palette de couleurs", ["viridis", "plasma", "magma", "coolwarm", "Spectral"])
    
    with st.expander("❓ Aide sur les palettes"):
        st.markdown("- **Viridis** : Pro (Violet-Jaune)\n- **Plasma** : Dynamique\n- **Magma** : Contrasté\n- **Coolwarm** : Équilibré\n- **Spectral** : Arc-en-ciel")
        
    st.markdown("---")
    st.markdown("### 🎨 Fond de l'image")
    st.info("💡 Choisissez la couleur de fond de votre nuage de mots. Elle sera appliquée à l'image finale téléchargée.")
    bg_col = st.color_picker("Couleur de fond", "#0f172a")
    st.markdown("---")
    
    st.subheader("📐 Options de bordures")
    use_border = st.checkbox("Afficher les bordures de la forme", value=False)
    
    if use_border:
        contour_w = st.slider("Épaisseur du contour", 1, 4, 1)
        contour_col = st.color_picker("Couleur du contour", "#06b6d4")
    else:
        contour_w = 0
        contour_col = bg_col

    st.header("🎞️ Paramètres Vidéo")
    fps = st.slider("Vitesse (FPS)", 5, 30, 8)
    pause_finale = st.slider("Pause finale (sec)", 1, 15, 5)
# [ANCRE_FIN_SIDEBAR]

# [ANCRE_DEBUT_DASHBOARD_PRINCIPAL]
st.title("☁️ Nuage de mots Premium")
st.markdown("Créez des visualisations textuelles époustouflantes en quelques clics.")

with st.container():
    uploaded_file = st.file_uploader("📂 Parcourir les fichiers (Excel .xlsx)", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    
    with st.container():
        target_column = st.selectbox("Sélectionnez la colonne à analyser :", df.columns)

    st.markdown("<hr/>", unsafe_allow_html=True)

    with st.container():
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

    st.markdown("<hr/>", unsafe_allow_html=True)

    FINAL_STOPWORDS = STOPWORDS.union(STOPWORDS_FR).union(st.session_state.manual_stopwords)
    text_list = df[target_column].dropna().astype(str).tolist()
    full_text = " ".join(text_list).lower()
    full_text = re.sub(r"\b[ldjns]['’]", " ", full_text)
    full_text = re.sub(r'[^\w\s]', ' ', full_text)

    with st.container():
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

    st.markdown("<hr/>", unsafe_allow_html=True)

    with st.container():
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1: btn_static = st.button("🚀 Générer Vue Fixe")
        with col_btn2: btn_video = st.button("🎬 Créer l'Animation")

        if btn_static:
            with st.spinner("Génération en cours..."):
                wc = WordCloud(background_color=bg_col, max_words=max_w, colormap=palette, 
                               width=1000, height=1000, mask=custom_mask, 
                               stopwords=FINAL_STOPWORDS, min_word_length=4,
                               repeat=True, contour_width=contour_w, contour_color=contour_col).generate(full_text)
                
                tab1, tab2 = st.tabs(["🖼️ Image Fixe", "📈 Graphique"])
                with tab1:
                    fig, ax = plt.subplots(figsize=(10, 10))
                    fig.patch.set_facecolor('#0f172a')
                    ax.imshow(wc, interpolation='bilinear')
                    ax.axis("off")
                    st.pyplot(fig)
                    buf = io.BytesIO()
                    fig.savefig(buf, format="png", bbox_inches='tight', pad_inches=0, facecolor='#0f172a')
                    st.download_button("📥 Télécharger PNG", buf.getvalue(), "nuage.png", "image/png")
                with tab2:
                    df_plot = pd.DataFrame(list(wc.words_.items()), columns=['Mot', 'Importance']).head(max_w)
                    fig_plot = px.bar(df_plot, x='Importance', y='Mot', orientation='h', color='Importance', color_continuous_scale=palette)
                    fig_plot.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#f8fafc')
                    st.plotly_chart(fig_plot)

        if btn_video:
            with st.spinner("🎬 Compilation vidéo... (cela peut prendre quelques instants)"):
                proc_tags = WordCloud(stopwords=FINAL_STOPWORDS, min_word_length=4).process_text(full_text)
                sorted_words = sorted(proc_tags.items(), key=lambda x: x[1], reverse=True)[:max_w]
                
                video_filename = "animation.mp4"
                frames = []
                words_to_show = []
                v_mask = custom_mask
                v_w, v_h = (1000, 1000) if v_mask is not None else (1280, 720)

                for word, _ in sorted_words:
                    words_to_show.append(word)
                    wc_frame = WordCloud(background_color=bg_col, max_words=max_w, colormap=palette, 
                                         width=v_w, height=v_h, mask=v_mask, 
                                         stopwords=FINAL_STOPWORDS, min_word_length=4,
                                         repeat=True, contour_width=contour_w, contour_color=contour_col).generate(" ".join(words_to_show))
                    frames.append(np.array(wc_frame.to_image()))
                
                for _ in range(fps * pause_finale): frames.append(frames[-1])
                imageio.mimsave(video_filename, frames, fps=fps, codec='libx264')
                
                with open(video_filename, "rb") as f:
                    v_bytes = f.read()
                st.video(v_bytes)
                st.download_button("📥 Télécharger la vidéo", v_bytes, "nuage_anime.mp4")
else:
    with st.container():
        st.info("👋 Bonjour ! Veuillez charger votre fichier Excel pour commencer.")
# [ANCRE_FIN_DASHBOARD_PRINCIPAL]
