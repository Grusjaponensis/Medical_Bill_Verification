import streamlit as st
import pandas as pd

def check(df_to_check: pd.DataFrame, df_base: pd.DataFrame):
    if '品名' not in df_to_check.columns:
        raise TypeError("\'品名\'列不存在，请检查数据格式或列名有无额外字符")
    df_to_check = df_to_check.dropna(subset=['品名'])
    
    if '编号' not in df_to_check.columns:
        raise TypeError("\'编号\'列不存在，请检查数据格式或列名有无额外字符")
    delete_columns = df_to_check[df_to_check['编号'] == '编号']
    
    df_to_check = df_to_check.drop(delete_columns.index)
    if df_to_check.shape[1] < 6:
        raise TypeError("待核查文件列数不正确，请保证‘品名’位于第2列， ‘购入单价（元/kg）’位于第6列。请检查数据格式")
    df_need = df_to_check[df_to_check.columns[[1, 5]]]
    
    if df_base.shape[1] < 4:
        raise TypeError("基准文件列数不正确，请检查数据格式")
    df_base_need = df_base.iloc[:, 1:3]
    name_list = []
    name_list_p = df_base_need.iloc[:, 0].tolist()
    for name in name_list_p:
        name = name.strip()
        name_list.append(name)
    del name_list_p
    
    errors = []

    for i in range(len(df_need)):
        name = df_need.iloc[i]['品名']
        value = df_need.iloc[i, 1]
        if name not in name_list:
            errors.append(f"[{name}] 不存在于基准文件中")
        else:
            base_value = df_base_need[df_base_need[df_base_need.columns[0]] == name].iloc[0, 1]
            if abs(value - base_value) >= 0.001:
                errors.append(f"[{name}] 的单价与基准文件不符，基准文件中为 [{base_value}]，实际为 [{value}].\n")

    if errors:
        raise ValueError("检测到以下错误:\n\n" + "\n".join(errors))

    return df_need, df_base_need

st.title('报表核对工具')

uploaded_file_to_check = st.file_uploader("请上传待核对的Excel文件", type=["xlsx", "xls"], accept_multiple_files=False)
uploaded_file_base = st.file_uploader("请上传核对基准Excel文件", type=["xlsx", "xls"])

if uploaded_file_to_check and uploaded_file_base:
    df_to_check = pd.read_excel(uploaded_file_to_check, sheet_name='Sheet1', header=2)
    df_base = pd.read_excel(uploaded_file_base)

    if st.button('核对数据'):
        try:
            (df_need, df_base_need) = check(df_to_check, df_base)
        except ValueError as e:
            st.error(e)
        except TypeError as e:
            st.error(e)
        else:
            st.success("核对成功！")
            base_list = []
            for i in range(len(df_need)):
                name = df_need.iloc[i]['品名']
                base_list.append(df_base_need[df_base_need[df_base_need.columns[0]] == name].iloc[0, 1])
            df_need['基准单价'] = base_list
            st.dataframe(df_need, height=500, width=700)
else:
    st.write("使用说明：请上传待检查Excel文件与基准Excel文件")
