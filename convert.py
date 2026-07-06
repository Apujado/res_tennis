import pandas as pd
import json

SOURCE_FILE = 'usp_appartements.xlsx'
OUTPUT_FILE = 'coproprietaires.json'


def apartment_sort_key(value):
    if value.isdigit():
        return (0, int(value))
    return (1, value.casefold())


# 1. Charger le fichier Excel
df = pd.read_excel(SOURCE_FILE)

# 2. Vérifier et nettoyer les colonnes attendues
required_columns = {'Immeuble', 'Appartement'}
missing_columns = required_columns - set(df.columns)
if missing_columns:
    raise ValueError(f"Colonnes manquantes dans {SOURCE_FILE} : {', '.join(sorted(missing_columns))}")

df['Immeuble'] = df['Immeuble'].astype(str).str.strip()
df['Appartement'] = df['Appartement'].astype(str).str.strip()

# 3. Signaler les valeurs suspectes
appartements_suspects = sorted({value for value in df['Appartement'] if ' ' in value})
if appartements_suspects:
    print(f"⚠️ Appartements à vérifier : {', '.join(appartements_suspects)}")

# 4. Grouper les appartements par immeuble en dédupliquant les valeurs
dictionnaire_copro = {}
for immeuble, appartements in df.groupby('Immeuble')['Appartement']:
    dictionnaire_copro[immeuble] = sorted(set(appartements), key=apartment_sort_key)

# 5. Sauvegarder au format JSON
with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    json.dump(dictionnaire_copro, f, ensure_ascii=False, indent=2)

print(f"🎉 Fichier {OUTPUT_FILE} généré avec succès !")
