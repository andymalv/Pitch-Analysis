from biomechanics_analysis import get_data, get_metrics, save_as_parquet
from resample import resample_data


# %%
def main():
    df = get_data("landmarks.csv")
    df = get_metrics(df)
    resampled_df = resample_data(df)
    save_as_parquet(df, "raw")
    save_as_parquet(resampled_df, "resampled")


if __name__ == "__main__":
    main()
