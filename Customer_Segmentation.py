# Customer Segmentation using RFM Analytics

# The data set consists of information obtained from the past shopping behavior of customers who made their last purchases
# via OmniChannel (both online and offline shopping) in 2020 - 2021. #
# 12 variables, 19.945 observations

# master_id: Unique customer id
# order_channel: Channel of the shopping platform where the shopping was made (Android, iOS, Desktop, Mobile)
# last_order_channel: Channel where the last shopping was made.
# first_order_date: The date of the customer's initial purchase.
# last_order_date: The date of the customer's most recent purchase.
# last_order_date_online: The date of the customer's most recent online purchase.
# last_order_date_offline: The date of the customer's most recent offline purchase.
# order_num_total_ever_online: The total number of purchases the customer has made on online platforms.
# order_num_total_ever_offline: The total number of purchases the customer has made on offline platforms.
# customer_value_total_ever_offline: The total amount the customer has spent on offline purchases.
# customer_value_total_ever_online: The total amount the customer has spent on online purchases.
# interested_in_categories_12: The list of categories in which the customer has made purchases in the last 12 months.

####################################################
### Task 1: Understanding and Preparing the Data ###
####################################################

# Step 1: Reading the dataset, necessary libraries and options

import datetime as dt
import pandas as pd
pd.set_option("display.max_columns", 14)
pd.set_option('display.width', 99)
pd.set_option("display.float_format", lambda x: "%.3f" % x)

_df_ = pd.read_csv("data_20k.csv")
df = _df_.copy()

# Step 2: Understanding the dataset

df.head()
df.shape
df.dtypes
df.columns
df.describe().T
df.isnull().sum()

# Step 3: Creating new variables in the dataset for using Omnichannel for shopping. This way we will be able
# to sum and evalute the customers both online and offline recency and frequency values together.#

df["omni_customer_value"] = df["customer_value_total_ever_online"] + df["customer_value_total_ever_offline"]
df["omni_total_order"] = df["order_num_total_ever_online"] + df["order_num_total_ever_offline"]
df.head()


# Step 4: Examination of variable types and converting variables that represent dates to the type datetime.

df.dtypes

for col in df.columns:
    if "date" in col:
        df[col] = pd.to_datetime(df[col])

df.dtypes


# Step 5.1: Evaluating the distribution of customer count, total product purchased, and total spending across online shopping channels.

df.groupby("order_channel").agg({"master_id": lambda master_id: master_id.nunique(),
                                 "order_num_total_ever_online": lambda order_num_total_ever_online: order_num_total_ever_online.sum(),
                                 "customer_value_total_ever_online": lambda customer_value_total_ever_online: customer_value_total_ever_online.sum()})


# Step 5.2: Evaluating the distribution of customer count, total product purchased, and total spending across all (online + offline) shopping channels.

df.groupby("order_channel").agg({"master_id": lambda master_id: master_id.nunique(),
                                 "omni_total_order": lambda omni_total_order: omni_total_order.sum(),
                                 "omni_customer_value": lambda omni_customer_value: omni_customer_value.sum()})


# Step 6: Listing the top 10 customers with the highest revenue.

df_top_ten_value = df.sort_values(by='omni_customer_value', ascending=False).head(10)


# Step 7: List the top 10 customers with the most orders.

df_top_ten_order = df.sort_values(by="omni_total_order", ascending=False).head(10)


# Step 8: Functionize the data preparation process.

def data_preparation(dataframe):
    dataframe["omni_customer_value"] = dataframe["customer_value_total_ever_online"] + dataframe["customer_value_total_ever_offline"]
    dataframe["omni_total_order"] = dataframe["order_num_total_ever_online"] + dataframe["order_num_total_ever_offline"]
    for col in dataframe.columns:
        if "date" in col:
            df[col] = pd.to_datetime(dataframe[col])
    return dataframe

data_preparation(df) # to call it.


#######################################
### Task 2: Calculating RFM Metrics ###
#######################################


# Step 1: Recency, Frequency, and Monetary definitions.

# Recency: Represents the time difference between the customer's last purchase date and the analysis date.
# Frequency: Indicates the total number of purchases made by the customer, representing the frequency of purchases.
# Monetary: The total revenue generated by the customer for the company.


# Step 2: Calculate the Recency, Frequency, and Monetary metrics on a customer-specific basis.
# We use list comprehension for columns that represent date and define it as "date_var".
# "df[date_var].max()" will result as max values of these variables and "df[date_var].max().max()" will result as max value of these max values.#

date_var = [col for col in df.columns if 'date' in col]
df[date_var].max().max()
today_date = dt.datetime(2021, 6, 1)

rfm = df.groupby("master_id").agg({"last_order_date": lambda last_order_date: (today_date - last_order_date.max()).days,
                             "omni_total_order": lambda omni_total_order: omni_total_order,
                             "omni_customer_value": lambda omni_customer_value: omni_customer_value})


# Step 3: Changing the names of the metrics we've created to recency, frequency, and monetary.

rfm.columns = ["recency", "frequency", "monetary"]
rfm.head()


########################################
### Task 3: Calculating the RF Score ###
########################################

# rank(method="first"): The "method="first"" expression is used to capture the first value in frequency.
# We are dividing the recency and frequency variables into 5 segments and labeling them from 1 to 5.
# For recency, smaller values are better, and since the qcut() function sorts values from lower to higher, we label the group with the lowest recency as 5,
# and the second-lowest group as 4, down to 1 for the highest recency.
# For frequency, higher values are better, and due to how the qcut() function works, we label the group with the lowest frequency as 1,
# and the second-lowest as 2, up to 5 for the highest frequency group.


rfm["recency_score"] = pd.qcut(rfm["recency"], 5, labels=[5, 4, 3, 2, 1])
rfm["frequency_score"] = pd.qcut(rfm["frequency"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5])
rfm["RF_score"] = (rfm["recency_score"].astype(str) + rfm["frequency_score"].astype(str))
rfm.reset_index(inplace=True)
rfm.head()


########################################################
### Task 4: Defining the RF Score as Segments ###
########################################################
# "REGEX" stands for "Regular expression",  The "-" within "[-]" represents the "or" expression.
# REGEX and RFM Naming

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
rfm.head()


###################################
### Task 5: RFM Use In Practice ###
###################################

# Step 1: Examine and evaluate the averages of recency, frequency, and monetary for the segments.

rfm[["Segment", "recency", "frequency", "monetary"]].groupby("Segment").agg(["mean", "count"])


# Step 2: Using RFM analysis, find the relevant profiled customers for the following 2 cases and save their customer IDs as a CSV.

# a. FLO is introducing a new women's shoe brand. The prices of this brand's products are above the general customer preferences.
# Therefore, they want to establish special communication with customers who are interested in promoting the brand and sales.
# The customers for special communication will include loyal customers (champions, loyal_customers) and those within the shopping category,
# including the women's category. Save the customer IDs of these customers to a CSV file.

rfm1 = rfm[rfm["Segment"].str.contains("champions|loyal_customers")][["master_id", "Segment"]]
df1 = df[df["interested_in_categories_12"].str.contains("KADIN", na=False)][["master_id", "interested_in_categories_12"]]
cus_for_new_brand = rfm1.merge(df1, on="master_id", how="inner")
cus_for_new_brand.head()
cus_for_new_brand.to_csv("cus_for_new_brand")


# "b. A discount of nearly 40% is planned for men's and children's products.
# Customers who have shown interest in these categories in the past but haven't shopped for a long time,
# as well as customers who are considered 'at risk' (sleeping), and new customers,
# are being targeted for this discount. Save the customer IDs of the appropriate profiled customers to a CSV file. #

rfm2 = rfm[rfm["Segment"].str.contains("cant_loose|hibernating|new_customers")][["master_id", "Segment"]]
df2 = df[(df["interested_in_categories_12"].str.contains("ERKEK|COCUK", na=False))][["master_id", "interested_in_categories_12"]]
cus_for_new_brand2 = rfm2.merge(df2, on="master_id", how="inner")
cus_for_new_brand2.head()
cus_for_new_brand2.to_csv("cus_for_new_brand2")