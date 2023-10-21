# This function presents a user-friendly, answer-based use for entire "Customer Segmentation Using RFM Analytics".
# Only works on current dataset structure.
import pandas as pd
import datetime as dt
pd.set_option("display.max_columns", 14)
pd.set_option("display.width", 500)

_df_ = pd.read_csv("data_20k.csv")
df = _df_.copy()

today_date = dt.datetime(2021, 6, 1)


def main_func(dataframe):
    """

    Parameters
    ----------
    dataframe: specify relevant dataframe.

    Returns
    Returns as three questions:
        1. Segment name
            (For a single segment, enter the segment name as is. For multiple segments, list the segment names separated by '|' (pipe character).)
        2. Category name
            (For a single category, enter the category name as is. For multiple categories, list the category names separated by '|' (pipe character).)
        3. CSV file name
    After answering these question, function will return as a .csv file that created by the answers.
    -------

    """
    def prep_data(dataframe):
        dataframe["omni_total_order"] = dataframe["order_num_total_ever_online"] + dataframe["order_num_total_ever_offline"]
        dataframe["omni_customer_value"] = dataframe["customer_value_total_ever_offline"] + dataframe[
            "customer_value_total_ever_online"]
        for col in dataframe.columns:
            if "date" in col:
                dataframe[col] = pd.to_datetime(dataframe[col])
        return rfm_creating(dataframe)
    def rfm_creating(dataframe):
        rfm = dataframe.groupby("master_id").agg(
            {"last_order_date": lambda date: (today_date - date.max()).days,
             "omni_total_order": lambda order: order,
             "omni_customer_value": lambda value: value})
        rfm.columns = ["recency", "frequency", "monetary"]
        return rfm_segment(rfm)
    def rfm_segment(rfm):
        rfm["recency_score"] = pd.qcut(rfm["recency"], 5, labels=[5, 4, 3, 2, 1])
        rfm["frequency_score"] = pd.qcut(rfm["frequency"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5])
        rfm["RF_score"] = (rfm["recency_score"].astype(str) + rfm["frequency_score"].astype(str))
        rfm.reset_index(inplace=True)

        seg_map = {
            r"[1-2][1-2]": "hibernating",
            r"[1-2][3-4]": "at_risk",
            r"[1-2]5": "cant_loose",
            r"3[1-2]": "about_to_sleep",
            r"33": "need_attention",
            r"[3-4][4-5]": "loyal_customers",
            r"41": "promising",
            r"51": "new_customers",
            r"[4-5][2-3]": "potential_loyalists",
            r"5[4-5]": "champions"
        }
        rfm["Segment"] = rfm["RF_score"].replace(seg_map, regex=True)
        return RFM_output(rfm, dataframe)
    def RFM_output(rfm, dataframe):
        segments = input("Segment name (eg. cant_loose or cant_loose|hibernating|new_customers)")
        categories = input("Category name (eg. KADIN or COCUK|ERKEK)")
        dataframe_1 = dataframe[dataframe["interested_in_categories_12"].str.contains(f"{categories}")][
            ["master_id", "interested_in_categories_12"]]
        rfm_1 = rfm[rfm["Segment"].str.contains(f"{segments}")][["master_id", "Segment"]]
        new_customers = dataframe_1.merge(rfm_1, on="master_id", how="inner")
        file_name = input("Under what name should the file be saved?")
        new_customers.to_csv(f"{file_name}")
        return print(f"Your file named {file_name} has been created and saved.")
    return prep_data(dataframe)



