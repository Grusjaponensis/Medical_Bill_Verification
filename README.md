# Report Verification Tool

This tool is designed to verify the unit price data in reports against a baseline file. It allows users to upload two Excel files: one containing the data to be verified and the other serving as the baseline for verification. The tool compares the unit prices and highlights discrepancies.

## Features

- Upload two Excel files: one to check and one as the baseline.
- Update column names for "Product Name" and "Unit Price" if they differ from the default values.
- Verify unit prices and identify any discrepancies between the two files.
- Display the verified data with an additional column showing the baseline unit price for comparison.

## Usage

1. **Upload Files**: Upload the Excel file to be checked and the baseline Excel file.
2. **Update Column Names**: Optionally, update the column names for "Product Name" and "Unit Price" using the provided text inputs.
3. **Verify Data**: Click the "Verify Data" button to start the verification process. Any discrepancies will be highlighted.

## Installation

To run this tool, you need to have Python installed along with the following packages:

- `streamlit`
- `pandas`
- `openpyxl`
- `xlrd`

## Access
You can visit [https://medical-bill.streamlit.app/](https://medical-bill.streamlit.app/) to access this project.
