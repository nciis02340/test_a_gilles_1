import streamlit as st
import fitz  # PyMuPDF
import pandas as pd
import io

st.set_page_config(page_title="Aspirateur de texte PDF", page_icon="🧹")

st.title("🧹 Aspirateur de texte intégral")
st.write("Cet outil extrait TOUT le texte lisible de vos PDF vers un seul fichier Excel.")

fichiers_uploades = st.file_uploader("Choisir les PDF", type="pdf", accept_multiple_files=True)

if fichiers_uploades:
    toutes_les_donnees = []
    
    for fichier in fichiers_uploades:
        try:
            # 1. Ouverture du PDF
            doc = fitz.open(stream=fichier.read(), filetype="pdf")
            
            # 2. Extraction de tout le texte de toutes les pages
            texte_integral = ""
            for page in doc:
                texte_integral += page.get_text() + "\n" # On ajoute un saut de ligne entre chaque page
            
            # 3. Nettoyage rapide (enlever les espaces inutiles en début/fin)
            texte_integral = texte_integral.strip()
            
            if texte_integral:
                toutes_les_donnees.append({
                    "Nom_Fichier": fichier.name,
                    "Nombre_Pages": len(doc),
                    "Texte_Extrait": texte_integral
                })
            else:
                # Si le texte est vide, c'est probablement une image (scan)
                toutes_les_donnees.append({
                    "Nom_Fichier": fichier.name,
                    "Nombre_Pages": len(doc),
                    "Texte_Extrait": "[AUCUN TEXTE DÉTECTÉ - Ce fichier est peut-être un scan/image]"
                })
                
        except Exception as e:
            st.error(f"Erreur sur {fichier.name} : {e}")

    if toutes_les_donnees:
        df = pd.DataFrame(toutes_les_donnees)
        
        st.success(f"Extraction terminée pour {len(toutes_les_donnees)} fichiers.")
        
        # Aperçu (on coupe le texte pour que l'affichage reste propre)
        st.subheader("Aperçu de l'extraction")
        st.dataframe(df)
        
        # Préparation Excel
        tampon = io.BytesIO()
        with pd.ExcelWriter(tampon, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
        
        st.download_button(
            label="📥 Télécharger tout le texte en Excel",
            data=tampon.getvalue(),
            file_name="extraction_integrale_texte.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )