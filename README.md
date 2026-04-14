# 🦺 Real-Time PPE Compliance Monitoring System (Multi-Model YOLOv11)

## 📌 Overview

This project implements a **real-time Personal Protective Equipment (PPE) compliance monitoring system** using a **modular multi-model deep learning architecture**.

Unlike traditional approaches that rely on a single model, this system uses **multiple specialized YOLOv11 models**, each trained independently for a specific PPE category (helmet, gloves, mask, etc.), and combines them at inference time to perform **accurate detection and compliance analysis**.

The system is deployed through an interactive **Streamlit dashboard** supporting real-time monitoring, multi-camera input, alerting, and historical analytics.

---

## 🚀 Key Features

* 🎯 **Multi-Model Architecture**

  * One YOLO model per PPE category
  * Independent training and optimization
  * Flexible and modular deployment

* 🎥 **Real-Time Detection**

  * Live webcam and IP camera support
  * Multi-camera monitoring

* 🧠 **Compliance Analysis**

  * Detects missing PPE per person
  * Generates real-time safety alerts

* 📊 **Data Logging & Analytics**

  * Automatic CSV logging of detections
  * Real-time charts and historical dashboards

* ⚙️ **Interactive UI**

  * Built with Streamlit
  * Dynamic PPE selection
  * Configurable monitoring periods

---

## 🧠 System Architecture

```
Camera Input
     ↓
Person Detection (YOLOv8)
     ↓
PPE Detection (Multiple YOLOv11 Models)
     ├── Helmet Model
     ├── Gloves Model
     ├── Mask Model
     ├── ...
     ↓
Aggregation & Matching
     ↓
Compliance Logic (Alert System)
     ↓
Dashboard + CSV Logging
```

---

## 🏗️ Project Structure

```
├── app/
│   └── streamlit_app.py      # User interface & real-time monitoring
│
├── src/
│   ├── model_manager.py      # Multi-model loading & inference
│   ├── detection.py          # Detection pipeline
│   ├── compliance.py         # PPE compliance logic
│   ├── data_logger.py        # CSV logging & data handling
│
├── models/                   # Trained YOLO models (.pt)
├── images/                   # Images used to design the app
├── resultats_csv/            # Output logs and metrics
               

```

---

## 🤖 Model Training

Each PPE category is trained **independently** using YOLOv11.

### Example: Helmet Detection Model

* Dataset: Custom dataset via Roboflow
* Classes:

  * Helmet
  * Helmet with strap
  * No helmet

### Training Configuration

* Epochs: 80
* Image size: 640
* Model: YOLOv11n

---

## 📊 Model Performance (Helmet Model)

| Metric                 | Value  |
| ---------------------- | ------ |
| Precision              | 0.986  |
| Recall                 | 0.991  |
| mAP@0.5                | 0.992  |
| mAP@0.5:0.95           | 0.733  |
| Accuracy (custom test) | 99.56% |

---

## ⚙️ Installation

```bash
git clone https://github.com/your-username/real-time-multi-model-ppe-detection-yolov11.git
cd real-time-multi-model-ppe-detection-yolov11

pip install -r requirements.txt
```

---

## ▶️ Usage

```bash
streamlit run app/streamlit_app.py
```

### Features available in the UI:

* Select PPE types to monitor
* Choose specific PPE subtypes
* Configure monitoring time window
* Add/remove cameras (USB or IP)
* View real-time alerts and dashboards

---

## 🚨 Compliance Logic

The system evaluates PPE compliance based on detected persons:

* If the number of detected PPE items is lower than the number of persons → ⚠️ alert is triggered
* Alerts are dynamically displayed in the dashboard

Example:

```
⚠️ ALERT: 2 persons without helmet
```

---

## 📈 Dashboard & Analytics

* Real-time visualization of PPE detection
* Historical data exploration by date
* Per-camera analytics
* Summary statistics (mean, max)

---

## 🔍 Technical Highlights

* Multi-model inference pipeline
* Real-time video processing with OpenCV
* Modular AI system design
* Integration of ML + business logic
* Lightweight deployment with Streamlit

---

## ⚠️ Limitations & Future Work

* No person–PPE association (IoU matching can be added)
* Performance can be optimized for edge devices



---

## 📌 Conclusion

This project demonstrates how modular deep learning models can be combined into a **real-time intelligent monitoring system**, bridging the gap between computer vision research and real-world industrial applications.

---

## 👩‍💻 Author

**Yosra Hammoudi**
Master’s Student in Data Science & Software Development

---

## ⭐ If you found this project useful

Give it a ⭐ on GitHub!
