import streamlit as st
import pandas as pd

category = '品名'
price = '单价'

def check(df_to_check: pd.DataFrame, df_base: pd.DataFrame):
    global category, price
    if category not in df_to_check.columns:
        raise TypeError(f"\'{category}\'列不存在，请检查待核查文件的数据格式或检查列名有无额外字符")
    df_to_check = df_to_check.dropna(subset=[category])
    
    if price not in df_to_check.columns:
        raise TypeError(f"\'{price}\'列不存在，请检查待核查文件的数据格式或检查列名有无额外字符")
    
    delete_columns = df_to_check[df_to_check[price].apply(lambda x: not isinstance(x, (int, float)))]
    df_to_check = df_to_check.drop(delete_columns.index)
    df_need = df_to_check[[category, price]]
    
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
            errors.append(f"[{name}] 不存在于基准文件中\n")
        else:
            base_value = df_base_need[df_base_need[df_base_need.columns[0]] == name].iloc[0, 1]
            if abs(value - base_value) >= 0.001:
                errors.append(f"[{name}] 的单价与基准文件不符，基准文件中为 [{base_value}]，实际为 [{value}].\n")

    if errors:
        raise ValueError("检测到以下错误:\n\n" + "\n".join(errors))

    return df_need, df_base_need

st.title('报表核对工具')

st.write("本工具用于核对报表中的单价数据是否与基准文件中的单价一致。")

uploaded_file_to_check = st.file_uploader("请上传待核对的Excel文件", type=["xlsx", "xls"], accept_multiple_files=False)
uploaded_file_base = st.file_uploader("请上传核对基准Excel文件", type=["xlsx", "xls"])

if uploaded_file_to_check and uploaded_file_base:
    with st.expander('更新列名'):
        uploaded_category = st.text_input("请输入药品名所在的列名（如不输入，则默认为'品名'）")
        if uploaded_category:
            category = uploaded_category
            st.success(f"已更新品名列名为：{category}")

        uploaded_price = st.text_input("请输入购入单价所在的列名（如不输入，则默认为'购入单价'）")
        if uploaded_price:
            price = uploaded_price
            st.success(f"已更新购入单价列名为：{price}")

    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="当前品名列名", value=category)
    with col2:
        st.metric(label="当前购入单价列名", value=price)

    df_to_check = pd.read_excel(uploaded_file_to_check, sheet_name='Sheet1')
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
