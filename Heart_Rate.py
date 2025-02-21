import tkinter as tk
from tkinter import simpledialog, messagebox, filedialog
import os
import json
import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkcalendar import Calendar

# Create the main application window
root = tk.Tk()
root.title('Data Profile Manager')
root.geometry('500x300')

# Create buttons for main interface
create_btn = tk.Button(root, text='Create Data Profile', command=None)  # command will be added later
load_btn = tk.Button(root, text='Load Data Profile', command=None)  # command will be added later
plot_btn = tk.Button(root, text='Plot Data', command=None)  # command will be added later

create_btn.pack(pady=20)
load_btn.pack(pady=20)
plot_btn.pack(pady=20)



def create_data_profile():
    # Ask the user for the name of the data profile
    profile_name = simpledialog.askstring('Input', 'Enter the name of the data profile:')
    if not profile_name:
        return

    # Check if a file with the given profile name already exists
    if os.path.exists(f'{profile_name}.json'):
        overwrite = messagebox.askyesno('Warning', f'A data profile with the name "{profile_name}" already exists. Do you want to overwrite it?')
        if not overwrite:
            return

    # Ask the user for the number of data points they want to associate with each date
    num_data_points = simpledialog.askinteger('Input', 'Enter the number of data points for each date:')
    if not num_data_points:
        return

    # Ask the user for names for each data point
    data_point_names = []
    for i in range(num_data_points):
        data_point_name = simpledialog.askstring('Input', f'Enter the name for data point {i+1}:')
        if not data_point_name:
            return
        data_point_names.append(data_point_name)

    # Store this information in a local file
    profile_data = {
        'profile_name': profile_name,
        'num_data_points': num_data_points,
        'data_point_names': data_point_names,  # Store the names of the data points
        'data': {}
    }
    with open(f'{profile_name}.json', 'w') as file:
        json.dump(profile_data, file)

    messagebox.showinfo('Success', 'Data profile created successfully!')



# Update the command for the 'Create Data Profile' button
create_btn.config(command=create_data_profile)

def load_data_profile():
    global current_profile_data  # Declare the variable as global

    # Ask the user to select a data profile file to load
    file_path = filedialog.askopenfilename(filetypes=[('JSON Files', '*.json')])
    if not file_path:
        return

    # Load the selected data profile
    with open(file_path, 'r') as file:
        profile_data = json.load(file)

    # Update the current_profile_data variable with the loaded data
    current_profile_data = profile_data

    # Display the loaded data profile details
    profile_name = profile_data['profile_name']
    num_data_points = profile_data['num_data_points']
    data_point_names = ', '.join(profile_data['data_point_names'])
    messagebox.showinfo('Loaded Data Profile', f'Profile Name: {profile_name}\nNumber of Data Points: {num_data_points}\nData Point Names: {data_point_names}')


# Update the command for the 'Load Data Profile' button
load_btn.config(command=load_data_profile)



current_profile_data = None  # This will store the currently loaded data profile

def enter_data():
    global current_profile_data

    # Check if a data profile is loaded
    if not current_profile_data:
        messagebox.showerror('Error', 'Please load a data profile first.')
        return

    # Use the Calendar widget for date selection
    date_win = tk.Toplevel(root)
    date_win.title('Select a Date')
    cal = Calendar(date_win, selectmode='day', year=datetime.datetime.now().year, month=datetime.datetime.now().month, day=datetime.datetime.now().day)
    cal.pack(pady=20)

    def on_date_select():
        date_obj = cal.selection_get()
        date_str = date_obj.strftime('%Y-%m-%d')
        date_win.destroy()
    
        # Check if data exists for the selected date
        existing_data = current_profile_data['data'].get(date_str)
        
        # Create a new window for data entry
        data_win = tk.Toplevel(root)
        data_win.title(f'Enter data for {date_str}')
    
        # If data exists for the selected date, display it
        if existing_data:
            existing_data_str = ', '.join(map(str, existing_data))
            tk.Label(data_win, text=f'Existing data for {date_str}: {existing_data_str}').pack(pady=10)
    
        # Create entry widgets for each data point
        entries = []
        for name in current_profile_data['data_point_names']:
            tk.Label(data_win, text=name).pack(pady=5)
            entry = tk.Entry(data_win)
            entry.pack(pady=5)
            entries.append(entry)
    
        # Function to save the entered data
        def save_data():
            data_values = []
            for entry in entries:
                try:
                    value = float(entry.get())
                    data_values.append(value)
                except ValueError:
                    messagebox.showerror('Error', 'Please enter valid numbers for all data points.')
                    return
    
            # Save the entered data to the loaded data profile
            current_profile_data['data'][date_str] = data_values
            with open(f"{current_profile_data['profile_name']}.json", 'w') as file:
                json.dump(current_profile_data, file)
    
            messagebox.showinfo('Success', f'Data for {date_str} saved successfully!')
            data_win.destroy()
    
        # Add a button to save the entered data
        save_btn = tk.Button(data_win, text='Save Data', command=save_data)
        save_btn.pack(pady=20)
    
        # Adjust the width and height of the window
        width = max(300, len(data_win.title()) * 10)
        height = 120 + 50 * len(current_profile_data['data_point_names'])  # 50 for padding and buttons, 30 per data point
        data_win.geometry(f"{width}x{height}")



    date_select_btn = tk.Button(date_win, text='Select Date', command=on_date_select)
    date_select_btn.pack(pady=20)


    
# Add a button to the main interface for data entry
enter_data_btn = tk.Button(root, text='Enter Data', command=enter_data)
enter_data_btn.pack(pady=20)

def edit_data():
    global current_profile_data

    # Check if a data profile is loaded
    if not current_profile_data:
        messagebox.showerror('Error', 'Please load a data profile first.')
        return

    # Ask the user to select a date
    date_str = simpledialog.askstring('Input', 'Enter the date (YYYY-MM-DD) you want to edit:')
    if not date_str:
        return

    # Check if data exists for the selected date
    existing_data = current_profile_data['data'].get(date_str)
    if not existing_data:
        messagebox.showerror('Error', f'No data found for {date_str}.')
        return

    # Display existing data for the selected date
    existing_data_str = ', '.join(map(str, existing_data))
    messagebox.showinfo('Existing Data', f'Data for {date_str}: {existing_data_str}')

    # Prompt the user to edit the data for the selected date
    edited_data = []
    for i, value in enumerate(existing_data):
        new_value = simpledialog.askfloat('Input', f'Edit data value {i+1} for {date_str} (current value: {value}):', initialvalue=value)
        if new_value is None:
            return
        edited_data.append(new_value)

    # Save the edited data to the loaded data profile
    current_profile_data['data'][date_str] = edited_data
    with open(f"{current_profile_data['profile_name']}.json", 'w') as file:
        json.dump(current_profile_data, file)

    messagebox.showinfo('Success', f'Data for {date_str} edited successfully!')

# Add a button to the main interface for data editing
edit_data_btn = tk.Button(root, text='Edit Data', command=edit_data)
edit_data_btn.pack(pady=20)


def plot_data():
    global current_profile_data

    # Check if a data profile is loaded
    if not current_profile_data:
        messagebox.showerror('Error', 'Please load a data profile first.')
        return

    # Extract dates and data from the loaded profile
    dates = sorted(current_profile_data['data'].keys())
    data_values = [current_profile_data['data'][date] for date in dates]

    # Convert string dates to datetime objects for plotting
    dates = [datetime.datetime.strptime(date, '%Y-%m-%d').date() for date in dates]

    # Plot each data series separately
    for i, name in enumerate(current_profile_data['data_point_names']):
        plt.figure(figsize=(10, 5))
        plt.plot(dates, [values[i] for values in data_values], marker='o')
        plt.title(f"{name} for {current_profile_data['profile_name']}")
        plt.xlabel('Date')
        plt.ylabel('Value')
        plt.grid(True)
        plt.tight_layout()
        plt.show()

# Update the command for the 'Plot Data' button
plot_btn.config(command=plot_data)


# Run the application
root.mainloop()