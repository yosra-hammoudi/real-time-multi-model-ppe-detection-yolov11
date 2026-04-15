from ultralytics import YOLO

class PPEModelManager:
    def __init__(self, model_paths, person_model_path=None):
        self.models = {}

        # charger modèles EPI
        for name, path in model_paths.items():
            try:
                self.models[name] = YOLO(path)
            except Exception as e:
                print(f"Erreur chargement modèle {name}: {e}")

        # charger modèle personne (IMPORTANT)
        self.person_model = None
        if person_model_path:
            try:
                self.person_model = YOLO(person_model_path)
            except Exception as e:
                print(f"Erreur chargement modèle person: {e}")

    def get_person_model(self):
        return self.person_model

    def detect(self, frame, selected_epis):
        results = {}

        for epi in selected_epis:
            model = self.models.get(epi)
            if model:
                results[epi] = model(frame)[0]

        return results