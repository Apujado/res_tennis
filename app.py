import streamlit as st
import json
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import threading

# Configuration de la page
st.set_page_config(page_title="Réservation Tennis Copropriété", layout="centered")

DB_FILE = "reservations.json"

# --- CHARGEMENT / SAUVEGARDE DES RÉSERVATIONS ---
def load_reservations():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}

def save_reservations(data):
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# --- FONCTION DE GÉNÉRATION DE REÇU TEXTE ---
def generer_recu_texte(user_id, date, creneau):
    timestamp = datetime.now().strftime("%d/%m/%Y à %H:%M:%S")
    id_unique = f"RESA-{datetime.now().strftime('%Y%m%d')}-{hash(user_id + date + creneau) % 10000:04d}"
    
    recu = f"""
==================================================
        REÇU OFFICIEL DE RÉSERVATION
             TENNIS COPROPRIÉTÉ
==================================================

🎟️ N° DE TICKET : {id_unique}
📅 Émis le : {timestamp}

--------------------------------------------------
👤 BÉNÉFICIAIRE :
   {user_id}

📅 DATE DU MATCH :
   {date}

⏰ CRÉNEAU HORAIRE :
   {creneau}
--------------------------------------------------

⚠️ En cas de litige sur le court, ce reçu fait foi.
   Bon match à vous !

==================================================
    """
    return recu, id_unique

# Chargement initial des bases
@st.cache_data
def load_copro_data():
    if os.path.exists('coproprietaires.json'):
        with open('coproprietaires.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

copro_data = load_copro_data()

if 'reservations' not in st.session_state:
    st.session_state.reservations = load_reservations()

st.title("🎾 Réservation du Court de Tennis")
st.write("Bienvenue sur la plateforme de réservation de la copropriété.")

# --- ESPACE CONNEXION ET VÉRIFICATION ---
st.subheader("👤 Vérification de votre profil")

if not copro_data:
    st.error("Le fichier 'coproprietaires.json' est introuvable. Veuillez d'abord exécuter convert.py.")
else:
    immeuble_saisi = st.text_input("Entrez le nom de votre Immeuble").strip()
    access_granted = False
    user_id = ""

    if immeuble_saisi:
        immeubles_existants = {k.lower(): k for k in copro_data.keys()}
        if len(immeuble_saisi) >= 3 and immeuble_saisi.lower() in immeubles_existants:
            vrai_nom_immeuble = immeubles_existants[immeuble_saisi.lower()]
            appart_saisi = st.text_input("Entrez votre numéro d'appartement").strip()
            
            if appart_saisi:
                liste_apparts = copro_data[vrai_nom_immeuble]
                if appart_saisi in liste_apparts:
                    user_id = f"{vrai_nom_immeuble} - Apt {appart_saisi}"
                    st.success(f"✅ Profil validé : Connecté en tant que **{user_id}**")
                    access_granted = True
                else:
                    st.error("❌ Numéro d'appartement inconnu pour cet immeuble. Accès bloqué.")
        else:
            st.error("❌ Cet immeuble ne fait pas partie de la copropriété. Accès bloqué.")

    if access_granted:
        st.write("---")
        st.subheader("📅 Choisir un créneau")
        
        date_resa = st.date_input("Date de réservation", min_value=datetime.today(), max_value=datetime.today() + timedelta(days=7))
        
        creneaux = [
            "08:00 - 08:50", "09:00 - 09:50", "10:00 - 10:50", "11:00 - 11:50",
            "12:00 - 12:50", "13:00 - 13:50", "14:00 - 14:50", "15:00 - 15:50",
            "16:00 - 16:50", "17:00 - 17:50", "18:00 - 18:50", "19:00 - 19:50",
            "20:00 - 20:50", "21:00 - 21:50"
        ]
        
        date_str = date_resa.strftime("%Y-%m-%d")
        if date_str not in st.session_state.reservations:
            st.session_state.reservations[date_str] = {}

        creneau_choisi = st.selectbox("Créneaux disponibles", creneaux)
        deja_reserve_par = st.session_state.reservations[date_str].get(creneau_choisi)

        if deja_reserve_par:
            if deja_reserve_par == user_id:
                st.warning("Vous avez réservé ce créneau.")
                
                # Proposer le téléchargement du reçu même après coup
                texte_recu, filename = generer_recu_texte(user_id, date_resa.strftime('%d/%m/%Y'), creneau_choisi)
                st.download_button(
                    label="📥 Télécharger à nouveau mon reçu",
                    data=texte_recu,
                    file_name=f"{filename}.txt",
                    mime="text/plain"
                )
                
                if st.button("❌ Annuler ma réservation"):
                    del st.session_state.reservations[date_str][creneau_choisi]
                    save_reservations(st.session_state.reservations)
                    st.rerun()
            else:
                st.error(f"Ce créneau est déjà réservé par : {deja_reserve_par}")
        else:
            if st.button("✅ Réserver ce créneau"):
                deja_un_creneau = any(res == user_id for res in st.session_state.reservations[date_str].values())
                
                if deja_un_creneau:
                    st.error("Règles : Vous avez déjà une réservation pour cette journée !")
                else:
                    # Enregistrement dans la base de données (Data Historique Copro)
                    st.session_state.reservations[date_str][creneau_choisi] = user_id
                    save_reservations(st.session_state.reservations)
                    
                    st.success("🎉 Réservation confirmée !")
                    
                    # Génération immédiate de la preuve
                    texte_recu, filename = generer_recu_texte(user_id, date_resa.strftime('%d/%m/%Y'), creneau_choisi)
                    
                    # Zone d'affichage visuel du reçu
                    st.code(texte_recu, language="text")
                    
                    # Bouton natif pour sauvegarder le fichier sur son téléphone/PC
                    st.download_button(
                        label="📥 Télécharger mon reçu officiel (Preuve)",
                        data=texte_recu,
                        file_name=f"{filename}.txt",
                        mime="text/plain"
                    )
                    st.balloons()

        st.write("---")
        st.subheader(f"📋 Planning du {date_resa.strftime('%d/%m/%Y')}")
        for c in creneaux:
            occupant = st.session_state.reservations[date_str].get(c, "🍃 Libre")
            st.write(f"**{c}** : {occupant}")
    else:
        st.write("---")
        st.info("💡 Veuillez entrer un immeuble et un numéro d'appartement valides pour débloquer le planning.")