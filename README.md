# 🎾 RésaTennis - Gestion des Réservations Estivales

Une application web légère et intuitive conçue pour simplifier la gestion et la réservation du terrain de tennis de la copropriété durant la période estivale.

## 🚀 Fonctionnalités
* **Réservation en temps réel :** Bloquez vos créneaux facilement depuis votre smartphone ou ordinateur.
* **Anti-conflit :** Système intelligent pour éviter les doubles réservations.
* **Suivi transparent :** Visualisation claire des disponibilités pour tous les résidents.

## 📱 Accéder à l'application
L'application est déployée et accessible en ligne ici :  
👉 **https://restennis-9svx4sgawlfu7u9afym8qt.streamlit.app/**

---

## 🛠️ Installation & Développement (Local)

Si vous souhaitez faire tourner le projet en local ou y contribuer :

### Prérequis
* [Python 3.10+](https://www.python.org/downloads/)

### Lancement
```bash
# Cloner le projet
git clone https://github.com/[VotrePseudo]/res_tennis.git
cd res_tennis

# Installer les dépendances
pip install -r requirements.txt

# Lancer l'application Streamlit
streamlit run app.py
```

### Générer les données copropriétaires

Si vous disposez du fichier source `usp_appartements.xlsx`, vous pouvez régénérer `coproprietaires.json` avec :

```bash
python convert.py
```

Le fichier Excel doit contenir les colonnes `Immeuble` et `Appartement`.
