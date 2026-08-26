# get csv file with pandas from sys args   
import pandas as pd
import sys
import utils

def main():
    df = get_csv_file()
    utils.report_issues(df)
    issues = {}
    cleaner = utils.DataCleaner(df)
    issues["order_id"] = cleaner.check_order_id()
    cleaner.check_order_date()
    cleaner.check_order_customer_name()
    cleaner.check_customer_email()
    cleaner.check_product()
    cleaner.check_category()
    cleaner.check_quantity()

    export_report_files(issues, cleaner)

def get_csv_file() -> pd.DataFrame: 
    # get csv file from sys args
        print("Fetching data ...")
        try:
            csv_file = sys.argv[1:]
            url = csv_file[0]
        except IndexError:
            print("no argument recived as file address.\nexample: 'python src/main.py [file_path_address]'")
            sys.exit(1)
        except Exception as e:
            print(e)
            sys.exit(1)
        df = pd.read_csv(url)
        return df

def export_report_files(issues, cleaner):
     pass


if __name__ == "__main__":
    main()
