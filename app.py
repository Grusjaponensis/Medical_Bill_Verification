import streamlit as st
import pandas as pd

from normal_check import normal_check
from special_check import special_check

from custom_errors import CustomizedError, NoneFloatError

# Global variables
category: str = '品名'
price: str = '单价'
company: str = None
specifications: str = None

# UI
st.title('报表核对工具')

st.write("本工具用于核对报表中的单价数据是否与基准文件中的单价一致。")

st.divider()

is_special_mode_activated: bool = st.toggle(label='启用特殊模式', help='未启用时为正常检查模式，选择“特殊模式”将会检查规格与公司不同的报表')
if is_special_mode_activated:
    st.success("已启用特殊模式！")

uploaded_file_to_check = st.file_uploader("请上传待核对的Excel文件", type=["xlsx"], accept_multiple_files=False)
uploaded_file_base = st.file_uploader("请上传核对基准Excel文件", type=["xlsx"], accept_multiple_files=False)

if uploaded_file_base:
    df_base = pd.read_excel(uploaded_file_base)
    
    with st.expander('选择基准表中的列'):
        base_options = df_base.columns.tolist()
        if not is_special_mode_activated:
            selected_base = st.multiselect("请选择基准表中需要的列，“**名称**”列必选！", options=base_options)
        else:
            selected_base = st.multiselect("在特殊模式中，请选择基准表中**药品名称**、**规格**、**药品单价**、**生产企业名称**列，**必须按照此顺序！**", options=base_options)
            if selected_base:
                st.warning("**请注意选择顺序！**")
        df_base = df_base[selected_base]
        
        if selected_base and not is_special_mode_activated:
            if len(selected_base) < 2:
                st.error("**请至少选择2列**！")
            else:
                st.success("**已选择基准表中的列**：" + "，".join(selected_base))
        elif selected_base and is_special_mode_activated:
            if len(selected_base) < 4:
                st.error("**请至少选择4列**！")
            else:
                st.success("**已选择基准表中的列**：" + "，".join(selected_base))

    if uploaded_file_to_check:
        excel_file = pd.ExcelFile(uploaded_file_to_check)
        if "Sheet1" in excel_file.sheet_names:
            df_to_check = pd.read_excel(uploaded_file_to_check, header=(2 if is_special_mode_activated else 0), sheet_name='Sheet1')
            options: list[str] = df_to_check.columns.tolist()

            with st.expander('选择待核对表中的列'):
                uploaded_category = st.selectbox("请选择待核查文件中药品名所在的列名", options=options)
                if uploaded_category:
                    category = uploaded_category
                    st.success(f"**已更新品名列名为**：{category}")

                uploaded_price = st.selectbox("请选择待核查文件中购入单价所在的列名", options=options)
                if uploaded_price:
                    price = uploaded_price
                    st.success(f"**已更新购入单价列名为**：{price}")
                    
                if is_special_mode_activated:
                    uploaded_company = st.selectbox("请选择待核查文件中生产企业所在的列名", options=options)
                    if uploaded_company:
                        company = uploaded_company
                        st.success(f"**已更新生产企业列名为**：{company}")
                        
                    uploaded_specifications = st.selectbox("请选择待核查文件中规格所在的列名", options=options)
                    if uploaded_specifications:
                        specifications = uploaded_specifications
                        st.success(f"**已更新规格列名为**：{specifications}")

            if st.button('核对数据'):
                try:
                    if not is_special_mode_activated:
                        (df_need, df_base_need) = normal_check(df_to_check, df_base, category, price)
                    else:
                        (df_need, df_base_need) = special_check(df_to_check, df_base, category, price, company, specifications)
                except CustomizedError as e:
                    st.error(e)
                except NoneFloatError as e:
                    st.error(e)
                else:
                    st.success("核对无误！")
                    st.toast("核对完成！")
                    st.balloons()
                    
                    df_need['基准单价'] = df_need[category].map(df_base_need.set_index(df_base_need.columns[0]).iloc[:, 0])
                    
                    st.dataframe(df_need, height=500, width=700)
        else:
            st.error("**请确保待核查文件中有“Sheet1”页**！")
    else:
        st.write("使用说明：请上传待检查Excel文件")
else:
    st.divider()
    st.write("使用说明：请上传待检查Excel文件与基准Excel文件")
