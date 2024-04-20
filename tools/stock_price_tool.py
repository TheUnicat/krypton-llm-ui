import requests
import csv
from io import StringIO
import json

with open("krypton_storage/secrets.json", "r") as file:
    secrets = json.load(file)
    alpha_vantage_key = secrets["alpha_vantage"]

def stock_price(args):
    symbol = args["ticker"]
    try:
        url = "https://www.alphavantage.co/query"
        params = {
            "function": "TIME_SERIES_INTRADAY",
            "symbol": symbol,
            "interval": "5min",
            "apikey": alpha_vantage_key,
            "datatype": "csv",
            "outputsize": "compact"
        }
        response = requests.get(url, params=params)

        if response.status_code == 200:
            csv_file = StringIO(response.text)
            csv_reader = csv.reader(csv_file)
            next(csv_reader)  # Skip the header row
            latest_data = next(csv_reader)  # Get the most recent data row

            # Assuming close price is the fourth column
            close_price = latest_data[3]
            yield json.dumps({
                "result": str(close_price),
                "done": True
            })
        else:
            yield json.dumps({
                "result": f"An error occurred while fetching the stock price. {str(response.status_code)}",
                "done": True
            })

    except Exception as e:
        return f"An error occurred: {str(e)}"