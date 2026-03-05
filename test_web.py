import streamlit as st
import fitz  # PyMuPDF
import pandas as pd
import io
import re # Le module pour la recherche de texte

st.set_page_config(page_title="Extracteur PDF Intelligent", page_icon="🧠")

st.title("🧠 Extracteur PDF (Formulaires & Texte)")
st.write("Cet outil extrait les données des champs éditables ET du texte brut (si pas de formulaire).")

# --- CONFIGURATION ---
CHAMPS_A_GARDER = ["serial number", "customer", "location", "date de reception"]

def extraire_via_regex(texte, mot_cle):
    """Cherche un mot clé dans le texte et récupère ce qui suit (sur la même ligne)"""
    # Cette regex cherche le mot clé, accepte ":" ou "=" optionnels, puis capture le reste de la ligne
    pattern = rf"{mot_cle}[:\s=]*(.*)"
    match = re.search(pattern, texte, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return None

fichiers_uploades = st.file_uploader("Choisir les PDF", type="pdf", accept_multiple_files=True)

if fichiers_uploades:
    toutes_les_donnees = []
    
    for fichier in fichiers_uploades:
        try:
            doc = fitz.open(stream=fichier.read(), filetype="pdf")
            infos = {"Nom_Fichier": fichier.name}
            
            # --- ÉTAPE 1 : Tentative via les widgets (Formulaire) ---
            champs_trouves_form = 0
            for page in doc:
                for widget in page.widgets():
                    if widget.field_name.lower() in [c.lower() for c in CHAMPS_A_GARDER]:
                        infos[widget.field_name] = widget.field_value
                        champs_trouves_form += 1

            # --- ÉTAPE 2 : Si champs vides, tentative via Texte Brut ---
            # On récupère tout le texte du PDF une seule fois
            texte_complet = "\n".join([page.get_text() for page in doc])
            
            for champ in CHAMPS_A_GARDER:
                # Si le champ n'a pas été trouvé par le formulaire, on le cherche dans le texte
                if champ not in infos or not infos[champ]:
                    valeur_detectee = extraire_via_regex(texte_complet, champ)
                    if valeur_detectee:
                        infos[champ] = valeur_detectee

            toutes_les_donnees.append(infos)
            
        except Exception as e:
            st.error(f"Erreur sur {fichier.name} : {e}")

    if toutes_les_donnees:
        df = pd.DataFrame(toutes_les_donnees)
        st.success("Analyse terminée.")
        st.dataframe(df)
        
        tampon = io.BytesIO()
        with pd.ExcelWriter(tampon, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
        
        st.download_button("📥 Télécharger l'Excel", tampon.getvalue(), "extraction_mixte.xlsx")