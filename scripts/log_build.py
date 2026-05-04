import pandas as pd
from datetime import datetime
import os 

def log_build(status):
    os.makedirs("data", exist_ok=True)

    row = {
        "timestamp": datetime.now(),
        "status": status
    }

    file_path = "data/build_log.csv"

    df = pd.DataFrame([row])
    df.to_csv(file_path, mode="a", header=not os.path.exists(file_path), index=False)