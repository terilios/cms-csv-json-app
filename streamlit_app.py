import streamlit as st
import pandas as pd
import json
from cms_csv_to_json import main, load_schema  # Ensure this file is in the same directory

st.title("CSV to JSON Converter")

uploaded_file = st.file_uploader("Upload a CSV file", type="csv")

if uploaded_file is not None:
    # Extract the original filename and change the extension to .json
    original_filename = uploaded_file.name
    json_filename = original_filename.rsplit('.', 1)[0] + '.json'
    
    # Process the CSV file
    try:
        schema_path = 'V2.0.0_Hospital_price_transparency_schema.json'
        schema = load_schema(schema_path)
        json_output = main(uploaded_file, schema)
        
        # Provide a download button for the JSON file with the same name as the CSV
        st.download_button(
            label="Download JSON",
            data=json.dumps(json_output, indent=4),
            file_name=json_filename,
            mime='application/json'
        )
    except Exception as e:
        st.error(f"Error processing file: {e}")