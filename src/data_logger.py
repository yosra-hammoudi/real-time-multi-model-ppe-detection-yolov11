import os
import csv
from datetime import datetime

EPI_TYPES = [
    "casque-standard", "casque-avec-jugulaire",
    "gants-anti-chaleur", "gants-isolants-electriques", "gants-chimiques", "gants-anti-coupures",
    "harnais-complet",
    "avec-oreillette",
    "Lunettes-teintees", "Lunettes_a_branches",
    "masque_chantier", "masque_avec_filtres", "masque_cartouches"
]

def get_daily_csv_path():
    os.makedirs("resultats_csv", exist_ok=True)
    date_str = datetime.now().strftime("%Y-%m-%d")
    return os.path.join("resultats_csv", f"detections_epi_{date_str}.csv")


def initialize_csv_file(csv_path):
    header = ["datetime", "camera", "nb_personnes"] + EPI_TYPES
    
    if not os.path.exists(csv_path) or os.path.getsize(csv_path) == 0:
        with open(csv_path, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=header)
            writer.writeheader()


def append_detection(csv_path, camera_id, nb_personnes, detections_dict, selected_epi_types):
    row = {
        'datetime': datetime.now().isoformat(),
        'camera': camera_id + 1,
        'nb_personnes': nb_personnes
    }

    for epi_type in EPI_TYPES:
        if epi_type not in selected_epi_types:
            row[epi_type] = -1
        else:
            row[epi_type] = detections_dict.get(epi_type, 0)

    with open(csv_path, mode='a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['datetime', 'camera', 'nb_personnes'] + EPI_TYPES)
        writer.writerow(row)