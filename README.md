# visualization_project

# 🌍 War on the Plate – Visualization Project

**Analyzing Israel's Vulnerability to Food Shortages Controlled by Global Market Leaders**

This interactive data visualization dashboard, built with Python and Dash, allows users to explore global food production and export patterns — with a specific focus on Israel’s food imports and self-sufficiency. It combines data from world food production, Israeli trade statistics, and national consumption needs to present a comprehensive picture of global food dependency.

---

## 📊 Key Features

- 🌐 **Global Choropleth Map**  
  Visualizes worldwide food production and highlights countries that export specific food items to Israel. Users can toggle between different display modes for clarity (borders, color-coded data, or both).

- 📈 **Line Chart**  
  Displays production trends for selected food items in a specific country over time. If Israel is selected, the chart also compares production against estimated consumption needs.

- 🔥 **Heatmap Visualization**  
  Shows the top food-producing countries for a specific item over the years, giving users insight into global production trends.

- 🎛️ **Interactive Controls**  
  Select food items, countries, years, and number of top countries to display. A year slider and animation (Play/Pause) allow for dynamic exploration.

---

## 🗂️ Dataset Sources

- `world food production.csv` – FAO-based food production data (1989–2020)
- `trade_israel.csv` – Israel’s export/import data
- `israel_need.csv` – Estimated food consumption needs in Israel by product

---

## 🚀 Getting Started

### 📦 Prerequisites

Ensure you have **Python 3.7+** installed. You’ll also need the following packages:

```bash
pip install pandas plotly dash
