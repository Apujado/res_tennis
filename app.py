import streamlit as st
import json
import os
from datetime import datetime, timedelta

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
    
    # 📝 AJOUT : Signature DataPeakInsights dans le reçu officiel téléchargé
    recu = f"""
==================================================
        REÇU OFFICIEL DE RÉSERVATION
             TENNIS COPROPRIÉTÉ
==================================================

🎟️ N° DE TICKET : {id_unique}
📅 Émis le : {timestamp}
🚀 Solution propulsée par DataPeakInsights

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


# --- ✨ NOUVEAU : SIDEBAR PROFESSIONNELLE (VITRINE) ---
with st.sidebar:
    st.markdown("## 📊 DataPeakInsights")
    st.markdown(
        """
        <div style="background-color: #f0f2f6; padding: 15px; border-radius: 10px; border-left: 5px solid #1e4620; margin-bottom: 20px;">
            <p style="margin: 0; font-size: 0.95em; color: #2c3e50;">
                Cette application a été développée et offerte bénévolement à la copropriété par <strong>Aurélie Pujado</strong>.
            </p>
        </div>
        """, 
        unsafe_allow_html=True
    )
    st.subheader("💡 Une idée ? Un projet ?")
    st.write(
        "Spécialisée en ingénierie des données et création d'applications métiers sur-mesure, "
        "j'accompagne les entreprises dans la valorisation de leurs données."
    )
    
    # Boutons d'action call-to-action
    st.markdown(
        """
        [💼 Me contacter sur LinkedIn](https://www.linkedin.com/in/aureliepujado/)
        
        [💻 Voir le code sur GitHub](https://github.com/Apujado/res_tennis)
        """
    )
    st.write("---")
    st.caption("© 2026 DataPeakInsights. Tous droits réservés.")


# --- CONTENU PRINCIPAL ---
st.title("🎾 Réservation du Court de Tennis")
st.write("Bienvenue sur la plateforme de réservation de la copropriété.")

# --- ESPACE CONNEXION ET VÉRIFICATION ---
st.subheader("👤 Vérification de votre profil")

if not copro_data:
    st.error("Le fichier 'coproprietaires.json' est introuvable. Veuillez d'abord exécuter convert.py.")
else:
    immeuble_saisi = st.text_input("Entrez le nom de votre Immeuble", key="input_immeuble").strip()
    access_granted = False
    user_id = ""

    if immeuble_saisi:
        immeubles_existants = {k.lower(): k for k in copro_data.keys()}
        if len(immeuble_saisi) >= 3 and immeuble_saisi.lower() in immeubles_existants:
            vrai_nom_immeuble = immeubles_existants[immeuble_saisi.lower()]
            appart_saisi = st.text_input("Entrez votre numéro d'appartement", key="input_appart").strip()
            
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
                    mime="text/plain",
                    key="download_again"
                )
                
                if st.button("❌ Annuler ma réservation", key="btn_annuler"):
                    del st.session_state.reservations[date_str][creneau_choisi]
                    save_reservations(st.session_state.reservations)
                    st.rerun()
            else:
                st.error("Ce créneau est déjà réservé.")
        else:
            if st.button("✅ Réserver ce créneau", key="btn_reserver"):
                # On compte le nombre de réservations de cet appartement pour ce jour
                resas_de_la_journee = st.session_state.reservations[date_str].values()
                nb_resas_user = sum(1 for res in resas_de_la_journee if res == user_id)
                
                if nb_resas_user >= 2:
                    st.error("🚫 Règles : Vous avez atteint la limite maximale de 2 réservations pour cette journée !")
                else:
                    # Enregistrement dans le fichier JSON
                    st.session_state.reservations[date_str][creneau_choisi] = user_id
                    save_reservations(st.session_state.reservations)
                    
                    st.success("🎉 Réservation confirmée !")
                    st.balloons()
                    
                    # Génération immédiate de la preuve
                    texte_recu, filename = generer_recu_texte(user_id, date_resa.strftime('%d/%m/%Y'), creneau_choisi)
                    
                    # Zone d'affichage visuel du reçu
                    st.code(texte_recu, language="text")
                    
                    # Bouton natif pour sauvegarder le fichier sur son téléphone/PC
                    st.download_button(
                        label="📥 Télécharger mon reçu officiel (Preuve)",
                        data=texte_recu,
                        file_name=f"{filename}.txt",
                        mime="text/plain",
                        key="download_first"
                    )

        st.write("---")
        st.subheader(f"📋 Planning du {date_resa.strftime('%d/%m/%Y')}")
        for c in creneaux:
            occupant = st.session_state.reservations[date_str].get(c, "🍃 Libre")
            if occupant not in ("🍃 Libre", user_id):
                occupant = "🔒 Réservé"
            st.write(f"**{c}** : {occupant}")
    else:
        st.write("---")
        st.info("💡 Veuillez entrer un immeuble et un numéro d'appartement valides pour débloquer le planning.")
