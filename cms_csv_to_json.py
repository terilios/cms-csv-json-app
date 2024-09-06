import pandas as pd
import json
import logging
from datetime import datetime
from jsonschema import validate, ValidationError
import re
import urllib.parse

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_csv(file_obj):
    try:
        full_data = pd.read_csv(file_obj, encoding='ISO-8859-1', low_memory=False)
        data = full_data.iloc[2:]
        data.columns = full_data.iloc[1]
        data.reset_index(drop=True, inplace=True)
        return data, full_data
    except Exception as e:
        logging.error(f"Error loading CSV file: {e}")
        raise

def extract_metadata(full_data):
    try:
        metadata = full_data.iloc[:2]
        hospital_name = metadata.iloc[0, 0]
        last_updated_on = metadata.iloc[0, 1]
        last_updated_on = datetime.strptime(last_updated_on, '%m/%d/%Y').strftime('%Y-%m-%d')
        hospital_location = metadata.iloc[0, 3].split('|')
        hospital_address = metadata.iloc[0, 4].split('|')
        license_info = metadata.iloc[0, 5].split('|')
        license_number = license_info[0]
        license_state = "MA"
        affirmation_text = "To the best of its knowledge and belief, the hospital has included all applicable standard charge information in accordance with the requirements of 45 CFR 180.50, and the information encoded is true, accurate, and complete as of the date indicated."
        confirm_affirmation = metadata.iloc[0, 6].strip().lower() == 'true'
        
        return {
            "hospital_name": hospital_name,
            "last_updated_on": last_updated_on,
            "version": "2.1.0",
            "hospital_location": hospital_location,
            "hospital_address": hospital_address,
            "license_information": {
                "license_number": license_number,
                "state": license_state
            },
            "affirmation": {
                "affirmation": affirmation_text,
                "confirm_affirmation": confirm_affirmation
            }
        }
    except Exception as e:
        logging.error(f"Error extracting metadata: {e}")
        raise

ALLOWED_METHODOLOGIES = [
    "case rate",
    "fee schedule",
    "percent of total billed charges",
    "per diem",
    "algorithm-based",
    "other"
]

def validate_or_default_methodology(methodology):
    processed_methodology = methodology.strip().lower().rstrip('.')
    if processed_methodology in ALLOWED_METHODOLOGIES:
        return processed_methodology
    else:
        logging.warning(f"Unrecognized methodology: {methodology}. Defaulting to 'other'.")
        return "other"

def safe_float(value, default=0.01):
    try:
        val = round(float(value), 2)
        if val <= 0:
            logging.warning(f"Value must be greater than zero. Using default {default}.")
            return default
        return val
    except ValueError:
        logging.warning(f"Invalid float conversion for value: {value}. Using default {default}.")
        return default

def extract_payer_plan_data(row):
    payer_plan_data = {}
    
    for col in row.index:
        if pd.notna(row[col]):
            parts = col.split('|')
            if len(parts) >= 3 and ('standard_charge' in parts[0] or 'estimated_amount' in parts[0]):
                field_prefix, payer_name, plan_name, *attribute_parts = parts
                payer_plan_key = f"{payer_name}|{plan_name}"

                if payer_plan_key not in payer_plan_data:
                    payer_plan_data[payer_plan_key] = {
                        "payer_name": payer_name,
                        "plan_name": plan_name,
                        "standard_charge_dollar": "",
                        "standard_charge_algorithm": "",
                        "estimated_amount": "",
                        "methodology": "other",
                        "additional_payer_notes": "no additional notes"
                    }

                attribute = attribute_parts[0] if attribute_parts else None
                if attribute == 'negotiated_dollar':
                    payer_plan_data[payer_plan_key]["standard_charge_dollar"] = safe_float(row[col])
                elif attribute == 'negotiated_percentage':
                    payer_plan_data[payer_plan_key]["standard_charge_percentage"] = safe_float(row[col])
                elif attribute == 'negotiated_algorithm':
                    payer_plan_data[payer_plan_key]["standard_charge_algorithm"] = row[col] if pd.notna(row[col]) else ""
                elif attribute == 'estimated_amount' or 'estimated_amount' == field_prefix:
                    payer_plan_data[payer_plan_key]["estimated_amount"] = safe_float(row[col])
                elif attribute == 'methodology':
                    payer_plan_data[payer_plan_key]["methodology"] = validate_or_default_methodology(row[col]) if pd.notna(row[col]) else ""
                elif attribute == 'additional_payer_notes':
                    if pd.notna(row[col]) and row[col].strip() != "":
                        note = row[col].replace('\n', ' ').replace('\r', ' ')
                        note = re.sub(r'(https?://\S+)', lambda x: urllib.parse.quote_plus(x.group()), note)
                        payer_plan_data[payer_plan_key]["additional_payer_notes"] = note

    for payer_info in payer_plan_data.values():
        if payer_info["estimated_amount"] == "":
            payer_info["estimated_amount"] = payer_info["standard_charge_dollar"]

    for payer_info in payer_plan_data.values():
        for key, value in list(payer_info.items()):
            if pd.isna(value):
                if key in ["standard_charge_dollar", "estimated_amount"]:
                    payer_info[key] = 0.01
                elif key == "standard_charge_percentage":
                    del payer_info[key]
                else:
                    payer_info[key] = ""
            elif key == "standard_charge_percentage":
                payer_info[key] = round(float(value), 2)
            elif key == "code":
                payer_info[key] = str(value)

    return list(payer_plan_data.values())

def convert_row_to_json(row):
    try:
        code_information = []
        for i in range(1, 3):
            code = row.get(f'code|{i}')
            code_type = row.get(f'code|{i}|type')
            if pd.notna(code) and pd.notna(code_type):
                code_information.append({"code": str(code), "type": code_type})

        def format_dollar(amount):
            try:
                return round(float(amount), 2) if pd.notna(amount) else None
            except (ValueError, TypeError):
                return None

        def format_percentage(percentage):
            try:
                return round(float(percentage), 2) if pd.notna(percentage) else None
            except (ValueError, TypeError):
                return None

        additional_generic_notes = row.get('additional_generic_notes', "")
        if pd.notna(additional_generic_notes) and additional_generic_notes != "":
            additional_generic_notes = additional_generic_notes.replace('\n', ' ').replace('\r', ' ')
            additional_generic_notes = re.sub(r'(https?://\S+)', lambda x: urllib.parse.quote_plus(x.group()), additional_generic_notes)
        else:
            additional_generic_notes = "no additional notes"

        standard_charges = {
            "setting": row['setting'].strip().lower() if pd.notna(row['setting']) else None,
            "gross_charge": format_dollar(row['standard_charge|gross']),
            "minimum": format_dollar(row['standard_charge|min']),
            "maximum": format_dollar(row['standard_charge|max']),
            "discounted_cash": format_dollar(row['standard_charge|discounted_cash']),
            "additional_generic_notes": additional_generic_notes
        }

        if 'gross_charge' not in standard_charges:
            standard_charges['gross_charge'] = None
        if 'discounted_cash' not in standard_charges:
            standard_charges['discounted_cash'] = None

        standard_charges = {k: v for k, v in standard_charges.items() if v is not None or k in ['gross_charge', 'discounted_cash']}

        payers_information = extract_payer_plan_data(row)
        if payers_information:
            standard_charges["payers_information"] = payers_information

        json_object = {
            "description": row['description'],
            "code_information": code_information,
            "standard_charges": [standard_charges]
        }

        return json_object
    except Exception as e:
        logging.error(f"Error converting row to JSON: {e}")
        raise

def load_schema(schema_path):
    with open(schema_path, 'r') as file:
        schema = json.load(file)
    return schema

def main(file_obj, schema):
    try:
        data, full_data = load_csv(file_obj)
        hospital_info = extract_metadata(full_data)
        core_data = data.apply(convert_row_to_json, axis=1).tolist()
        hospital_info["standard_charge_information"] = core_data
        validate(instance=hospital_info, schema=schema)
        return hospital_info
    except ValidationError as ve:
        logging.error(f"Validation error: {ve}")
        raise
    except Exception as e:
        logging.error(f"Error in main function: {e}")
        raise

if __name__ == "__main__":
    schema_path = 'V2.0.0_Hospital_price_transparency_schema.json'
    schema = load_schema(schema_path)

    csv_files = [
        'csv-json/04-2774441_Boston-Childrens-North-Dartmouth_StandardCharges.csv',
        'csv-json/04-2774441_Boston-Childrens-Brookline_StandardCharges.csv',
        'csv-json/04-2774441_Boston-Childrens-Lexington_StandardCharges.csv',
        'csv-json/04-2774441_Boston-Childrens-Longwood_StandardCharges.csv',
        'csv-json/04-2774441_Boston-Childrens-Peabody_StandardCharges.csv',
        'csv-json/04-2774441_Boston-Childrens-Waltham_StandardCharges.csv',
        'csv-json/04-2774441_Boston-Childrens-Weymouth_StandardCharges.csv',
        'csv-json/04-2774441_Boston-Childrens-Martha-Eliot_StandardCharges.csv',
    ]
    
    for csv_file_path in csv_files:
        filename_without_extension = csv_file_path.split('.')[0]
        output_file_path = f"{filename_without_extension}-output.json"
        
        try:
            output = main(csv_file_path, schema)
            with open(output_file_path, 'w') as f:
                json.dump(output, f, indent=4)
            logging.info(f"JSON file saved: {output_file_path}")
        except Exception as e:
            logging.error(f"Failed to save JSON file for {csv_file_path}: {e}")