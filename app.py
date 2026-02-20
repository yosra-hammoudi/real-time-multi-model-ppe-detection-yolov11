import patch_streamlit 
import os
import streamlit as st
import cv2
from ultralytics import YOLO
import time as systime
from datetime import datetime, time, date
import pandas as pd
import base64
import altair as alt
import csv

def base64_image(image_path):
    with open(image_path, "rb") as img_file:
        b64_string = base64.b64encode(img_file.read()).decode("utf-8")
    return b64_string

EPI_TYPES = [
    "casque-standard", "casque-avec-jugulaire",
    "gants-anti-chaleur", "gants-isolants-electriques", "gants-chimiques", "gants-anti-coupures",
    "harnais-complet",
    "avec-oreillette",
    "Lunettes-teintees", "Lunettes_a_branches",
    "masque_chantier", "masque_avec_filtres", "masque_cartouches"
]
all_epi_precise_types = EPI_TYPES.copy()

def initialize_csv_file(csv_path):
    header = [
        "datetime",
        "camera",
        "nb_personnes",
    ] + EPI_TYPES
    
    if not os.path.exists(csv_path) or os.path.getsize(csv_path) == 0:
        with open(csv_path, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=header)
            writer.writeheader()

def append_detection(csv_path, camera_id, nb_personnes, detections_dict, selected_epi_types):
    # Créer un dictionnaire avec toutes les colonnes EPI_TYPES
    row = {
        'datetime': datetime.now().isoformat(),
        'camera': camera_id+1,
        'nb_personnes': nb_personnes
    }
    
    # Pour chaque type d'EPI possible
    for epi_type in EPI_TYPES:
        # Si l'EPI n'est pas dans les sélectionnés, mettre -1
        if epi_type not in selected_epi_types:
            row[epi_type] = -1
        else:
            # Si l'EPI est sélectionné mais non détecté, mettre 0
            # Sinon mettre le nombre détecté
            row[epi_type] = detections_dict.get(epi_type, 0)

    with open(csv_path, mode='a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['datetime', 'camera', 'nb_personnes'] + EPI_TYPES)
        writer.writerow(row)

def get_daily_csv_path():
    os.makedirs("resultats_csv", exist_ok=True)
    date_str = datetime.now().strftime("%Y-%m-%d")
    return os.path.join("resultats_csv", f"detections_epi_{date_str}.csv")

def create_realtime_chart(df, camera_id):
    try:
        df_cam = df[df['camera'] == camera_id + 1]
        
        if df_cam.empty:
            return None
        
        # Convertir la colonne datetime si ce n'est pas déjà fait
        if not pd.api.types.is_datetime64_any_dtype(df_cam['datetime']):
            df_cam['datetime'] = pd.to_datetime(df_cam['datetime'])
        
        melted_df = df_cam.melt(id_vars=['datetime', 'camera', 'nb_personnes'], 
                              value_vars=[epi for epi in EPI_TYPES if epi in df_cam.columns], 
                              var_name='EPI', 
                              value_name='count')
        
        # Ne garder que les EPI sélectionnés (count != -1) et détectés (count > 0)
        melted_df = melted_df[(melted_df['count'] > 0)]
        
        if melted_df.empty:
            return None
        
        chart = alt.Chart(melted_df).mark_line().encode(
            x=alt.X('datetime:T', title='Heure'),
            y=alt.Y('sum(count):Q', title='Nombre total détecté'),
            color=alt.Color('EPI:N', legend=alt.Legend(title="Type d'EPI")),
            tooltip=['EPI', 'sum(count)']
        ).properties(
            width=800,
            height=300,
            title=f"Détection d'EPI - Caméra {camera_id + 1}"
        ).interactive()
        
        return chart
    
    except Exception as e:
        st.error(f"Erreur lors de la création du graphique : {e}")
        return None

def check_epi_compliance(nb_persons, epi_counts, required_epis):
    alerts = []
    if nb_persons >= 1:  # Seuil minimal de personnes pour déclencher les vérifications
        for epi in required_epis:
            epi_count = epi_counts.get(epi, 0)
            # On déclenche une alerte si le nombre d'EPI détectés est inférieur au nombre de personnes - 1
            if epi_count < (nb_persons - 1):
                epi_name = epi.replace("-", " ").capitalize()
                missing_count = nb_persons - epi_count
                alerts.append(f"{missing_count} personne(s) sans {epi_name}")
    
    if alerts:
        return "⚠️ ALERTE : " + " | ".join(alerts)
    return None

# Configuration de la page
st.set_page_config(page_title="Surveillance EPI - Chantier", layout="wide")
st.markdown("""
<style>
html, body, [class^="css"] {
    zoom: 90%;
    background-color: #F7F9FB;
}
h1 {
    color: #1F77B4;
    font-weight: 900;
    font-size: 2.3rem;
    text-align: center;
    margin-bottom: 1rem;
    text-shadow: 1px 1px 3px rgba(31, 119, 180, 0.2);
}
h2 {
    color: #264653;
    font-weight: 700;
    font-size: 1.4rem;
    margin-top: 0.8rem;
    margin-bottom: 0.6rem;
}
h3 {
    color: #5C7893;
    font-weight: 600;
    font-size: 1.15rem;
    margin-top: 0.5rem;
    margin-bottom: 0.4rem;
}
[data-testid="stSidebar"] {
    background-color: #D6F3FF;
    color: #2F4858;
    padding: 1rem;
    border-radius: 0 0 10px 0;
}
[data-testid="stSidebar"] h2, 
[data-testid="stSidebar"] h3, 
[data-testid="stSidebar"] p, 
[data-testid="stSidebar"] label {
    color: #2F4858;
}
button {
    background-color: #3DB2FF !important;
    color: white !important;
    border: none !important;
    padding: 10px 0 !important;
    min-width: 140px !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    cursor: pointer !important;
    box-shadow: 0 3px 6px rgba(61, 178, 255, 0.3) !important;
    transition: background-color 0.3s ease !important;
    margin: 10px auto !important;
    display: block !important;
}
button:hover {
    background-color: #45D3F4 !important;
    box-shadow: 0 5px 12px rgba(69, 211, 244, 0.4) !important;
}
div[data-baseweb="checkbox"] label,
div[role="listbox"] {
    font-weight: 600;
    font-size: 0.95rem;
    color: #33658A !important;
}
div.stMarkdown, figcaption {
    font-size: 1rem;
    font-weight: 600;
    color: #2F4858 !important;
}
.stAlert, .stChart {
    margin-top: 0.5rem;
    margin-bottom: 1.5rem;
    border-radius: 8px;
    padding: 0.5rem;
    background-color: white;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
[data-testid="stVerticalBlock"] > div:has(> h3) {
    margin-top: 1.5rem !important;
    padding-top: 1rem !important;
    border-top: 1px solid #e1e4e8;
}
.dynamic-alert {
    background-color: #FFF3F3;
    border-left: 4px solid #FF4B4B;
    padding: 1rem;
    margin: 1rem 0;
    border-radius: 4px;
    animation: pulse 2s infinite;
}
@keyframes pulse {
    0% { box-shadow: 0 0 0 0 rgba(255, 75, 75, 0.4); }
    70% { box-shadow: 0 0 0 10px rgba(255, 75, 75, 0); }
    100% { box-shadow: 0 0 0 0 rgba(255, 75, 75, 0); }
}
</style>
""", unsafe_allow_html=True)

# Titre principal
st.markdown("<h1>Surveillance EPI - Chantier</h1>", unsafe_allow_html=True)

# Placeholder pour les alertes globales
global_alert_placeholder = st.empty()

# Chargement des modèles disponibles
model_options = {
    "Casque": "models/casque-best.pt",
    "Gants": "models/gants-best.pt",
    "Harnais": "models/harnais-best.pt",
    "Lunettes": "models/lunettes-best.pt",
    "Masque": "models/masque-best.pt",
    "Oreillette": "models/oreillette-best.pt"
}

epi_types = {
    "Casque": ["casque-standard", "casque-avec-jugulaire"],
    "Gants": ["gants-anti-chaleur", "gants-isolants-electriques", "gants-chimiques", "gants-anti-coupures"],
    "Harnais": ["harnais-complet"],
    "Oreillette": ["avec-oreillette"],
    "Lunettes": ["Lunettes-teintees", "Lunettes_a_branches"],
    "Masque": ["masque_chantier", "masque_avec_filtres", "masque_cartouches"]
}

image_epi = {
    "casque-standard": "images/casque-standard.jpg",
    "casque-avec-jugulaire": "images/casque-jugulaire.jpg",
    "gants-anti-chaleur": "images/chaleur.jpg",
    "gants-isolants-electriques": "images/electrique.jpg",
    "gants-chimiques": "images/chimiques.jpg",
    "gants-anti-coupures": "images/coupure.jpg",
    "harnais-complet": "images/harnais.jpg",
    "avec-oreillette": "images/oreillette.jpg",
    "Lunettes-teintees": "images\lunettes-téintées.jpg",
    "Lunettes_a_branches": "images/lunettes.jpg",
    "masque_chantier": "images/masque-chantier.jpg",
    "masque_avec_filtres": "images/masque-filtres.jpg",
    "masque_cartouches": "images/masque-cartouches.jpg"
}

# États initiaux
if "camera_count" not in st.session_state:
    st.session_state.camera_count = 1
if "detection_active" not in st.session_state:
    st.session_state.detection_active = {}
if "epi_selection" not in st.session_state:
    st.session_state.epi_selection = {}
if "current_alert" not in st.session_state:
    st.session_state.current_alert = None
# Initialisation des états pour les dashboards
for cam_id in range(st.session_state.camera_count):
    if f"show_dashboard_{cam_id}" not in st.session_state:
        st.session_state[f"show_dashboard_{cam_id}"] = False
    if f"dashboard_data_{cam_id}" not in st.session_state:
        st.session_state[f"dashboard_data_{cam_id}"] = None
# GESTION DES CAMÉRAS
st.sidebar.header("🎥 Caméras")

# Nouvelle section pour le type de caméra
st.sidebar.subheader("🔧 Configuration des caméras")
camera_type = st.sidebar.radio("Type de caméra", 
                             ["Locale (USB)", "IP (Téléphone)"],
                             key="camera_type")

camera_configs = []
for cam_id in range(st.session_state.camera_count):
    config = {"type": camera_type}
    
    if camera_type == "IP (Téléphone)":
        config["ip"] = st.sidebar.text_input(
            f"URL Caméra {cam_id+1}", 
            value="http://192.168.1.X:8080/video",
            key=f"cam_{cam_id}_ip"
        )
        config["auth"] = st.sidebar.checkbox(f"Authentification requise {cam_id+1}")
        if config["auth"]:
            config["username"] = st.sidebar.text_input(f"Utilisateur {cam_id+1}", key=f"cam_{cam_id}_user")
            config["password"] = st.sidebar.text_input(f"Mot de passe {cam_id+1}", type="password", key=f"cam_{cam_id}_pass")
    
    camera_configs.append(config)

col1, col2 = st.sidebar.columns(2)
with col1:
    if st.button("➕ Ajouter "):
        st.session_state.camera_count += 1
with col2:
    if st.button("➖ Supprimer ") and st.session_state.camera_count > 1:
        st.session_state.camera_count -= 1
# CONTROLES CAMERAS ET DASHBOARDS (version corrigée)
st.sidebar.markdown("---")
st.sidebar.subheader(" Contrôles caméras")

for cam_id in range(st.session_state.camera_count):
    st.sidebar.markdown(f"**Caméra {cam_id + 1}**")
    col_start, col_stop = st.sidebar.columns(2)
    with col_start:
        if st.button(f"▶️ Démarrer", key=f"start_{cam_id}"):
            st.session_state.detection_active[cam_id] = True
    with col_stop:
        if st.button(f"⏹️ Arrêter", key=f"stop_{cam_id}"):
            st.session_state.detection_active[cam_id] = False
    
    col_show, col_hide = st.sidebar.columns(2)
    with col_show:
        if st.button(f"📊 Afficher", key=f"show_dash_{cam_id}"):
            st.session_state[f"show_dashboard_{cam_id}"] = True
    with col_hide:
        if st.button(f"❌ Masquer", key=f"hide_dash_{cam_id}"):
            st.session_state[f"show_dashboard_{cam_id}"] = False
# PÉRIODE DE CONTRÔLE
st.sidebar.markdown("---")
st.sidebar.subheader("⏱️ Période de contrôle")
date_debut = st.sidebar.date_input("Date de début", value=date.today())
heure_debut = st.sidebar.time_input("Heure de début", value=time(8, 0))
date_fin = st.sidebar.date_input("Date de fin", value=date.today())
heure_fin = st.sidebar.time_input("Heure de fin", value=time(18, 0))
periode_debut = datetime.combine(date_debut, heure_debut)
periode_fin = datetime.combine(date_fin, heure_fin)



# MAIN CONTENT
col_video, col_epi = st.columns([2, 1])

with col_epi:
    st.markdown(f"<h3>Sélection des EPI à détecter</h3>", unsafe_allow_html=True)
    selected_epis = []
    selected_types = {}
    for epi in model_options:
        if st.checkbox(epi, key=f"{epi}_global"):
            selected_epis.append(epi)
            type_selected = st.selectbox(
                f"Type de {epi.lower()} à compter :",
                epi_types[epi],
                key=f"{epi}_type_global"
            )
            selected_types[epi] = type_selected
            if type_selected in image_epi:
                st.image(image_epi[type_selected], caption=type_selected.replace("-", " ").capitalize(), width=150)

# Charger une fois le modèle personne
person_model = YOLO("yolov8n.pt")

# Charger une fois les modèles EPI sélectionnés
loaded_epi_models = {}
for epi in selected_epis:
    model_path = model_options[epi]
    if os.path.exists(model_path):
        loaded_epi_models[epi] = YOLO(model_path)
    else:
        st.warning(f"Modèle non trouvé pour {epi} : {model_path}")

# HISTORIQUE DES DASHBOARDS
st.sidebar.markdown("---")
st.sidebar.subheader("📅 Historique des dashboards")

# Utiliser un expander pour forcer l'affichage correct
with st.sidebar.expander("Sélection de date", expanded=True):
    date_historique = st.date_input("Choisir une date", value=date.today(), key="hist_date")

if st.sidebar.button("Afficher le dashboard historique"):
    # Chemin du fichier CSV pour la date sélectionnée
    csv_historique = os.path.join("resultats_csv", f"detections_epi_{date_historique.strftime('%Y-%m-%d')}.csv")
    
    if os.path.exists(csv_historique):
        try:
            df_historique = pd.read_csv(csv_historique)
            
            # Créer un onglet par caméra
            tabs = st.tabs([f"Caméra {i+1}" for i in range(st.session_state.camera_count)])
            
            for cam_id, tab in enumerate(tabs):
                with tab:
                    st.markdown(f"### Dashboard historique - Caméra {cam_id+1} - {date_historique.strftime('%d/%m/%Y')}")
                    
                    # Filtrer les données pour cette caméra
                    df_cam = df_historique[df_historique['camera'] == cam_id+1]
                    
                    if not df_cam.empty:
                        # Graphique principal
                        chart = create_realtime_chart(df_cam, cam_id)
                        if chart:
                            st.altair_chart(chart, use_container_width=True)
                        
                        # Statistiques récapitulatives
                        st.markdown("#### Statistiques récapitulatives")
                        stats = df_cam[EPI_TYPES].describe().loc[['mean', 'max']]
                        st.dataframe(stats.style.format("{:.1f}"))
                        
                        # Alertes synthétiques
                        st.markdown("#### Alertes synthétiques")
                        for epi in EPI_TYPES:
                            if epi in df_cam.columns and (df_cam[epi] == 0).any():
                                st.warning(f"EPI manquant détecté: {epi.replace('-', ' ')}")
                    else:
                        st.warning(f"Aucune donnée disponible pour la caméra {cam_id+1}")
        except Exception as e:
            st.error(f"Erreur lors du chargement des données historiques: {str(e)}")
    else:
        st.warning("Aucun fichier de données trouvé pour cette date")

# Initialize CSV file
os.makedirs("resultats_csv", exist_ok=True)
csv_path = get_daily_csv_path()
initialize_csv_file(csv_path)

# Boucle principale de détection
for cam_id in range(st.session_state.camera_count):
    if st.session_state.detection_active.get(cam_id, False):
        results_data = []
        
        # Configuration de la capture vidéo selon le type
        if camera_configs[cam_id]["type"] == "Locale (USB)":
            cap = cv2.VideoCapture(cam_id)
        else:
            ip_config = camera_configs[cam_id]
            if ip_config.get("auth", False):
                url = f"http://{ip_config['username']}:{ip_config['password']}@{ip_config['ip'].replace('http://', '').replace('https://', '').split('/video')[0]}/video"
            else:
                url = ip_config["ip"]
            cap = cv2.VideoCapture(url)
            
            # Test de connexion
            if not cap.isOpened():
                st.error(f"Échec de connexion à la caméra IP {cam_id+1}")
                # Tentative de reconnexion avec URL alternative
                cap = cv2.VideoCapture(url.replace("/video", ""))
                
        if not cap.isOpened():
            st.warning(f"Impossible d'accéder à la caméra {cam_id+1}")
            st.session_state.detection_active[cam_id] = False
            continue

        with col_video:
            count_persons_placeholder = st.empty()
            epi_summary_placeholders = {epi: st.empty() for epi in selected_epis}
            frame_slot = st.empty()
            chart_placeholder = st.empty()

        matched_count = {epi: 0 for epi in selected_epis}
        frame_counter = 0
        start_timestamp = systime.time()
        results_data = []
        colors = {
            "Casque": (255, 255, 0),
            "Gants": (255, 0, 0),
            "Harnais": (0, 0, 255),
            "Lunettes": (255, 0, 255),
            "Masque": (0, 255, 255),
            "Oreillette": (255, 165, 0)
        }
        epi_mapping = {selected_types[epi]: epi for epi in selected_epis}
        
        while st.session_state.detection_active.get(cam_id, False):
            current_dt = datetime.now()
            if current_dt > periode_fin:
                st.info("⏹️ Fin de la période de contrôle atteinte.")
                st.session_state.detection_active[cam_id] = False
                break

            ret, frame = cap.read()
            if not ret:
                st.warning(f"Échec de capture sur la caméra {cam_id}")
                break

            # Détection personnes
            results_person = person_model(frame)[0]
            person_class_idx = None
            for idx, name in results_person.names.items():
                if name == "person":
                    person_class_idx = idx
                    break

            nb_persons = 0
            if person_class_idx is not None:
                nb_persons = sum(1 for cls_id in results_person.boxes.cls if int(cls_id) == person_class_idx)

            # Détection EPI
            matched_frame_count = {epi: 0 for epi in selected_epis}
            frame_display = frame.copy()

            # Collecter toutes les boîtes de détection
            all_boxes = []
            all_labels = []
            all_confidences = []

            for epi in selected_epis:
                model = loaded_epi_models.get(epi)
                if model:
                    results_epi = model(frame)[0]
                    for box, cls_id, conf in zip(results_epi.boxes.xyxy, results_epi.boxes.cls, results_epi.boxes.conf):
                        cls_idx = int(cls_id)
                        cls_name = results_epi.names[cls_idx].lower().replace(" ", "-")
                        target_type = selected_types[epi].lower().replace(" ", "-")
                        if cls_name == target_type:
                            matched_frame_count[epi] += 1
                            all_boxes.append(box.cpu().numpy())
                            all_labels.append(f"{epi}: {cls_name} ({conf:.2f})")
                            all_confidences.append(conf.cpu().numpy())

            # Vérification de la conformité EPI avec seuil de 1
            required_epis = [selected_types[epi] for epi in selected_epis]
            epi_counts = {selected_types[epi]: matched_frame_count[epi] for epi in selected_epis}
            alert_message = check_epi_compliance(nb_persons, epi_counts, required_epis)

            # Gestion dynamique de l'alerte
            if alert_message:
                if st.session_state.current_alert != alert_message:
                    st.session_state.current_alert = alert_message
                    with global_alert_placeholder:
                        st.markdown(f'<div class="dynamic-alert">{alert_message}</div>', unsafe_allow_html=True)
            else:
                if st.session_state.current_alert is not None:
                    st.session_state.current_alert = None
                    global_alert_placeholder.empty()

            # Annoter toutes les détections sur la frame
            for box, label in zip(all_boxes, all_labels):
                x1, y1, x2, y2 = map(int, box)
                cv2.rectangle(frame_display, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame_display, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            frame_counter += 1
            for epi in selected_epis:
                matched_count[epi] += matched_frame_count[epi]

            # Construction du dictionnaire de la ligne de résultats
            detections_to_log = {epi_type: 0 for epi_type in EPI_TYPES}
            for epi in selected_epis:
                detected_type = selected_types[epi]
                detections_to_log[detected_type] = matched_frame_count[epi]

            # Récupérer les types d'EPI sélectionnés
            selected_epi_types = [selected_types[epi] for epi in selected_epis]

            # Enregistrement dans le CSV
            append_detection(csv_path, cam_id, nb_persons, detections_to_log, selected_epi_types)

            # Mise à jour toutes les secondes
            now = systime.time()
            if now - start_timestamp >= 1.0:
                avg_persons = nb_persons
                with count_persons_placeholder:
                    st.markdown(f"👥 **Personnes détectées : {avg_persons}**")

                for epi in selected_epis:
                    avg_epi = matched_count[epi] // frame_counter if frame_counter > 0 else 0
                    type_epi = selected_types[epi]
                    image_path = image_epi.get(type_epi)
                    if image_path:
                        with epi_summary_placeholders[epi]:
                            b64_img = base64_image(image_path)
                            html = f"""
                            <div style="display: flex; align-items: center;">
                                <img src="data:image/png;base64,{b64_img}" width="40" style="margin-right: 8px;" />
                                <span style="font-weight: bold;">{type_epi.replace('-', ' ').capitalize()} : {avg_epi}</span>
                            </div>
                            """
                            st.markdown(html, unsafe_allow_html=True)

                matched_count = {epi: 0 for epi in selected_epis}
                frame_counter = 0
                start_timestamp = now

            # Afficher la frame avec toutes les annotations
            frame_rgb = cv2.cvtColor(frame_display, cv2.COLOR_BGR2RGB)
            with col_video:
                frame_slot.image(frame_rgb, channels="RGB", use_container_width=True)

            # Gestion spéciale pour les caméras IP
            if camera_configs[cam_id]["type"] == "IP (Téléphone)":
                # Réduire le délai entre les frames pour les caméras IP
                systime.sleep(0.1)
            else:
                systime.sleep(0.03)
            
            # Mise à jour du graphique en temps réel
            if st.session_state[f"show_dashboard_{cam_id}"]:
                try:
                    if os.path.exists(csv_path):
                        st.session_state[f"dashboard_data_{cam_id}"] = pd.read_csv(csv_path)
                        chart = create_realtime_chart(st.session_state[f"dashboard_data_{cam_id}"], cam_id)
                        if chart:
                            with chart_placeholder:
                                st.altair_chart(chart, use_container_width=True)
                        else:
                            chart_placeholder.warning("Aucune donnée de détection disponible")
                    else:
                        chart_placeholder.warning("Fichier de données introuvable")
                except Exception as e:
                    chart_placeholder.error(f"Erreur : {str(e)}")
            elif not st.session_state.detection_active.get(cam_id, False):
                if st.session_state[f"dashboard_data_{cam_id}"] is not None:
                    chart = create_realtime_chart(st.session_state[f"dashboard_data_{cam_id}"], cam_id)
                    if chart:
                        with chart_placeholder:
                            st.altair_chart(chart, use_container_width=True)
            else:
                chart_placeholder.empty()
                
        cap.release()