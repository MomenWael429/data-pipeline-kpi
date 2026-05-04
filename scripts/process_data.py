import pandas as pd
import json
import os

def compute_kpis(path = 'data/data.csv'):
    df = pd.read_csv(path)

    kpis = {
        "avg_price": float(df["price"].mean()),
        "max_price": float(df["price"].max()),
        "min_price": float(df["price"].min()),
        "lastest_change": float(df["change_24h"].iloc[-1])

    }

    return df, kpis

def save_kpis_json(kpis):
    os.makedirs("output", exist_ok=True)

    with open("output/kpis.json", "w") as f:
        json.dump(kpis, f, indent=4)