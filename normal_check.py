import pandas as pd
import streamlit as st

from custom_errors import *

def normal_check(df_to_check: pd.DataFrame, df_base: pd.DataFrame, category: str, price: str):
    df_to_check = df_to_check.dropna(subset=[category, price])
    
    delete_columns = df_to_check[df_to_check[price].apply(lambda x: not isinstance(x, (int, float)))]
    
    if len(delete_columns) > 0:
        warning_message = "**处理数据过程中，被删除的行是**：\n\n"
        temp = ' | '
        for index, row in delete_columns.iterrows():
            warning_message += f"行 {index}: {temp.join([str(item) for item in row.to_list()])}\n\n"
        st.warning(warning_message)

    df_to_check = df_to_check.drop(delete_columns.index)
    df_need = df_to_check[[category, price]]

    if len(df_base.columns) < 2:
        raise CustomizedError("基准文件至少需要两行数据，请检查基准文件选择的列是否正确")
    
    if len(df_need) == 0:
        raise CustomizedError("待核查文件中无有效数据，请检查已选择的列是否正确")
    
    df_base_need = df_base
    name_list = [] # name_list is from base file
    name_list_p = df_base_need.iloc[:, 0].tolist()
    for name in name_list_p:
        name = str(name).strip()
        name_list.append(name)
    del name_list_p
    
    errors = []
    
    for i in range(len(df_need)):
        name = str(df_need.iloc[i][category]).strip()   # name in check file
        value = df_need.iloc[i, 1]                      # value in check file
        if name not in name_list:
            errors.append(f"**{name}** 不存在于基准文件中\n")
        else:
            base_value = df_base_need[df_base_need[df_base_need.columns[0]] == name].iloc[0, 1]
            if not isinstance(base_value, (int, float)):
                raise NoneFloatError(f"基准文件中 **{name}** 的单价不是数字，请检查该行数据")
            
            if abs(value - base_value) >= 0.0001:
                errors.append(f"**{name}** 的单价与基准文件不符，基准文件中为 **{base_value:.3f}**，实际为 **{value:.3f}**.\n")

    if errors:
        raise CustomizedError("**检测到以下错误**:\n\n" + "\n".join(errors))

    return df_need, df_base_need
