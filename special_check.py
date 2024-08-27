import pandas as pd
import re
from fuzzywuzzy import fuzz, process
import streamlit as st

from custom_errors import CustomizedError, NoneFloatError

# Fuzzy matching function
def fuzzy_match(name: str, choice: list[str], threshold: int = 60):
    matches = process.extract(name, choice, scorer=fuzz.token_sort_ratio)
    return [match for match in matches if match[1] >= threshold]

def make_unique(l: list) -> list:
    seen = set()
    return [x for x in l if not (x in seen or seen.add(x))]

# Main function
def special_check(df_to_check: pd.DataFrame, df_base: pd.DataFrame, 
                  category: str, price: str, company: str, specifications: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    # Preprocess data
    df_to_check = df_to_check.dropna(subset=[category, price, company, specifications])
    
    delete_columns = df_to_check[df_to_check[price].apply(lambda x: not isinstance(x, (int, float)))]
    
    df_to_check.loc[:, specifications] = df_to_check[specifications].apply(lambda x: str(x).replace('千克', 'kg').replace('克', 'g').replace('/袋', ''))
    
    if len(delete_columns) > 0:
        warning_message = "**处理数据过程中，被删除的行是**：\n\n"
        temp = ' | '
        for index, row in delete_columns.iterrows():
            warning_message += f"行 {index}: {temp.join([str(item) for item in row.to_list()])}\n\n"
        st.warning(warning_message)

    df_to_check = df_to_check.drop(delete_columns.index)
    
    # df_need is the data to be checked
    df_need = df_to_check[[category, price, company, specifications]]
    
    # df_base_need is the base data
    df_base_need = df_base
    
    if len(df_base.columns) < 2:
        raise CustomizedError("基准文件至少需要两行数据，请检查基准文件选择的列是否正确")
    
    if len(df_need) == 0:
        raise CustomizedError("待核查文件中无有效数据，请检查已选择的列是否正确")

    # replace all parentheses with empty string and strip
    pattern = re.compile(r'[\(\)（）]')
    df_need.loc[:, category] = df_need[category].apply(lambda x: pattern.sub('', x).strip())
    # 0 - category, 1 - specification, 2 - price, 3 - company
    df_base_need.iloc[:, 0] = df_base_need.iloc[:, 0].apply(lambda x: pattern.sub('', x).strip())

    errors: list[str] = []

    name_list = df_need[category].tolist()
    name_base_list = df_base_need.iloc[:, 0].tolist()
    
    for index in range(len(name_list)):
        name = name_list[index]
        if name not in name_base_list:
            similar_names = [s for s, _ in make_unique(fuzzy_match(name, name_base_list))]
            errors.append(f"**{name}** 不存在于基准文件中，最相近的是：{'、'.join(similar_names)}\n")
        else:
            # filtered_df is data with same name, specification and company
            filtered_df = df_base_need[
                (df_base_need.iloc[:, 0] == name) &
                (df_base_need.iloc[:, 1] == df_need[specifications][index]) & 
                (df_base_need.iloc[:, 3] == df_need[company][index])
            ]
            if filtered_df.empty:
                similar_names = [s for s, _ in make_unique(fuzzy_match(name, name_base_list))]
                similar_names_with_diff_spec: pd.DataFrame = df_base_need[df_base_need.iloc[:, 0].isin(similar_names)]
                content_to_display = ""
                for _, row in similar_names_with_diff_spec.iterrows():
                    content_to_display += f"\t[名称：{row[0]}，规格：{row[1]}/袋，单价：{row[2]}，生产企业：{row[3]}]\n\n"
                errors.append(f"**[名称：{name}，规格：{df_need[specifications][index]}/袋，单价：{df_need[price][index]}，生产企业：{df_need[company][index]}]** 在基准文件中不存在，\
                    最相近的是：\n\n{content_to_display}\n\n")
            elif len(filtered_df) > 1:
                errors.append(f"**[名称：{name}，规格：{df_need[specifications][index]}/袋，生产企业：{df_need[company][index]}]** 在基准文件中存在多个匹配项，请检查数据\n")
            elif not isinstance(filtered_df.iloc[0, 2], (int, float)):
                    raise NoneFloatError(f"**{name}** 在基准文件中的价格不是可识别的数字，请检查相应数据\n")
            else:
                base_price = float(filtered_df.iloc[0, 2])
                if abs(base_price - df_need[price][index]) >= 0.0001:
                    errors.append(f"**[单价：{name}，规格：{df_need[specifications][index]}，生产企业：{df_need[company][index]}]** 的单价与基准文件不符，\
                                  基准文件中为 **{base_price:.3f}**，实际为 **{df_need[price][index]:.3f}**.\n")
    
    if errors:
        raise CustomizedError("**检测到以下错误**:\n\n" + "\n".join(errors))
    
    return df_need, df_base_need