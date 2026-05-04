import sys
sys.path.insert(0,'.')
import pandas as pd
from scripts.process_data import compute_kpis

def test_kpis():
    df = pd.DataFrame({

        "price":[10,20,30],
        "change_24hr": [1,2,3]
    })

    df.to_csv("data/test.csv", index=False)

    _, kpis = compute_kpis("data/test.csv")

    assert kpis["avg_price"] == 20
    assert kpis["max_price"] == 30
    assert kpis["min_price"] == 10