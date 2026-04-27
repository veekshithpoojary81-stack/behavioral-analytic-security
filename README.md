# 🔐 Behavioral Analytics for Energy Security

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-FF4B4B.svg)](https://streamlit.io/)
[![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-1.3+-F7931E.svg)](https://scikit-learn.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A specialized cybersecurity analytics platform designed for the **Energy Sector**. This application leverages behavioral analytics and machine learning to detect suspicious login patterns, helping infrastructure operators identify potential credential compromises and insider threats.

---

## 🚀 Key Features

- **📊 Dynamic Dashboards**: Real-time visualization of login trends, geographic distributions, and risk heatmaps using Plotly.
- **🛡️ Multi-Layered Detection**:
    - **Rule-Based Engine**: Flags anomalies based on 5 customizable security rules (Time, Frequency, Device, etc.).
    - **ML-Powered Detection**: Utilizes **Isolation Forest** to identify subtle behavioral outliers that rules might miss.
- **📉 Risk Scoring System**: Categorizes events into Low, Medium, High, and Critical risk levels based on multiple behavioral indicators.
- **📁 Flexible Data Ingestion**: Upload custom CSV datasets or experiment with built-in sample data.
- **📄 Automated Reporting**: Generate and export comprehensive anomaly reports in CSV format for security audits.
- **🎨 Premium UI**: A sleek, dark-mode professional interface optimized for Security Operation Centers (SOC).

---

## 🛠️ Technology Stack

- **Core**: Python 3.9+
- **Web Framework**: Streamlit
- **Data Processing**: Pandas, NumPy
- **Machine Learning**: Scikit-Learn (Isolation Forest, PCA)
- **Visualization**: Plotly, Matplotlib, Seaborn
- **Styling**: Custom CSS & Streamlit Theming

---

## 📂 Project Structure

```text
behavioral_energy_security/
├── app.py              # Main application entry point
├── requirements.txt    # Project dependencies
├── src/                # Core logic modules
│   ├── data_loader.py  # File handling and validation
│   ├── preprocessing.py # Feature engineering & cleaning
│   ├── detector.py      # Rule-based & risk logic
│   ├── ml_model.py      # Isolation Forest implementation
│   ├── dashboard.py    # Plotly visualization functions
│   └── utils.py        # Helper functions & reporting
├── assets/             # Custom CSS and images
├── reports/            # Exported anomaly reports
└── sample_data/        # Default dataset for testing
```

---

## ⚙️ Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-repo/behavioral_energy_security.git
   cd behavioral_energy_security
   ```

2. **Create a virtual environment (optional but recommended)**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

---

## 🖥️ Usage

1. **Launch the application**:
   ```bash
   streamlit run app.py
   ```

2. **Analysis Workflow**:
   - **Upload**: Drag and drop your login logs (CSV) into the sidebar.
   - **Configure**: Adjust the "Failed attempts threshold" and toggle ML detection.
   - **Analyze**: Explore the **Behavioral Analysis** and **Dashboard** tabs to investigate flags.
   - **Export**: Navigate to the **Reports** tab to save high-risk findings.

---

## 🧠 Detection Logic

The system analyzes logins across five primary behavioral vectors:

1.  **Suspicious Time**: Flags logins occurring during non-standard hours (e.g., 3:00 AM).
2.  **Time Deviation**: Compares login time against the user's historical average.
3.  **Failed Attempts**: Monitors for brute-force patterns exceeding user-defined thresholds.
4.  **Frequency Spikes**: Detects sudden bursts of activity within short intervals.
5.  **Device Entropy**: Identifies logins from previously unknown or unauthorized devices.

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request or open an issue for feature requests.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👤 Author

**Cybersecurity Analytics Team**  
*Energy Sector Threat Intelligence Division*