from scripts.fetch import fetch_data
from scripts.process_data import compute_kpis, save_kpis_json
from scripts.visualize import create_chart
from scripts.log_build import log_build
import os
def run_pipeline():
    print("main started")
    os.makedirs("output", exist_ok=True)
    print("output dir is there")

    try:
        print("Step 1: fetch")
        fetch_data()
        print("step 2: compute kpis")
        df, kpis = compute_kpis()
        print("step 3: chart in output")
        create_chart(df)
        print("step 4: json file")
        save_kpis_json(kpis)
        print("step 5: logs .....")
        log_build("success")
    except Exception as e:
        log_build("failure")
        raise e
    
if __name__ == "__main__":
    print("....")
    run_pipeline()