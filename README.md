# CMS Hospital Pricing Transparency Data Converter

This repository contains a tool for converting CSV files of hospital pricing data to JSON format while validating against the CMS Hospital Pricing Transparency schema. The solution is designed to ensure compliance with CMS requirements, helping hospitals meet the mandate for transparency in pricing.

## Table of Contents

- [Background](#background)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Schema Information](#schema-information)
- [Validation Process](#validation-process)
- [Contributing](#contributing)
- [License](#license)

## Background

The **CMS Hospital Pricing Transparency mandate** is a rule established by the Centers for Medicare & Medicaid Services (CMS) to promote transparency in hospital pricing and empower consumers with accessible information about healthcare costs. Effective January 1, 2021, the mandate requires all hospitals operating in the United States to publish their standard charges for items and services they provide. This includes:

- **Gross Charges**: The full, standard rates hospitals charge for items and services before any discounts or insurance adjustments.
- **Discounted Cash Prices**: The prices a hospital is willing to accept directly from a patient for a service, without involving insurance.
- **Payer-Specific Negotiated Charges**: The charges a hospital has negotiated with third-party payers (such as insurance companies) for specific services.
- **De-identified Minimum and Maximum Charges**: The lowest and highest charges a hospital has negotiated with all third-party payers for a given service.

### Purpose and Goals of the Mandate

The CMS mandate aims to achieve several key objectives:

1. **Enhance Consumer Decision-Making**: By making pricing information readily available, the mandate empowers patients and their families to make more informed decisions about their healthcare, considering both the cost and quality of services.
   
2. **Increase Market Competition**: Transparency in pricing is expected to foster competition among hospitals, encouraging them to offer more cost-effective services to attract patients. This, in turn, can contribute to reducing overall healthcare costs.

3. **Promote Accountability and Standardization**: The mandate standardizes how hospitals report their pricing information, ensuring consistency and accuracy across the industry. This facilitates easier comparison of costs by consumers, payers, and regulators.

4. **Support Policy and Research Efforts**: The data made available through this mandate also helps policymakers, researchers, and regulators analyze healthcare pricing trends, identify outliers, and develop strategies to improve the efficiency and affordability of healthcare delivery.

### Compliance Requirements for Hospitals

To comply with the mandate, hospitals must:

- **Publish Machine-Readable Files**: Provide a comprehensive list of standard charges for all items and services in a machine-readable file format (such as JSON or CSV) that is accessible to the public. This file must include details such as service descriptions, billing codes (e.g., CPT, HCPCS), gross charges, and negotiated rates with payers.
- **Provide a Consumer-Friendly Display**: Publish at least 300 “shoppable” services (services that can be scheduled in advance) in a consumer-friendly format, including the payer-specific negotiated charges, discounted cash prices, and de-identified minimum and maximum negotiated charges.
- **Update Data Annually**: Ensure that the data is up-to-date and refreshed at least once a year to reflect any changes in charges or negotiated rates.

### Challenges and Solutions

Many hospitals face challenges in meeting these requirements due to the complexity of their pricing structures, the variability in negotiated rates, and the need to format and validate their data according to CMS standards. 

This tool addresses these challenges by:

- **Automating the Conversion of CSV to JSON**: Simplifies the data preparation process by converting hospital pricing data from CSV files (a common format for internal hospital systems) into JSON, which is required for the machine-readable file format.
- **Ensuring Schema Compliance**: Validates the converted data against the CMS Hospital Pricing Transparency schema (versions 2.0.0 and 2.1.0), ensuring all required fields, formats, and data types are correct. This reduces the risk of non-compliance and potential penalties.
- **Providing an Intuitive User Interface**: Utilizes a Streamlit-based web interface to make the tool accessible to users with varying technical skills, allowing easy upload of CSV files, conversion to JSON, and validation against the CMS schema.

By leveraging this tool, hospitals can streamline their data publication processes, reduce the risk of non-compliance, and contribute to a more transparent healthcare market.

## Features

- **CSV to JSON Conversion**: Converts hospital pricing data from CSV to JSON format, ready for publication according to CMS requirements.
- **Schema Validation**: Ensures JSON output complies with the CMS Hospital Pricing Transparency schema (versions 2.0.0 and 2.1.0).
- **Streamlit Web Interface**: Provides a user-friendly web app for uploading CSV files, converting data, and viewing validation results.
- **Support for Multiple Schema Versions**: Handles different schema versions, allowing for easy updates as CMS requirements evolve.

## Installation

To install and set up the tool, follow these steps:

1. **Clone the Repository**:

   ```sh
   git clone https://github.com/yourusername/cms-hospital-pricing-transparency.git
   cd cms-hospital-pricing-transparency
   ```

2. **Create a Virtual Environment**:

   ```sh
   python -m venv env
   source env/bin/activate # On Windows use `env\Scripts\activate`
   ```

3. **Install the Required Packages**:

   Use the `requirements.txt` file to install the necessary Python libraries:

   ```sh
   pip install -r requirements.txt
   ```

## Usage

### Running the Tool

1. **Start the Streamlit App**:

   Launch the Streamlit app to interact with the converter via a web interface:

   ```sh
   streamlit run streamlit_app.py
   ```

2. **Upload CSV File**:

   - Use the web interface to upload your hospital pricing CSV file.
   - The tool will automatically convert the CSV to JSON and validate it against the CMS schema.

3. **View and Download Results**:

   - The JSON output and any validation errors will be displayed in the web app.
   - You can download the validated JSON file directly from the interface.

### Command-Line Usage

If you prefer to use the tool via the command line, you can run the `cms_csv_to_json.py` script directly:

```sh
python cms_csv_to_json.py --input <input_csv_file> --output <output_json_file> --schema <schema_version>
```

Replace `<input_csv_file>`, `<output_json_file>`, and `<schema_version>` with your desired input file path, output file path, and schema version (e.g., `2.0.0` or `2.1.0`).

## Configuration

### Schema Versions

The tool supports multiple schema versions (`2.0.0` and `2.1.0`). The appropriate schema file is automatically selected based on the version specified during the conversion. You can also modify the `config.py` file to add or update schema versions.

## Schema Information

This tool uses the CMS Hospital Pricing Transparency schema, which includes detailed requirements for various data fields, such as:

- **Standard Charges**: Gross charges, minimum and maximum rates, discounted cash prices, and payer-specific charges.
- **Affirmations and License Information**: Legal affirmations, license numbers, and state information.
- **Code Information**: Codes for various services, such as CPT, HCPCS, and DRG codes.
- **Payer Information**: Details about the payer, plan names, and charge methodologies.

### Supported Schema Versions

- **V2.0.0**: The initial version supporting basic data structures and validation rules.
- **V2.1.0**: An enhanced version with conditional validations and additional flexibility in representing payer information.

## Validation Process

The JSON output is validated against the CMS schema using the `jsonschema` library. Validation errors, if any, are displayed in the Streamlit app or printed in the command line output.

### Example Validation

If the JSON output does not conform to the schema, the tool provides detailed error messages, indicating the fields that do not comply with the schema requirements.

## Contributing

Contributions are welcome! Please follow these steps to contribute:

1. **Fork the Repository**: Click the "Fork" button at the top right of this page.
2. **Clone Your Fork**: 
   ```sh
   git clone https://github.com/terilios/cms-csv-json-app/
   ```
3. **Create a Feature Branch**:
   ```sh
   git checkout -b feature/your-feature-name
   ```
4. **Commit Your Changes**: Make your changes and commit them with a descriptive message.
5. **Push Your Changes**: 
   ```sh
   git push origin feature/your-feature-name
   ```
6. **Submit a Pull Request**: Go to the original repository and click "New Pull Request."

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.
