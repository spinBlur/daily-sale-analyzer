# Daily Sale Analyzer

A Python-based tool for analyzing, cleaning, and reporting on daily sales data. This application validates sales records, identifies data quality issues, and generates comprehensive sales reports with revenue analytics.

## Features

- **Data Validation**: Comprehensive validation of all sales data fields
- **Data Cleaning**: Automatic detection and handling of:
  - Duplicate records
  - Invalid order IDs, dates, and quantities
  - Missing or malformed customer information
  - Invalid email addresses
  - Missing product or category information
  - Invalid unit prices and quantities
  - Invalid country codes

- **Sales Analytics**: Generates detailed reports including:
  - Total sales and order count
  - Top 5 products by revenue
  - Top 5 countries by revenue
  - Average order value
  - Complete data quality metrics

- **Output Generation**: Creates three output files:
  - Cleaned data (valid records only)
  - Issue data (records with validation errors)
  - Sales report (summary analytics and quality metrics)

## Installation

1. Clone or download this repository:
```bash
git clone <repository-url>
cd daily-sale-analyzer
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

### Requirements
- Python 3.8+
- pandas
- numpy
- email-normalize

## Usage

Run the analyzer with a CSV file as input:

```bash
python src/main.py input/sales_data.csv
```

**Arguments:**
- `input/sales_data.csv`: Path to the CSV file containing sales data

### Expected CSV Columns

The input CSV should contain the following columns:
- `order_id`: Unique order identifier
- `order_date`: Date of the order
- `customer_name`: Name of the customer
- `customer_email`: Email address of the customer
- `product`: Product name
- `category`: Product category
- `quantity`: Number of units ordered
- `unit_price`: Price per unit
- `country`: Country code or name

## Output Files

### cleaned_data.csv
Contains all valid sales records after data cleaning. Includes:
- All original columns (with corrections applied)
- `revenue` column (quantity × unit_price)

### issue_data.csv
Contains records that failed validation. Useful for:
- Identifying data quality problems
- Manual review and correction
- Tracking problematic records

### sales_report.txt
Summary report containing:
- Total orders and total sales revenue
- Top 5 products by revenue
- Top 5 countries by revenue
- Data quality metrics (duplicate records, invalid fields, etc.)

## Example

```bash
# Process a sales data file
python src/main.py input/sales_data.csv

# Output:
# Sales Data Analysis
# ====================
# Rows: 1000
# Columns: 9
# 
# Missing values will be listed
# Duplicate records count
```

After execution, check the `output/` directory for:
- `cleaned_data.csv` - Clean dataset ready for analysis
- `issue_data.csv` - Records requiring attention
- `sales_report.txt` - Executive summary and analytics

## Attention

- This project will calculate the revenue base on the validation of order_date, product, quantity, unit_price.
If one of those fields are invalid, that record will not considering for revenue calculation and it will be moved to issue_data.csv.
- The other invalid fields will be reported.
- Only duplicate records will be removed from the cleaned_data.csv.