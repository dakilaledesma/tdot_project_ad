import pandas as pd
from collections import defaultdict

option_df = pd.read_excel("../apps/processing/data/ResearchProjectSpreadsheet.xlsx", sheet_name="DesignConsiderations")
# print(option_df.columns)
# main_categories = option_df["Unnamed: 0"][3:].dropna().tolist()
# subcategories = option_df["Subcategory"][3:].dropna().tolist()
# print(main_categories)
# print(subcategories)

categories_df = option_df[["Unnamed: 0", "Subcategory"]][3:]
categories = []
subcategories = []

category_dict = defaultdict(dict)
curr_category = None
for index, row in categories_df.iterrows():
    category = row["Unnamed: 0"]
    subcategory = row["Subcategory"]
    if category != curr_category and str(category) != "nan":
        curr_category = category

    if str(subcategory) != "nan":
        category_dict[curr_category][subcategory] = index
    else:
        category_dict[curr_category][category] = index

print(category_dict)

for col in option_df.columns[2:]:
    col_header = [v for v in option_df[col][:3] if str(v) != "nan"]
    print(col_header)
    print(option_df[col][category_dict["Bioretention"]["Bioswales"]])


