# main_app.py
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
import json
import matplotlib.pyplot as plt
from datetime import datetime
import os
import subprocess
import requests  # Add this import for making API requests
import general_health_tests  # Make sure to create this file as per step 2
import withings_smartwatch_app  # You'll create this module


# Define the paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TOKENS_FILE_PATH = os.path.join(SCRIPT_DIR, 'saved_data', 'withings_tokens.json')
WEIGHT_DATA_FILE_PATH = os.path.join(SCRIPT_DIR, 'saved_data', 'weight_data.json')


# Load Weight Data
def load_weight_data():
    try:
        with open(WEIGHT_DATA_FILE_PATH, 'r') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        st.error("Data file not found. Please fetch data first.")
        return []
    

# Plotting Weight Data
def plot_weight_measurements(measure_type, measure_name):
    data = load_weight_data()
    if not data:
        return

    dates = []
    values = []

    for entry in data:
        for measure in entry['measures']:
            if measure['type'] == measure_type:
                date = datetime.utcfromtimestamp(entry['date'])
                value = measure['value'] * (10 ** measure['unit'])
                dates.append(date)
                values.append(value)

    if dates:
        dates, values = zip(*sorted(zip(dates, values)))

        # Create Plotly figure
        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=dates, y=values,
            mode='lines+markers',
            name=measure_name
        ))

        fig.update_layout(
            title=f'{measure_name} Over Time',
            xaxis_title='Date',
            yaxis_title=measure_name,
            xaxis=dict(range=[dates[0], dates[-1]]),
            yaxis=dict(autorange=True),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )

        # Render the Plotly figure in Streamlit
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.write("No data available to plot.")

# Fetch Measurements from Withings API
def fetch_measurements(access_token, measure_type):
    url = 'https://wbsapi.withings.net/measure'
    params = {
        'action': 'getmeas',
        'access_token': access_token,
        'meastypes': measure_type,
        'category': 1
    }
    response = requests.get(url, params=params)
    response_json = response.json()
    if response_json.get('status') == 0:
        data = response_json['body']['measuregrps']
        # Save the data to a JSON file
        with open(WEIGHT_DATA_FILE_PATH, 'w') as f:
            json.dump(data, f)
        return True
    else:
        st.error(f"Error fetching measurements: {response_json.get('error')}")
        return False   

# Load Heart Rate Data
def load_heart_rate_data():
    try:
        with open('saved_data/heart_rate_data.json', 'r') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        st.error("Heart rate data file not found.")
        return None

# Save Heart Rate Data
def save_heart_rate_data(data):
    with open('saved_data/heart_rate_data.json', 'w') as f:
        json.dump(data, f, indent=4)

# Plot Heart Rate Data
def plot_heart_rate_data(selected_plots):
    data = load_heart_rate_data()
    if not data:
        st.write("No heart rate data available to plot.")
        return

    dates = []
    systolic = []
    diastolic = []
    pulse = []

    for date_str, values in data['data'].items():
        dates.append(datetime.strptime(date_str, '%Y-%m-%d'))
        systolic.append(values[0])
        diastolic.append(values[1])
        pulse.append(values[2])

    # Sort the data by dates
    dates, systolic, diastolic, pulse = zip(*sorted(zip(dates, systolic, diastolic, pulse)))

    # Create Plotly figure
    fig = go.Figure()

    if 'Systolic' in selected_plots:
        fig.add_trace(go.Scatter(
            x=dates, y=systolic,
            mode='lines+markers',
            name='Systolic'
        ))
    if 'Diastolic' in selected_plots:
        fig.add_trace(go.Scatter(
            x=dates, y=diastolic,
            mode='lines+markers',
            name='Diastolic'
        ))
    if 'Pulse' in selected_plots:
        fig.add_trace(go.Scatter(
            x=dates, y=pulse,
            mode='lines+markers',
            name='Pulse'
        ))

    # Add background shading for drug levels
    t1 = datetime(2024, 5, 29)
    t2 = datetime(2024, 8, 23)

    # Get data range
    data_start = dates[0]
    data_end = dates[-1]

    # Define the shapes for shading
    shapes = []
    annotations = []

    y_min = min(min(systolic), min(diastolic), min(pulse))
    y_max = max(max(systolic), max(diastolic), max(pulse))
    y_range = [y_min - 5, y_max + 5]  # Add some padding

    # Region 1: Before t1, dosage 300 mg
    if data_start <= t1:
        shapes.append(dict(
            type="rect",
            xref="x",
            yref="paper",
            x0=data_start,
            y0=0,
            x1=min(t1, data_end),
            y1=1,
            fillcolor="lightblue",
            opacity=0.3,
            layer="below",
            line_width=0,
        ))
        annotations.append(dict(
            x=data_start + (min(t1, data_end) - data_start) / 2,
            y=y_max,
            xref="x",
            yref="y",
            text="300 mg",
            showarrow=False,
            yshift=10,
            font=dict(color="black")
        ))

    # Region 2: Between t1 and t2, dosage 150 mg
    if data_start <= t2 and data_end >= t1:
        shapes.append(dict(
            type="rect",
            xref="x",
            yref="paper",
            x0=max(t1, data_start),
            y0=0,
            x1=min(t2, data_end),
            y1=1,
            fillcolor="lightgreen",
            opacity=0.3,
            layer="below",
            line_width=0,
        ))
        annotations.append(dict(
            x=max(t1, data_start) + (min(t2, data_end) - max(t1, data_start)) / 2,
            y=y_max,
            xref="x",
            yref="y",
            text="150 mg",
            showarrow=False,
            yshift=10,
            font=dict(color="black")
        ))

    # Region 3: After t2, dosage 75 mg
    if data_end >= t2:
        shapes.append(dict(
            type="rect",
            xref="x",
            yref="paper",
            x0=max(t2, data_start),
            y0=0,
            x1=data_end,
            y1=1,
            fillcolor="lightyellow",
            opacity=0.3,
            layer="below",
            line_width=0,
        ))
        annotations.append(dict(
            x=max(t2, data_start) + (data_end - max(t2, data_start)) / 2,
            y=y_max,
            xref="x",
            yref="y",
            text="75 mg",
            showarrow=False,
            yshift=10,
            font=dict(color="black")
        ))

    # Add vertical lines for t1 and t2
    vlines = []
    if data_start <= t1 <= data_end:
        vlines.append(dict(
            type="line",
            x0=t1,
            y0=0,
            x1=t1,
            y1=1,
            xref='x',
            yref='paper',
            line=dict(color='black', dash='dash')
        ))
    if data_start <= t2 <= data_end:
        vlines.append(dict(
            type="line",
            x0=t2,
            y0=0,
            x1=t2,
            y1=1,
            xref='x',
            yref='paper',
            line=dict(color='black', dash='dash')
        ))

    # Update figure layout
    fig.update_layout(
        title="Heart Rate Data Over Time",
        xaxis_title="Date",
        yaxis_title="Values",
        shapes=shapes + vlines,
        annotations=annotations,
        xaxis=dict(range=[data_start, data_end]),
        yaxis=dict(range=y_range),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    # Render the Plotly figure in Streamlit
    st.plotly_chart(fig, use_container_width=True)

# Add New Heart Rate Data
def add_heart_rate_data(date, systolic, diastolic, pulse):
    data = load_heart_rate_data()
    if data is None:
        data = {"profile_name": "Omron_X7_Heart_Rate", "num_data_points": 3, "data_point_names": ["Systolic", "Diastolic", "Pulse"], "data": {}}

    data['data'][date] = [systolic, diastolic, pulse]
    save_heart_rate_data(data)
    st.success("New heart rate data added!")

# Main Streamlit app
st.title("Health Application")
st.write("Choose your app:")

if "selected_app" not in st.session_state:
    st.session_state.selected_app = None


# Adjusted to have three columns
col1, col2, col3, col4 = st.columns(4)  # Adjusted to have four columns

with col1:
    if st.button("Weight App"):
        st.session_state.selected_app = "Weight App"

with col2:
    if st.button("Heart Rate App"):
        st.session_state.selected_app = "Heart Rate App"

with col3:
    if st.button("General Health Tests App"):
        st.session_state.selected_app = "General Health Tests App"

with col4:
    if st.button("Withings SmartWatch App"):
        st.session_state.selected_app = "Withings SmartWatch App"


if st.session_state.selected_app == "Weight App":
    st.subheader("Withings Data Visualization")
    
    # Add a button to re-authenticate
    if st.button("Re-authenticate with Withings"):
        # Run withings_auth.py as a subprocess
        subprocess.Popen(['python', 'withings_auth.py'])
        st.info("Please complete the authentication in the opened browser window.")
        st.info("After completing authentication, click 'Check for Tokens'.")
    
    # Add a button to check for tokens
    if st.button("Check for Tokens"):
        st.experimental_rerun()
    
    # Check if tokens are available
    if os.path.exists(TOKENS_FILE_PATH):
        # Load tokens
        with open(TOKENS_FILE_PATH, 'r') as f:
            tokens = json.load(f)
            access_token = tokens.get('access_token')
            refresh_token = tokens.get('refresh_token')
        
        # Proceed to fetch and plot data
        measure_type = st.selectbox("Choose a measurement type", 
            [("Weight (kg)", 1), 
             ("Fat Ratio (%)", 6), 
             ("Fat-Free Mass (kg)", 5),
             ("Fat Mass Weight (kg)", 8),
             ("Muscle Mass (kg)", 76),
             ("Hydration (kg)", 77),
             ("Bone Mass (kg)", 88),
             ("Visceral Fat Level", 170),
             ("Body Score (units)", 226)],
            format_func=lambda x: x[0]
        )
        
        if st.button("Fetch and Plot Data"):
            success = fetch_measurements(access_token, measure_type[1])
            if success:
                plot_weight_measurements(measure_type[1], measure_type[0])
            else:
                st.error("Failed to fetch data. Please try re-authenticating.")
    else:
        st.warning("No tokens found. Please click 'Re-authenticate with Withings' to authenticate.")
    pass

elif st.session_state.selected_app == "Heart Rate App":
    st.subheader("Heart Rate Data Visualization and Entry")
    
    # Add checkboxes for each plot type
    systolic_checked = st.checkbox("Systolic", value=True)
    diastolic_checked = st.checkbox("Diastolic", value=True)
    pulse_checked = st.checkbox("Pulse", value=True)
    
    selected_plots = []
    if systolic_checked:
        selected_plots.append("Systolic")
    if diastolic_checked:
        selected_plots.append("Diastolic")
    if pulse_checked:
        selected_plots.append("Pulse")

    if st.button("Plot Heart Rate Data"):
        plot_heart_rate_data(selected_plots)
    
    st.subheader("Add New Heart Rate Data")
    date = st.date_input("Date", datetime.today())
    systolic = st.number_input("Systolic", min_value=50, max_value=200, value=120)
    diastolic = st.number_input("Diastolic", min_value=30, max_value=120, value=80)
    pulse = st.number_input("Pulse", min_value=40, max_value=150, value=70)

    if st.button("Add Heart Rate Data"):
        add_heart_rate_data(date.strftime('%Y-%m-%d'), systolic, diastolic, pulse)
    pass

elif st.session_state.selected_app == "General Health Tests App":
    # Call the function from general_health_tests.py
    general_health_tests.general_health_tests_app()
    pass

elif st.session_state.selected_app == "Withings SmartWatch App":
    withings_smartwatch_app.run_app()
