import pandas as pd
import json

# 1. Charger ton fichier Excel
df = pd.read_excel('usp_appartements.xlsx')

# 2. Nettoyer les espaces vides au cas où
# /!\ Vérifie bien que tes colonnes s'appellent exactement 'Immeuble' et 'Appartement'
df['Immeuble'] = df['Immeuble'].astype(str).str.strip()
df['Appartement'] = df['Appartement'].astype(str).str.strip()

# 3. Grouper les appartements par immeuble
dictionnaire_copro = df.groupby('Immeuble')['Appartement'].apply(list).to_dict()

# 4. Sauvegarder au format JSON
with open('coproprietaires.json', 'w', encoding='utf-8') as f:
    json.dump(dictionnaire_copro, f, ensure_ascii=False, indent=2)

print("🎉 Fichier coproprietaires.json généré avec succès !")