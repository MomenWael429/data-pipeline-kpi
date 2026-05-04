import matplotlib.pyplot as plt
import pandas as pd

def create_chart(df):
    df["timestamp:"] = pd.to_datetime(df["timestamp"])

    plt.figure()
    plt.plot(df["timestamp"], df["price"])
    plt.title("Bitcoin price over time")
    plt.xticks(rotation = 45)
    plt.tight_layout()
    plt.savefig("output/chart.png")