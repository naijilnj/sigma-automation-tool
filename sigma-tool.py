import streamlit as st
import pandas as pd
import io
import csv

# Streamlit app title
st.title("Sigma Percentage Checker")

# File uploader to upload CSV file
uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

# Function to clean and standardize the CSV file
def clean_csv(file):
    try:
        # Read the file as raw string content
        file_content = file.read().decode('ISO-8859-1')
        
        # Automatically detect the delimiter
        sniffer = csv.Sniffer()
        delimiter = sniffer.sniff(file_content).delimiter
        
        # Use io.StringIO to handle the string as a file-like object
        file_like = io.StringIO(file_content)
        
        # Read the CSV file, skipping problematic rows
        df = pd.read_csv(file_like, delimiter=delimiter, on_bad_lines='skip')
        return df, "File cleaned successfully!"
    except Exception as e:
        return None, f"Error cleaning the file: {e}"

# Function to check Sigma rows and navigate upwards
def check_sigma(df):
    results = []
    for index, row in df.iterrows():
        # Identify the Sigma label row
        if 'Sigma' in str(row.iloc[0]):  
            # Get the next row (which contains percentages) if it's within bounds
            if index + 1 < len(df):
                percentage_row = df.iloc[index + 1]
                percentages_less_than_100 = []  # To store all percentages < 100% in this row
                for i, value in enumerate(percentage_row[1:], 1):  # Skip the first column (Sigma label)
                    if isinstance(value, str) and '%' in value:
                        try:
                            percentage_value = float(value.replace('%', '').strip())
                            # Add to the list if Sigma is less than 100%
                            if percentage_value < 100.0:
                                percentages_less_than_100.append(percentage_value)
                        except ValueError:
                            continue
                # If there are percentages < 100%, ensure a single output for this Sigma block
                if percentages_less_than_100:
                    for upward_index in range(index, -1, -1):  # Traverse upwards
                        if 'Table: 1<BR/>Level: Top' in str(df.iloc[upward_index, 0]):
                            # Two rows above this cell
                            target_index = upward_index - 2
                            if target_index >= 0:
                                target_cell = df.iloc[target_index, 0]
                                percentages_text = ", ".join(f"{val}%" for val in percentages_less_than_100)
                                # Append a single result for the entire Sigma block
                                results.append(f"Sigma < 100% (Values: {percentages_text}). Question: {target_cell}")
                            break
                    break  # Stop further processing for this Sigma block to avoid duplicates
    return results

# If a file is uploaded
if uploaded_file is not None:
    try:
        # Clean and standardize the file before processing
        df, cleaning_message = clean_csv(uploaded_file)
        if df is not None:
            st.write(cleaning_message)
            st.write("File uploaded successfully!")

            # Run the Sigma check function
            sigma_results = check_sigma(df)

            # Display results in the Streamlit app
            if sigma_results:
                st.write("Sigma rows with less than 100% found:")
                for result in sigma_results:
                    st.write(result)
            else:
                st.write("No Sigma less than 100%.")
        else:
            st.error(cleaning_message)
    
    except Exception as e:
        st.error(f"Error processing the file: {e}")
