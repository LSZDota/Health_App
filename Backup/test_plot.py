import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

# Create some test data
x = np.linspace(0, 10, 100)
y = np.sin(x)

st.title("Test Plot")

if st.button("Plot Test Data"):
    # Create a test plot
    plt.figure(figsize=(10, 5))
    plt.plot(x, y, marker='o')
    plt.title('Sine Wave Test')
    plt.xlabel('X Axis')
    plt.ylabel('Y Axis')
    plt.grid(True)
    
    # Display the plot in Streamlit
    st.pyplot(plt.gcf())
