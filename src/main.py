# get csv file with pandas from sys args   
import pandas as pd
import sys
import utils

def main():
    df = get_csv_file()
    utils.report_issues(df)
    issues = {}
    cleaner = utils.DataCleaner(df)
    issues["duplicate"] = cleaner.remove_duplicate()
    issues["order_id"] = cleaner.check_order_id()
    issues["order_date"] = cleaner.check_order_date()
    issues["customer_name"] = cleaner.check_order_customer_name()
    issues["customer_email"] = cleaner.check_customer_email()
    issues["product"] = cleaner.check_product()
    issues["category"] = cleaner.check_category()
    issues["quantity"] = cleaner.check_quantity()
    issues["unit_price"] = cleaner.check_unit_price()
    issues["country"] = cleaner.check_country()

    total = cleaner.clean[cleaner.clean["status"] == True]
    cleaner.clean["revenue"] = total["quantity"] * total["unit_price"]

    issues["errors"] = cleaner.clean[cleaner.clean["status"] == False].shape[0]
    cleaner.clean.drop(columns=["status"], inplace=True)
    cleaner.errors.drop(columns=["status"], inplace=True)
    cleaner.errors.sort_values(by="order_id", inplace=True)
    cleaner.errors.drop_duplicates(inplace=True)

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
        except FileNotFoundError as e:
            print("Invalid file address. check the file name or directory again!")
            sys.exit(1)
        except Exception as e:
            print(e)
            sys.exit(1)
        df = pd.read_csv(url)
        return df

def export_report_files(issues, cleaner):
    cleaner.clean.to_csv("output/cleaned_data.csv", index=False)
    print("Cleaned data saved to output/cleaned_data.csv")

    cleaner.errors.to_csv("output/issue_data.csv", index=False)
    print("Issue data saved to output/issue_data.csv")

    # generating sales reports
    total_sales = cleaner.clean["revenue"].sum()
    total_orders = cleaner.clean["order_id"].nunique()
    top_products = cleaner.clean.groupby("product")["revenue"].sum()
    top_countries = cleaner.clean.groupby("country")["revenue"].sum()
    count_error_records = issues["errors"]
    average_order_value = total_sales / (total_orders - count_error_records)

    def format_currency(x):
        return "${:,.2f}".format(x)

    import os
    os.makedirs("output", exist_ok=True)

    with open("output/sales_report.txt", "w") as f:
        f.write(f"Sales Report for {cleaner.date}\n")
        f.write("-------------------\n")
        f.write(f"Total orders: {total_orders}\n")
        f.write(f"Total sales: {format_currency(total_sales)}\n\n")
        f.write(f"Top 5 products by revenue:\n")
        f.write(top_products.nlargest(5).apply(format_currency).to_string() + "\n\n")
        f.write(f"Top 5 countries by revenue:\n")
        f.write(top_countries.nlargest(5).apply(format_currency).to_string() + "\n\n")

        f.write("Data Quality Report\n")
        f.write("-------------------\n")

        if issues["duplicate"]:
            f.write(f"Duplicate records: {issues['duplicate']}\n")
        if issues["order_id"]:
            f.write(f"Invalid order_id: {issues['order_id']}\n")
        if issues["order_date"]:
            f.write(f"Invalid order_date: {issues['order_date']}\n")
        if issues["customer_name"]:
            f.write(f"Invalid customer_name: {issues['customer_name']}\n")
        if issues["product"]:
            f.write(f"Invalid product: {issues['product']}\n")
        if issues["category"]:
            f.write(f"Invalid category: {issues['category']}\n")
        if issues["quantity"]:
            f.write(f"Invalid quantity: {issues['quantity']}\n")
        if issues["unit_price"]:
            f.write(f"Invalid unit_price: {issues['unit_price']}\n")
        if issues["country"]:
            f.write(f"Invalid country: {issues['country']}\n\n")

        f.write("\nSummary\n")
        f.write("-------------------\n")
        f.write(f"{cleaner.errors["order_id"].nunique()} records saved in issue file and need to check!\n")
        f.write(f"{count_error_records} records not considering for analysis\n")
        f.write(f"{total_orders - count_error_records} records are valid and considered for analysis\n\n")
        f.write(f"{format_currency(average_order_value)} average order value")
        print("Report generated successfully in output/sale_report.txt")


if __name__ == "__main__":
    main()
