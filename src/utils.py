import logging
import pandas as pd

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

    def remove_duplicate(self):
        self.logger.info("Removing duplicate records")
        self.errors = self.clean[self.clean.duplicated(keep=False)]
        self.clean.drop_duplicates(keep="first", inplace=True)
        self.logger.info(f"Removed {len(self.errors)} duplicate records")

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
        pass

    def check_order_customer_name(self):
        pass

    def check_customer_email(self):
        pass

    def check_product(self):
        pass

    def check_category(self):
        pass

    def check_quantity(self):
        pass

    def check_unit_price(self):
        pass

    def check_country(self):
        pass