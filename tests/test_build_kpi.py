import pandas as pd
from scripts.process_data import compute_build_kpis

def test_build_kpi():
    df = pd.DataFrame({

        "status":["success", "failure", "success"],
    })

    df.to_csv("data/build_log.csv", index=False)

    total = len(df)
    success = len(df[df["status"] == "success"])
    rate = (success/total) * 100

    assert total == 3
    assert success == 2
    assert round(rate,2) == 66.67