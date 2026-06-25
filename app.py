import streamlit as st
import pandas as pd
import zipfile
import io

st.set_page_config(page_title="Découpage Hebdomadaire", layout="centered")

st.title("📅 Découpeur de Données Hebdomadaire (Multi-fichiers)")
st.write("Uploadez un ou plusieurs fichiers CSV. L'application va les fusionner, puis les découper en fichiers hebdomadaires (du lundi au dimanche) regroupés dans un seul fichier ZIP.")

# Le paramètre accept_multiple_files=True permet d'uploader plusieurs fichiers
uploaded_files = st.file_uploader("Uploadez vos fichiers CSV", type=["csv"], accept_multiple_files=True)

if uploaded_files: # Si la liste des fichiers n'est pas vide
    try:
        with st.spinner("Lecture et fusion des fichiers en cours..."):
            # 1. Lire et combiner tous les fichiers CSV uploadés
            dataframes = []
            for file in uploaded_files:
                df_temp = pd.read_csv(file)
                dataframes.append(df_temp)
            
            # Fusionner toutes les données en un seul DataFrame
            df = pd.concat(dataframes, ignore_index=True)
        
        st.write("### Aperçu des données fusionnées")
        st.dataframe(df.head())
        st.write(f"**Total des lignes combinées :** {len(df)}")
        
        # 2. Identifier la colonne de date
        date_col = 'order day'
        
        if date_col not in df.columns:
            st.error(f"Erreur : Impossible de trouver la colonne '{date_col}' dans les fichiers uploadés. Veuillez vérifier vos CSV.")
        else:
            with st.spinner("Découpage des données par semaine..."):
                # Convertir la colonne 'order day' en objets datetime
                df[date_col] = pd.to_datetime(df[date_col])
                
                # Obtenir le numéro de semaine ISO (du Lundi au Dimanche) et l'année
                df['Week_Number'] = df[date_col].dt.isocalendar().week
                df['Year'] = df[date_col].dt.isocalendar().year
                
                # Grouper les données par Année et par Numéro de Semaine
                grouped = df.groupby(['Year', 'Week_Number'])
                
                # 3. Créer un buffer ZIP en mémoire
                zip_buffer = io.BytesIO()
                
                with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                    for (year, week), group in grouped:
                        # Supprimer les colonnes temporaires avant l'export
                        clean_group = group.drop(columns=['Week_Number', 'Year'])
                        
                        # Convertir le dataframe de la semaine en format CSV en mémoire
                        csv_data = clean_group.to_csv(index=False)
                        
                        # Créer le nom du fichier : "data week x_année.csv"
                        file_name = f"data week {week}_{year}.csv"
                        
                        # Écrire les données CSV dans le fichier ZIP
                        zip_file.writestr(file_name, csv_data)
                
                st.success("✅ Données fusionnées et découpées par semaine avec succès !")
                
                # 4. Bouton de téléchargement en 1 clic
                st.download_button(
                    label="📥 Télécharger toutes les semaines (ZIP)",
                    data=zip_buffer.getvalue(),
                    file_name="donnees_hebdomadaires.zip",
                    mime="application/zip",
                    use_container_width=True
                )
                
    except Exception as e:
        st.error(f"Une erreur s'est produite lors du traitement des fichiers : {e}")
