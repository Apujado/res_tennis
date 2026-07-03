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