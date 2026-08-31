import logging
import pandas as pd
import numpy as np
import email_normalize

def get_logging() -> logging.Logger:
    """ Return stream logger with custom format """
    logger = logging.getLogger(__name__)

    stream = logging.StreamHandler()
    formater = logging.Formatter('%(levelname)s - %(message)s')
    stream.setFormatter(formater)

    logger.addHandler(stream)
    logger.setLevel(logging.DEBUG)
    return logger

def report_issues(df):
    print("\nSales Data Analysis")
    print("=" * 20 + "\n")
    print(f"Rows: {df.shape[0]}")
    print(f"Columns: {df.shape[1]}\n")

    print("Missing value:")
    for x, y in df.count().items():
        if y < df.shape[0]:
            print(f"{x}: {df.shape[0] - y}")

    print()
    duplicate_order_id = df.duplicated()
    print(f"Duplicate orders: {duplicate_order_id.sum()}")

class DataCleaner:
    def __init__(self, df: pd.DataFrame):
        self.clean = df.copy()
        self.errors = pd.DataFrame(columns=df.columns)
        self.logger = get_logging()
        self.clean["status"] = True

    def remove_duplicate(self):
        self.logger.info("Removing duplicate records")
        self.errors = self.clean[self.clean.duplicated(keep=False)]
        self.clean.drop_duplicates(keep="first", inplace=True)
        self.logger.info(f"Removed {len(self.errors)} duplicate records")
        return len(self.errors)

    # add missing order_id to issue file
    def check_order_id(self):
        self.logger.info("Checking order_id")

        # convert any non int to NaN
        self.clean["order_id"] = pd.to_numeric(self.clean['order_id'], errors='coerce')

        # append NaN to issue file
        error_mask = self.clean["order_id"].isna()
        missing = len(self.clean[error_mask])
        self.errors = pd.concat([self.errors, self.clean[error_mask]])

        # fill NaN with "missing"
        self.clean["order_id"] = self.clean["order_id"].astype("Int64").astype(object)
        self.clean.fillna({"order_id": "missing"}, inplace=True)
        self.logger.info(f"moved {missing} records with missing order_id to issue file")
        return missing
        
    def check_order_date(self):
        self.logger.info("Checking order_date")
        # to datetime
        self.clean["order_date"] = pd.to_datetime(self.clean["order_date"], errors="coerce")

        # get most frequent date
        date_counts = self.clean["order_date"].dt.date.value_counts()
        if len(date_counts) == 0:
            self.logger.warning("No valid date found")
            return 0
        date_target = date_counts.idxmax()
        self.date = date_target

        # remove time and timezone
        self.clean["order_date"] = self.clean["order_date"].dt.date
        # get invalid date
        invalid_date = self.clean[(self.clean["order_date"] != date_target) | self.clean["order_date"].isna()]
        # invalid_date["order_date"] = invalid_date["order_date"].dt.date

        # append missing dates in errors df and fill them with null in clean df
        self.errors = pd.concat([self.errors, invalid_date])
        self.clean.loc[invalid_date.index, "order_date"] = np.nan
        self.logger.info(f"moved {len(invalid_date)} records with invalid date to issue file")

        # add status column to clean df for calculation
        # self.clean["status"] = self.clean["order_date"].apply(lambda x: False if pd.isnull(x)  else True)
        self.clean.loc[invalid_date.index, "status"] = False
        return len(invalid_date)

    def check_order_customer_name(self):
        self.logger.info("Checking customer_name")
        self.clean["customer_name"] = self.clean["customer_name"].str.strip()
        self.clean["customer_name"] = self.clean["customer_name"].str.title()

        # check if customer_name is null or digit
        null_count = (self.clean["customer_name"].isna()) | (self.clean["customer_name"].str.isdigit())
        counter = null_count.sum()
        if counter == 0:
            self.logger.info("No null or invalid customer_name found")
            return 0
        self.logger.info(f"Found {counter} null or invalid customer_name")
        return counter

    def check_customer_email(self):

        def normalize_email(email):
            try:
                return email_normalize.normalize(email).address
            except:
                return np.nan
        
        self.logger.info("Checking customer_email")

        # keep valid email and NaN for invalid email
        self.clean["customer_email"] = self.clean["customer_email"].apply(normalize_email)
        missing_email = self.clean["customer_email"].isna().sum()
        self.logger.info(f"Found {missing_email} null customer_email")
        return missing_email

    def check_product(self):
        self.logger.info("Checking product")

        missing_products = self.clean[(self.clean["product"].isna()) | (self.clean["product"].str.isdigit()) | (self.clean["product"].str.len() < 3)]

        self.errors = pd.concat([self.errors, missing_products])
        self.clean.loc[missing_products.index, "product"] = np.nan
        self.clean.loc[missing_products.index, "status"] = False
        self.logger.info(f"moved {len(missing_products)} records with invalid product to issue file")
        return len(missing_products)

    def check_category(self):
        self.logger.info("Checking category")
        self.clean["category"] = self.clean["category"].str.strip()
        self.clean["category"] = self.clean["category"].str.title()

        # check if category is null or digit
        null_count = (self.clean["category"].isna()) | (self.clean["category"].str.isdigit())
        counter = null_count.sum()
        if counter == 0:
            self.logger.info("No null or invalid category found")
            return 0
        self.logger.info(f"Found {counter} null or invalid category")
        return counter

    def check_quantity(self):
        self.logger.info("Checking quantity")

        # Convert to numeric first so string values like "12", "abc", or empty values
        # are handled safely instead of causing comparison errors.
        self.clean["quantity"] = pd.to_numeric(self.clean["quantity"], errors="coerce")

        # Decimal values are invalid in this data model.
        invalid_quantity = (
            self.clean["quantity"].isna()
            | (self.clean["quantity"] <= 0)
            | (self.clean["quantity"] % 1 != 0)
        )
        invalid_rows = self.clean[invalid_quantity]

        self.errors = pd.concat([self.errors, invalid_rows])
        self.clean.loc[invalid_rows.index, "quantity"] = np.nan
        self.clean.loc[invalid_rows.index, "status"] = False
        self.clean["quantity"] = self.clean["quantity"].astype("Int64")

        self.logger.info(f"moved {len(invalid_rows)} records with invalid quantity to issue file")
        return len(invalid_rows)

    def check_unit_price(self):
        self.logger.info("Checking unit_price")

        # keep numeric values
        self.clean["unit_price"] = pd.to_numeric(self.clean["unit_price"], errors='coerce')

        missing_unit = self.clean[(self.clean["unit_price"].isna()) | (self.clean["unit_price"] <= 0)]

        self.errors = pd.concat([self.errors, missing_unit])
        self.clean.loc[missing_unit.index, "unit_price"] = np.nan
        self.clean.loc[missing_unit.index, "status"] = False
        self.logger.info(f"moved {len(missing_unit)} records with invalid unit_price to issue file")
        return len(missing_unit)


    def check_country(self):
        self.logger.info("Checking country")
        self.clean["country"] = self.clean["country"].str.strip()
        self.clean["country"] = self.clean["country"].str.title()

        # Mapping of common variations to standard country names
        country_mapping = {
            'Usa': 'United States',
            'U.S.A.': 'United States',
            'United States Of America': 'United States',
            'Uk': 'United Kingdom',
            'U.K.': 'United Kingdom',
            'England': 'United Kingdom',
            'Deutschland': 'Germany',
            'Brasil': 'Brazil',
            # Add more mappings as needed
        }

        self.clean["country"] = self.clean["country"].replace(country_mapping)

        # check if country is null or digit
        null_count = (self.clean["country"].isna()) | (self.clean["country"].str.isdigit())
        counter = null_count.sum()
        if counter == 0:
            self.logger.info("No null or invalid country found")
            return 0
        self.logger.info(f"Found {counter} null or invalid country")
        return counter
