# 🦠 COVID-19 Analytics Dashboard by Manjot Singh

[![Python](https://img.shields.io/badge/Python-3.13-blue?logo=python&logoColor=white)](https://www.python.org/) 
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30-orange?logo=streamlit&logoColor=white)](https://streamlit.io/) 
[![GitHub](https://img.shields.io/badge/GitHub-Repo-black?logo=github&logoColor=white)](https://github.com/manjotsingh9864/covid19-analytics-dashboard)

---

## 🌐 Project Overview

The **COVID-19 Analytics Dashboard** is an **interactive, modern, and visually appealing web application** providing comprehensive global insights into COVID-19 cases, deaths, recoveries, and vaccination trends. Built with **Python, Streamlit, and Plotly**, it enables users to explore **daily, weekly, and cumulative data** with **advanced visualizations, AI-powered forecasting, and downloadable reports**.  

This project is ideal for **data analysis, visualization, and portfolio showcase** in data science.

---

## 🎯 Key Features

### **1. Interactive KPIs**
- Wide rectangular cards displaying:
  - Affected Countries
  - Total Cases
  - Total Deaths
  - New Weekly/Daily Cases
  - Mortality Rate
- Modern pastel gradient styling and hover effects.

### **2. Animated Global Map**
- Time-lapse bubble map of COVID-19 spread.
- Custom pastel color scales.
- Logarithmic scaling support for better visualization.

### **3. Top Countries Analysis**
- Bar charts for top countries by cases and deaths.
- Scatter plots showing case-death relationships and mortality rates.

### **4. Global Trends**
- Line and area charts for cumulative, daily, and weekly metrics.
- Moving averages for smoother trends.
- Interactive hover tooltips and dual-axis charts.

### **5. Regional Analysis**
- Pie charts, treemaps, and area charts by WHO region.
- Mortality rates per region displayed.
- Fallback horizontal bar charts for incomplete data.

### **6. Interactive Country Explorer**
- Compare multiple countries over time.
- Radar charts for normalized multi-metric comparisons.
- Pastel color palette for readability.

### **7. Forecasting (AI Predictions)**
- 14-day forecasts using **Prophet** (ARIMA fallback).
- Confidence intervals included.
- Multi-country selection with performance optimization.

### **8. Data Table & Export**
- Interactive tables using **st_aggrid**.
- Filtered analytics exportable in **CSV, Excel, JSON, or PDF**.
- PDF includes key metrics, charts, and author info.

### **9. Modern Dashboard Design**
- Light, pastel, and visually appealing theme.
- Animated logo in sidebar.
- Hover effects and interactive KPI cards.
- Smooth animations for charts and maps.

---

## 🛠️ Technologies Used

- **Python 3.13**
- **Streamlit**: Web app interface
- **Plotly**: Interactive visualizations
- **Pandas & NumPy**: Data manipulation
- **Prophet**: Forecasting (optional)
- **ARIMA**: Fallback forecasting
- **st_aggrid**: Interactive tables
- **ReportLab**: PDF report generation
- **Seaborn & Matplotlib**: Optional visualization support

---

## ⚡ Installation & Setup

### **Clone the repository**
```bash
git clone https://github.com/manjotsingh9864/covid19-analytics-dashboard.git
cd covid19-analytics-dashboard
```

### **Create virtual environment (optional)**
```bash
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows
```

### **Install dependencies**
```bash
pip install -r requirements.txt
```

### **Run the app**
```bash
streamlit run app.py
```

---

## 💡 Usage

- Select dataset type: **Daily or Weekly**.
- Filter by **date range, WHO region, or countries**.
- Explore **interactive charts**: maps, bar charts, line plots, radar charts.
- Forecast trends using **Prophet/ARIMA**.
- Export filtered analytics in **CSV, Excel, JSON, PDF** formats.

---

## 🚀 Deployment

Deploy for free using **[Streamlit Community Cloud](https://share.streamlit.io/)**:

1. Push your project to GitHub.
2. Sign in to Streamlit Cloud and connect the repo.
3. Select branch `main` and file `app.py`.
4. Click **Deploy** to get a live URL.

---

## 📈 Future Enhancements

- Multi-variate regression for vaccination vs mortality.
- Rolling average trend lines.
- Optimize map animations for large datasets.
- Dark/light toggle option for UI.
- Multi-metric forecasting for multiple countries simultaneously.

---

## 👨‍💻 Author

**Manjot Singh**  
Email: singhtmanjot@gmail.com | Phone: +91 7087736640  
[LinkedIn](https://www.linkedin.com/in/manjot-singh-ds/)

---

## 📄 License

This project is for **portfolio and educational purposes**. Code reuse is allowed with proper credit.
