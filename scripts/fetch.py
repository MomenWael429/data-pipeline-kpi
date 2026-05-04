import requests 
import pandas as pd
from datetime import datetime
import os

def fetch_data():
    url = "https://api.coingecko.com/api/v3/simple/price"

    params= {
        "ids": "bitcoin",
        "vs_currencies": "eur",
        "include_24hr_change": "true",
    }

    response = requests.get(url, params=params)

    if response.status_code != 200:
        raise Exception(f"API Error: status code: {response.status_code}, {response.text}")
    
    data = response.json()
    print(f"API Response: {data}")

    bitcoin_data = data.get("bitcoin", {})
    price = bitcoin_data.get("eur", 0)
    change_24h = bitcoin_data.get("eur_24h_change", 0)


    row = {
        "timestamp": datetime.now(),
        "price": price,  # Use the price, not the change
        "price_eur": price,  # You might want both
        "change_24h": change_24h  # Store the 24h change separately
    }

    

    os.makedirs("data", exist_ok= True)
    file_path = "data/data.csv"

    df =pd.DataFrame([row])
    df.to_csv(file_path, mode='a', header=not os.path.exists(file_path),index = False)
    return df

