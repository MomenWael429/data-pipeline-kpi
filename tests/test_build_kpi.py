import sys
sys.path.insert(0,'.')

import pandas as pd
from scripts.process_data import compute_build_kpis

def test_build_kpi():
    df = pd.DataFrame({

        "status":["success", "failure", "success"],
    })

    df.to_csv("data/build_log.csv", index=False)

    total = len(df)
    success = len(df[df["status"] == "success"])
    rate = compute_build_kpis("data/build_log.csv")

    assert total == 3
    assert success == 2
    assert round(rate,2) == 66.67