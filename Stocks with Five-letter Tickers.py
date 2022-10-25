import pandas as pd
import yfinance as yf
import requests
import json
import config


def get_selected_symbols(row):
    """return rows with symbol length >=5, excluding common stocks like "BRK.B", warrants, units, etc"""
    if(((len(row["symbol"])) >= 5) & ("." not in row["symbol"])):
        # not warrants, tradable rights, units, preferred shares
        if(row["type"] not in ["wt", "rt", "ut", "ps"]):
            return row
    return pd.Series(index=row.index, dtype=pd.StringDtype())


try:
    json_data = json.load(open("./data/symbols.json"))
except:
    json_data = requests.get(
        "https://workspace.iex.cloud/v1/ref-data/symbols?token="+config.iex_token).json()
    with open('./data/symbols.json', 'w') as file:
        file.write(json.dumps(json_data))

data = pd.DataFrame(json_data).apply(
    get_selected_symbols, axis=1).dropna(subset=["symbol"])
data["Market Cap"] = [0] * len(data)


for index, row in data.iterrows():
    ticker = yf.Ticker(row["symbol"])
    if("marketCap" in ticker.info):
        data.at[index, "Market Cap"] = ticker.info["marketCap"]
        print(data.loc[[index]])

print(data)
data.to_csv("./output.csv")
