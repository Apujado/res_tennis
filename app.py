import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime, timedelta, date
import os
import json

# Configuration de la page
st.set_page_config(page_title="Réservation Tennis Copropriété", layout="centered", page_icon="🎾")

# --- CONNEXION GOOGLE SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)

def load_reservations_df():
    try:
        df = conn.read(ttl=0)
        if df.empty or 'Date' not in df.columns:
            return pd.DataFrame(columns=["Date", "Créneau", "Logement"])
        return df.dropna(how="all")
    except Exception:
        return pd.DataFrame(columns=["Date", "Créneau", "Logement"])

def save_reservation_gsheet(date_str, creneau, user_id):
    df_current = load_reservations_df()
    new_row = pd.DataFrame([{"Date": str(date_str), "Créneau": str(creneau), "Logement": str(user_id)}])
    df_updated = pd.concat([df_current, new_row], ignore_index=True)
    conn.update(data=df_updated)

def delete_reservation_gsheet(date_str, creneau, user_id):
    df_current = load_reservations_df()
    df_updated = df_current[~((df_current['Date'] == str(date_str)) & 
                               (df_current['Créneau'] == str(creneau)) & 
                               (df_current['Logement'] == str(user_id)))]
    conn.update(data=df_updated)

# --- FONCTION AUXILIAIRE POUR VÉRIFIER SI UN CRÉNEAU EST TERMINÉ ---
def est_creneau_termine(date_str, creneau_str):
    try:
        # Extraire l'heure de fin du créneau (ex: "08:00 - 08:50" -> "08:50")
        heure_fin_str = creneau_str.split("-")[1].strip()
        dt_fin_creneau = datetime.strptime(f"{date_str} {heure_fin_str}", "%Y-%m-%d %H:%M")
        return datetime.now() > dt_fin_creneau
    except Exception:
        return False

# --- FONCTION DE GÉNÉRATION DE REÇU TEXTE ---
def generer_recu_texte(user_id, date_str_fr, creneau):
    timestamp = datetime.now().strftime("%d/%m/%Y à %H:%M:%S")
    id_unique = f"RESA-{datetime.now().strftime('%Y%m%d')}-{hash(user_id + date_str_fr + creneau) % 10000:04d}"
    
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
   {date_str_fr}

⏰ CRÉNEAU HORAIRE :
   {creneau}
--------------------------------------------------

⚠️ En cas de litige sur le court, ce reçu fait foi.
   Bon match à vous !

==================================================
    """
    return recu, id_unique

# Chargement de la liste des copropriétaires
@st.cache_data
def load_copro_data():
    if os.path.exists('coproprietaires.json'):
        with open('coproprietaires.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

copro_data = load_copro_data()

# --- SIDEBAR VITRINE ---
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
    st.markdown(
        """
        [💼 Me contacter sur LinkedIn](https://www.linkedin.com/in/aureliepujado/)
        
        [💻 Voir le code sur GitHub](https://github.com/Apujado/res_tennis)
        """
    )
    st.write("---")
    st.caption("© 2026 DataPeakInsights. Tous droits réservés.")

# --- EN-TÊTE ET TITRE PRINCIPAL ---
st.title("🎾 Réservation du Court de Tennis")
st.write("Bienvenue sur la plateforme de réservation de la copropriété.")

df_resas = load_reservations_df()

# --- VÉRIFICATION DU PROFIL ---
st.subheader("👤 Identification du logement")

if not copro_data:
    st.error("Le fichier 'coproprietaires.json' est introuvable.")
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
        
        # Limite stricte à 3 jours glissants
        date_aujourdhui = date.today()
        date_max = date_aujourdhui + timedelta(days=2)
        
        date_resa = st.date_input(
            "Date de réservation (ouverture à 3 jours glissants max)", 
            min_value=date_aujourdhui, 
            max_value=date_max
        )
        date_str = date_resa.strftime("%Y-%m-%d")

        creneaux = [
            "08:00 - 08:50", "09:00 - 09:50", "10:00 - 10:50", "11:00 - 11:50",
            "12:00 - 12:50", "13:00 - 13:50", "14:00 - 14:50", "15:00 - 15:50",
            "16:00 - 16:50", "17:00 - 17:50", "18:00 - 18:50", "19:00 - 19:50",
            "20:00 - 20:50", "21:00 - 21:50"
        ]

        creneau_choisi = st.selectbox("Créneaux disponibles", creneaux)
        
        resas_jour = df_resas[df_resas['Date'] == date_str] if not df_resas.empty else pd.DataFrame()
        match_creneau = resas_jour[resas_jour['Créneau'] == creneau_choisi] if not resas_jour.empty else pd.DataFrame()
        deja_reserve_par = match_creneau['Logement'].values[0] if not match_creneau.empty else None

        if deja_reserve_par:
            if deja_reserve_par == user_id:
                st.warning("Vous avez réservé ce créneau.")
                texte_recu, filename = generer_recu_texte(user_id, date_resa.strftime('%d/%m/%Y'), creneau_choisi)
                st.download_button(
                    label="📥 Télécharger à nouveau mon reçu",
                    data=texte_recu,
                    file_name=f"{filename}.txt",
                    mime="text/plain",
                    key="download_again"
                )
                if st.button("❌ Annuler ma réservation", key="btn_annuler"):
                    delete_reservation_gsheet(date_str, creneau_choisi, user_id)
                    st.success("Réservation annulée !")
                    st.rerun()
            else:
                st.error(f"Ce créneau est déjà réservé par : {deja_reserve_par}")
        else:
            if st.button("✅ Réserver ce créneau", key="btn_reserver"):
                # 1. Vérification du quota du jour (Max 2 résas le même jour)
                nb_resas_jour_user = len(resas_jour[resas_jour['Logement'] == user_id]) if not resas_jour.empty else 0
                
                # 2. Vérification des créneaux actifs non encore joués sur les jours suivants
                a_des_resas_futures = False
                if not df_resas.empty:
                    resas_user = df_resas[df_resas['Logement'] == user_id]
                    for _, row in resas_user.iterrows():
                        if row['Date'] > date_aujourdhui.strftime("%Y-%m-%d"):
                            a_des_resas_futures = True
                            break
                        elif row['Date'] == date_aujourdhui.strftime("%Y-%m-%d"):
                            if not est_creneau_termine(row['Date'], row['Créneau']):
                                # C'est un créneau aujourd'hui mais qui n'est pas encore fini
                                pass  # On autorise si c'est pour la même journée (dans la limite de 2)

                if nb_resas_jour_user >= 2:
                    st.error("🚫 Règle d'équité : Vous avez déjà 2 réservations enregistrées pour cette journée !")
                elif date_str > date_aujourdhui.strftime("%Y-%m-%d") and a_des_resas_futures:
                    st.error("🚫 Règle d'équité : Vous avez déjà un créneau à venir non terminé. Vous pourrez réserver sur les jours suivants une fois votre créneau actuel joué !")
                else:
                    save_reservation_gsheet(date_str, creneau_choisi, user_id)
                    st.success("🎉 Réservation confirmée et sauvegardée !")
                    st.balloons()
                    
                    texte_recu, filename = generer_recu_texte(user_id, date_resa.strftime('%d/%m/%Y'), creneau_choisi)
                    st.code(texte_recu, language="text")
                    
                    st.download_button(
                        label="📥 Télécharger mon reçu officiel (Preuve)",
                        data=texte_recu,
                        file_name=f"{filename}.txt",
                        mime="text/plain",
                        key="download_first"
                    )

        st.write("---")
        st.subheader(f"📋 Planning du {date_resa.strftime('%d/%m/%Y')}")
        dict_resas = dict(zip(resas_jour['Créneau'], resas_jour['Logement'])) if not resas_jour.empty else {}
        for c in creneaux:
            occupant = dict_resas.get(c, "🍃 Libre")
            st.write(f"**{c}** : {occupant}")
    else:
        st.write("---")
        st.info("💡 Veuillez entrer un immeuble et un numéro d'appartement valides pour débloquer le planning.")

# --- SECTION DISCRÈTE EN BAS DE PAGE : STATISTIQUES & REGISTRE ---
st.write("---")
with st.expander("📊 Consulter l'historique de fréquentation & les statistiques (Optionnel)"):
    if not df_resas.empty:
        col1, col2 = st.columns(2)
        col1.metric("Total réservations enregistrées", len(df_resas))
        col2.metric("Logements participants", df_resas['Logement'].nunique())
        
        st.write("#### 🏆 Logements les plus actifs")
        st.bar_chart(df_resas['Logement'].value_counts().head(10))
        
        st.write("#### ⏰ Créneaux les plus prisés")
        st.bar_chart(df_resas['Créneau'].value_counts())
        
        st.write("#### 🔍 Registre des réservations")
        st.dataframe(df_resas.sort_values(by="Date", ascending=False), use_container_width=True)
    else:
        st.info("Aucune donnée enregistrée pour le moment.")