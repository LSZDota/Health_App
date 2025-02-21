# general_health_tests.py
import streamlit as st
import json
from datetime import datetime
import os
import pandas as pd
import plotly.graph_objects as go


# Define the path to the data file
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(SCRIPT_DIR, 'saved_data', 'health_tests_data.json')

# Reference ranges and units
REFERENCE_RANGES = {
    "Hématies": (4.25, 5.79, "Tera/L"),
    "Hémoglobine": (13.4, 16.7, "g/dL"),
    "Hématocrite": (39.2, 48.6, "%"),
    "V.G.M.": (78.0, 97.0, "fl"),
    "T.C.M.H.": (26.3, 32.8, "pg"),
    "C.C.M.H.": (32.4, 36.3, "g/dL"),
    "Leucocytes": (4.05, 11.00, "Giga/L"),
    "Poly. neutrophiles": (1.78, 6.95, "Giga/L"),
    "Poly. éosinophiles": (0.05, 0.63, "Giga/L"),
    "Poly. basophiles": (None, 0.10, "Giga/L"),
    "Lymphocytes": (1.24, 3.92, "Giga/L"),
    "Monocytes": (0.23, 0.77, "Giga/L"),
    "Plaquettes": (161, 398, "Giga/L"),
    "Protéine C réactive": (None, 5, "mg/l"),
    "Sodium": (136, 145, "mmol/L"),
    "Potassium": (3.5, 5.1, "mmol/L"),
    "Albumine": (35, 50, "g/L"),
    "Calcium": (2.10, 2.55, "mmol/L"),
    "Calcium corrigé": (2.10, 2.55, "mmol/L"),
    "Créatinine": (64, 104, "μmol/L"),
    "DFG selon l'équation CKD-EPI": (60, None, "ml/mn/1.73m²"),
    "DFG selon l'équation MDRD": (60, None, "ml/mn/1.73m²"),
    "Transaminase ASAT (S.G.O.T)": (5, 34, "U/L"),
    "Transaminase ALAT (S.G.P.T)": (None, 55, "U/L"),
    "Phosphatases alcalines": (40, 150, "U/L"),
    "GGT(gamma-glutamyl-transférase)": (12, 64, "UI/L"),
    "Glycémie à jeun": (3.9, 6.1, "mmol/L"),
    "Cholestérol total": (None, 5.18, "mmol/L"),
    "Cholestérol H.D.L.": (1.04, None, "mmol/L"),
    "Cholestérol L.D.L.": (None, None, "mmol/L"),
    "Triglycérides": (None, 1.70, "mmol/L"),
    "Ferritine": (22, 275, "μg/L"),
    "25 OH VITAMINE D (D2/D3)": (30, 60, "ng/ml"),
    "Protéinurie": (None, 0.14, "g/L"),
    "Glycosurie": (None, 0.83, "mmol/L")
}

# List of test names
TEST_NAMES = list(REFERENCE_RANGES.keys())

# Function to load data
def load_health_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        return []

# Function to save data
def save_health_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def general_health_tests_app():
    st.title("Analyses Médicales Générales")

    # Load existing data
    data = load_health_data()

    # Option to add new test data
    st.header("Ajouter de Nouvelles Données de Test")

    # Step 1: Select date
    date = st.date_input("Date du Test", datetime.today())

    # Step 2: Select tests to enter
    selected_tests = st.multiselect("Sélectionnez les tests pour lesquels vous avez des résultats", TEST_NAMES)

    # Step 3: Enter test results
    if selected_tests:
        test_results = {}
        with st.form(key='health_test_form'):
            for test in selected_tests:
                min_val, max_val, unit = REFERENCE_RANGES[test]
                reference_str = ""
                if min_val is not None and max_val is not None:
                    reference_str = f"(Référence: {min_val} - {max_val} {unit})"
                elif min_val is None and max_val is not None:
                    reference_str = f"(Référence: Inférieur à {max_val} {unit})"
                elif min_val is not None and max_val is None:
                    reference_str = f"(Référence: Supérieur à {min_val} {unit})"

                value = st.number_input(f"{test} ({unit}) {reference_str}", value=0.0)
                test_results[test] = {
                    "value": value,
                    "unit": unit,
                    "reference_range": [min_val, max_val]
                }

            submitted = st.form_submit_button("Soumettre")

        if submitted:
            # Save the new test data
            test_entry = {
                "date": date.strftime('%Y-%m-%d'),
                "tests": test_results
            }
            data.append(test_entry)
            save_health_data(data)
            st.success("Les données du test ont été enregistrées!")

    # Option to view and plot data
    st.header("Afficher et Tracer les Données de Test")
    if data:
        # Convert data into a format suitable for plotting
        plot_health_data(data)
    else:
        st.info("Aucune donnée de test disponible. Veuillez ajouter de nouvelles données de test.")

def plot_health_data(data):
    # Convert data to DataFrame
    records = []
    for entry in data:
        record = {"date": entry["date"]}
        for test_name, test_info in entry["tests"].items():
            record[test_name] = test_info["value"]
        records.append(record)
    df = pd.DataFrame(records)
    df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
    df.sort_values('date', inplace=True)

    # Select tests to plot
    available_tests = [col for col in df.columns if col != 'date']
    selected_tests = st.multiselect("Sélectionnez les tests à tracer", available_tests)

    for test in selected_tests:
        fig = go.Figure()

        # Plot test values over time
        fig.add_trace(go.Scatter(
            x=df['date'], y=df[test],
            mode='lines+markers',
            name=test
        ))

        # Add reference range if available
        min_val, max_val, unit = REFERENCE_RANGES.get(test, (None, None, ""))
        y_min = df[test].min() - abs(df[test].min() * 0.1)
        y_max = df[test].max() + abs(df[test].max() * 0.1)

        # Handle None values in reference ranges
        shapes = []
        annotations = []
        if min_val is not None and max_val is not None:
            shapes.append(dict(
                type="rect",
                xref="x",
                yref="y",
                x0=df['date'].min(),
                y0=min_val,
                x1=df['date'].max(),
                y1=max_val,
                fillcolor="green",
                opacity=0.1,
                layer="below",
                line_width=0,
            ))
            annotations.append(dict(
                x=df['date'].mean(),
                y=max_val,
                xref="x",
                yref="y",
                text=f"Référence ({min_val} - {max_val} {unit})",
                showarrow=False,
                yshift=10,
                font=dict(color="black")
            ))
        elif min_val is None and max_val is not None:
            shapes.append(dict(
                type="rect",
                xref="x",
                yref="y",
                x0=df['date'].min(),
                y0=y_min,
                x1=df['date'].max(),
                y1=max_val,
                fillcolor="green",
                opacity=0.1,
                layer="below",
                line_width=0,
            ))
            annotations.append(dict(
                x=df['date'].mean(),
                y=max_val,
                xref="x",
                yref="y",
                text=f"Référence (Inférieur à {max_val} {unit})",
                showarrow=False,
                yshift=10,
                font=dict(color="black")
            ))
        elif min_val is not None and max_val is None:
            shapes.append(dict(
                type="rect",
                xref="x",
                yref="y",
                x0=df['date'].min(),
                y0=min_val,
                x1=df['date'].max(),
                y1=y_max,
                fillcolor="green",
                opacity=0.1,
                layer="below",
                line_width=0,
            ))
            annotations.append(dict(
                x=df['date'].mean(),
                y=min_val,
                xref="x",
                yref="y",
                text=f"Référence (Supérieur à {min_val} {unit})",
                showarrow=False,
                yshift=10,
                font=dict(color="black")
            ))

        # Update layout
        fig.update_layout(
            title=f"{test} au fil du temps",
            xaxis_title="Date",
            yaxis_title=f"{test} ({unit})",
            xaxis=dict(range=[df['date'].min(), df['date'].max()]),
            yaxis=dict(autorange=True),
            shapes=shapes,
            annotations=annotations
        )

        st.plotly_chart(fig, use_container_width=True)

