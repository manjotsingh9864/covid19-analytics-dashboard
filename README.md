# COVID-19 Global Impact Analysis

![Dashboard Version](https://img.shields.io/badge/version-5.0-blue)
![Python](https://img.shields.io/badge/python-3.8%2B-brightgreen)
![Streamlit](https://img.shields.io/badge/streamlit-1.24.0-red)
![Last Update](https://img.shields.io/badge/last%20updated-June%202025-yellow)

## 🌐 Overview

An interactive, data-driven dashboard for analyzing and visualizing the global impact of COVID-19. This project leverages WHO datasets to provide comprehensive insights into the pandemic's spread, regional patterns, mortality rates, and temporal trends.

[Streamlit Cloud Website](https://covid-19-global-analysis.streamlit.app/)

## Features

- **Dual Dataset Support**: Seamlessly switch between daily and weekly COVID-19 data for different analysis granularity
- **Interactive Global Map**: Animated timeline showing the spread of COVID-19 across countries
- **Country Comparison**: Deep-dive analysis of top affected countries with customizable metrics
- **Trend Analysis**: Temporal trends with moving averages for better pattern recognition
- **Regional Breakdown**: WHO regional insights with hierarchical visualizations
- **Mortality Analysis**: Track mortality rates over time across different regions
- **Data Export**: Download analyzed data in CSV, Excel, or JSON formats
- **Theme Support**: Full light/dark mode compatibility with Streamlit's theme system
- **Responsive Design**: Optimized for both desktop and mobile viewing

## Dashboard Sections

1. **Animated Map**: Visual representation of the global spread over time
2. **Top Countries**: Analysis of most affected countries with comparative metrics
3. **Trends**: Time-series analysis with customizable view options
4. **Regional Analysis**: WHO region breakdowns with interactive visualizations
5. **Interactive Explorer**: Compare selected countries across multiple dimensions
6. **Data Table**: Detailed data view with export capabilities

## Getting Started

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Installation

1. Clone the repository:
```bash
git clone https://github.com/AdilShamim8/COVID-19_Global_Impact_Analysis.git
cd COVID-19_Global_Impact_Analysis
```

2. Create a virtual environment (optional but recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

### Data Files

Ensure you have the following dataset files in the project directory:
- `WHO-COVID-19-global-data.csv` - Weekly data from WHO
- `WHO-COVID-19-global-daily-data.csv` - Daily data from WHO

### Running the Dashboard

```bash
streamlit run app.py
```

The dashboard will open in your default web browser at `http://localhost:8501`.

## 📈 Usage Guide

- **Dataset Selection**: Choose between daily or weekly data in the sidebar
- **Date Range**: Filter analysis by specific time periods
- **Geographic Filters**: Focus on specific WHO regions or countries
- **View Options**: Toggle between cumulative data, daily new cases, or weekly trends
- **Visualization Settings**: Adjust log scale, trend lines, and other display options
- **Data Export**: Download filtered and analyzed data in various formats

## Advanced Features

- **Interactive Charts**: Hover for detailed information, zoom, and pan capabilities
- **Customizable Displays**: Adjust map style, animation speed, and color themes
- **Performance Optimization**: Efficient data handling for smooth experience even with large datasets
- **Error Handling**: Robust handling of missing or inconsistent data
- **Responsive Design**: Optimized for various screen sizes and devices

## Project Structure

```
COVID-19_Global_Impact_Analysis/
├── app.py               # Main Streamlit application
├── requirements.txt     # Python dependencies
├── assets/             # Images and static assets
├── data/               # Data directory (for WHO datasets)
└── README.md           # Project documentation
```

## Data Sources

This dashboard uses official COVID-19 data from the World Health Organization (WHO), which includes:

- Confirmed cases (daily and cumulative)
- Deaths (daily and cumulative)
- Country and regional classifications
- Temporal data from the start of the pandemic

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Author

**Adil Shamim** - [@AdilShamim8](https://github.com/AdilShamim8)

## Acknowledgments

- World Health Organization for providing the COVID-19 datasets
- Streamlit team for the amazing framework
- Plotly for the interactive visualization capabilities
