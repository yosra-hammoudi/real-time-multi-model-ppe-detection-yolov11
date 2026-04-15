import cv2

def detect_persons(frame, person_model):
    results = person_model(frame)[0]

    person_class_idx = None
    for idx, name in results.names.items():
        if name == "person":
            person_class_idx = idx
            break

    nb_persons = 0
    if person_class_idx is not None:
        nb_persons = sum(1 for cls_id in results.boxes.cls if int(cls_id) == person_class_idx)

    return nb_persons, results


def detect_epi(frame, model_manager, selected_epis, selected_types):
    matched_counts = {epi: 0 for epi in selected_epis}
    all_boxes = []
    all_labels = []

    results = model_manager.detect(frame, selected_epis)

    for epi in selected_epis:
        res = results.get(epi)
        if not res:
            continue

        for box, cls_id, conf in zip(res.boxes.xyxy, res.boxes.cls, res.boxes.conf):
            cls_idx = int(cls_id)
            cls_name = res.names[cls_idx].lower().replace(" ", "-")
            target_type = selected_types[epi].lower().replace(" ", "-")

            if cls_name == target_type:
                matched_counts[epi] += 1
                all_boxes.append(box.cpu().numpy())
                all_labels.append(f"{epi}: {cls_name} ({conf:.2f})")

    return matched_counts, all_boxes, all_labels


def draw_detections(frame, boxes, labels):
    frame_display = frame.copy()

    for box, label in zip(boxes, labels):
        x1, y1, x2, y2 = map(int, box)
        cv2.rectangle(frame_display, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(frame_display, label, (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    return frame_display
def process_frame(frame, model_manager, selected_epis, selected_types):
    # 1. détecter personnes
    person_model = model_manager.get_person_model()  # si tu l’as
    nb_persons, _ = detect_persons(frame, person_model)

    # 2. détecter EPI
    matched_counts, boxes, labels = detect_epi(
        frame,
        model_manager,
        selected_epis,
        selected_types
    )

    # 3. draw
    frame_out = draw_detections(frame, boxes, labels)

    return {
        "nb_persons": nb_persons,
        "detections": matched_counts,
        "frame": frame_out
    }