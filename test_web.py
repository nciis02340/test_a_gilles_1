import streamlit as st
import fitz  # PyMuPDF
import pandas as pd
import io

st.set_page_config(page_title="Extracteur PDF Batch", page_icon="🗂️")

st.title("🗂️ Extracteur Multi-PDF vers Excel")
st.write("Glissez plusieurs formulaires PDF ici pour les regrouper dans un seul tableau.")

# 1. Autoriser la sélection de plusieurs fichiers
fichiers_uploades = st.file_uploader(
    "Choisir les formulaires PDF", 
    type="pdf", 
    accept_multiple_files=True  # L'option clé est ici
)

if fichiers_uploades:
    toutes_les_donnees = []
    
    st.info(f"Analyse de {len(fichiers_uploades)} fichiers en cours...")
    
    for fichier in fichiers_uploades:
        try:
            # Lire chaque PDF
            doc = fitz.open(stream=fichier.read(), filetype="pdf")
            donnees_du_fichier = {"Nom_Fichier": fichier.name} # On ajoute le nom du fichier pour s'y retrouver
            
            # Extraire les champs
            for page in doc:
                for widget in page.widgets():
                    donnees_du_fichier[widget.field_name] = widget.field_value
            
            toutes_les_donnees.append(donnees_du_fichier)
        except Exception as e:
            st.error(f"Erreur sur le fichier {fichier.name} : {e}")

    if toutes_les_donnees:
        # 2. Créer le DataFrame global
        df_final = pd.DataFrame(toutes_les_donnees)
        
        st.success("✅ Extraction terminée !")
        
        # Aperçu des 5 premières lignes
        st.subheader("Aperçu du regroupement")
        st.dataframe(df_final.head(10))
        
        # 3. Préparation du téléchargement Excel
        tampon_excel = io.BytesIO()
        with pd.ExcelWriter(tampon_excel, engine='openpyxl') as writer:
            df_final.to_excel(writer, index=False)
        
        st.download_button(
            label="📥 Télécharger le tableau récapitulatif (Excel)",
            data=tampon_excel.getvalue(),
            file_name="regroupement_formulaires.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
else:
    st.info("Sélectionnez un ou plusieurs fichiers PDF pour commencer.")

st.divider()
st.caption("Astuce : Vous pouvez sélectionner tout un dossier avec Ctrl+A dans la fenêtre de sélection.")