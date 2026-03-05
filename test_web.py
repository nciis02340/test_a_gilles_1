import streamlit as st
import fitz  # PyMuPDF
import pandas as pd
import io

# Configuration de la page
st.set_page_config(page_title="Extracteur PDF Formulaire", page_icon="📄")

st.title("📄 Extracteur de Formulaire PDF")
st.write("Chargez un PDF rempli pour transformer ses données en fichier Excel.")

# 1. Zone de chargement du fichier
fichier_uploade = st.file_uploader("Choisir un formulaire PDF", type="pdf")

if fichier_uploade:
    try:
        # Lecture du PDF depuis la mémoire du serveur
        doc = fitz.open(stream=fichier_uploade.read(), filetype="pdf")
        
        donnees_extraites = {}
        
        # 2. Extraction des données des champs (widgets)
        for page in doc:
            widgets = page.widgets()
            for widget in widgets:
                nom_du_champ = widget.field_name
                valeur = widget.field_value
                # On nettoie un peu si c'est du texte
                if isinstance(valeur, str):
                    valeur = valeur.strip()
                donnees_extraites[nom_du_champ] = valeur
        
        if donnees_extraites:
            st.success(f"✅ {len(donnees_extraites)} champs détectés !")
            
            # 3. Création du tableau de données (DataFrame)
            df = pd.DataFrame([donnees_extraites])
            
            # Affichage de l'aperçu
            st.subheader("Aperçu des données")
            st.dataframe(df)
            
            # 4. Préparation du fichier Excel en mémoire (BytesIO)
            # Indispensable pour le Cloud car on n'écrit pas sur le disque dur du serveur
            tampon_excel = io.BytesIO()
            with pd.ExcelWriter(tampon_excel, engine='openpyxl') as writer:
                df.to_excel(writer, index=False)
            
            # 5. Bouton de téléchargement vers ton PC
            st.download_button(
                label="📥 Télécharger les données en Excel",
                data=tampon_excel.getvalue(),
                file_name=f"extraction_{fichier_uploade.name}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
        else:
            st.warning("⚠️ Aucun champ de formulaire (nommé) n'a été trouvé dans ce PDF.")
            st.info("Note : Si c'est un scan sans champs interactifs, ce script ne pourra pas 'lire' le texte visuel.")

    except Exception as e:
        st.error(f"Une erreur est survenue lors de la lecture : {e}")

else:
    st.info("En attente d'un fichier PDF...")

# Petit pied de page
st.divider()
st.caption("Outil d'automatisation personnel - Propulsé par Streamlit & PyMuPDF")