import streamlit as st
import pandas as pd

category = '品名'
price = '单价'

class CustomizedError(Exception):
    def __init__(self, message):
        self.message = message


class NoneFloatError(Exception):
    def __init__(self, message):
        self.message = message


def check(df_to_check: pd.DataFrame, df_base: pd.DataFrame):
    global category, price
    if category not in df_to_check.columns:
        raise CustomizedError(f"\'{category}\'列不存在，请检查待核查文件的数据格式或检查列名有无额外字符")
    df_to_check = df_to_check.dropna(subset=[category])
    
    if price not in df_to_check.columns:
        raise CustomizedError(f"\'{price}\'列不存在，请检查待核查文件的数据格式或检查列名有无额外字符")
    
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

# UI

st.title('报表核对工具')

st.write("本工具用于核对报表中的单价数据是否与基准文件中的单价一致。")

uploaded_file_to_check = st.file_uploader("请上传待核对的Excel文件", type=["xlsx", "xls"], accept_multiple_files=False)
uploaded_file_base = st.file_uploader("请上传核对基准Excel文件", type=["xlsx", "xls"])

if uploaded_file_base:
    df_base = pd.read_excel(uploaded_file_base)
    
    with st.expander('选择基准表中的列'):
        base_options = df_base.columns.tolist()
        selected_base = st.multiselect("请选择基准表中需要的列，“**名称**”列必选！", options=base_options)
        df_base = df_base[selected_base]
        if selected_base:
            if len(selected_base) < 2:
                st.error("**请至少选择2列**！")
            else:
                st.success("**已选择基准表中的列**：" + "，".join(selected_base))

    if uploaded_file_to_check:
        excel_file = pd.ExcelFile(uploaded_file_to_check)
        if "Sheet1" in excel_file.sheet_names:
            df_to_check = pd.read_excel(uploaded_file_to_check, sheet_name='Sheet1')

            with st.expander('选择待核对表中的列'):
                category_options = df_to_check.columns.tolist()
                uploaded_category = st.selectbox("请选择待核查文件中药品名所在的列名", options=category_options)
                if uploaded_category:
                    category = uploaded_category
                    st.success(f"**已更新品名列名为**：{category}")

                price_options = df_to_check.columns.tolist()
                uploaded_price = st.selectbox("请选择待核查文件中购入单价所在的列名", options=price_options)
                if uploaded_price:
                    price = uploaded_price
                    st.success(f"**已更新购入单价列名为**：{price}")

            if st.button('核对数据'):
                try:
                    (df_need, df_base_need) = check(df_to_check, df_base)
                except CustomizedError as e:
                    st.error(e)
                except NoneFloatError as e:
                    st.error(e)
                else:
                    st.success("核对无误！")
                    st.toast("核对完成！")
                    st.balloons()
                    base_list = []
                    for i in range(len(df_need)):
                        name = df_need.iloc[i][category]
                        base_list.append(df_base_need[df_base_need[df_base_need.columns[0]] == name].iloc[0, 1])
                    df_need['基准单价'] = base_list
                    st.dataframe(df_need, height=500, width=700)
        else:
            st.error("**请确保待核查文件中有“Sheet1”页**！")
    else:
        st.write("使用说明：请上传待检查Excel文件")
else:
    st.write("使用说明：请上传待检查Excel文件与基准Excel文件")
