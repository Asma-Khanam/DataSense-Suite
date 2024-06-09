import streamlit as st
import pandas as pd
import plotly.express as px
import base64
from io import StringIO, BytesIO

def generate_excel_download_link(df):
    towrite = BytesIO()
    df.to_excel(towrite, index=False, header=True)
    towrite.seek(0)
    b64 = base64.b64encode(towrite.read()).decode()
    href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="data_download.xlsx">Download Excel File</a>'
    return st.markdown(href, unsafe_allow_html=True)

def generate_html_download_link(fig):
    towrite = StringIO()
    fig.write_html(towrite, include_plotlyjs="cdn")
    towrite = BytesIO(towrite.getvalue().encode())
    b64 = base64.b64encode(towrite.read()).decode()
    href = f'<a href="data:text/html;charset=utf-8;base64, {b64}" download="plot.html">Download Plot</a>'
    return st.markdown(href, unsafe_allow_html=True)

def check_abnormal_values(df, column, lower_limit, upper_limit):
    # Convert column values to numeric
    df[column] = pd.to_numeric(df[column], errors='coerce')

    # Filter abnormal values
    abnormal_values = df[(df[column] < lower_limit) | (df[column] > upper_limit)]

    return abnormal_values

st.set_page_config(page_title='Excel Plotter')
st.title('Excel Plotter 📈')
st.subheader('Upload your Excel file')

uploaded_file = st.file_uploader('Choose a file', type=['xlsx','csv'])
if uploaded_file:
    st.markdown('---')

    # Read DataFrame based on file type
    if uploaded_file.type == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
        df = pd.read_excel(uploaded_file, engine='openpyxl')
    elif uploaded_file.type == 'text/csv':
        df = pd.read_csv(uploaded_file)

    st.dataframe(df)

    st.subheader('Select columns for analysis:')
    selected_columns = st.multiselect('Choose columns', df.columns)

    if selected_columns:
        st.subheader('Group data by:')
        groupby_column = st.selectbox('Select a column for grouping', df.columns)

        # GROUP DATAFRAME
        df_grouped = df.groupby(by=[groupby_column], as_index=False)[selected_columns].sum()

        # Initialize fig variable
        fig = None

        # Create various types of visualizations
        plot_types = ['Bar Chart', 'Line Chart', 'Area Chart', 'Scatter Plot', 'Pie Chart']
        selected_plot_type = st.selectbox('Select a plot type', plot_types)

        if selected_plot_type == 'Bar Chart':
            fig = px.bar(df_grouped, x=groupby_column, y=selected_columns, color=selected_columns[0])
        elif selected_plot_type == 'Line Chart':
            fig = px.line(df_grouped, x=groupby_column, y=selected_columns, color=selected_columns[0])
        elif selected_plot_type == 'Area Chart':
            fig = px.area(df_grouped, x=groupby_column, y=selected_columns, color=selected_columns[0])
        elif selected_plot_type == 'Scatter Plot':
            fig = px.scatter(df_grouped, x=groupby_column, y=selected_columns, color=selected_columns[0])
        elif selected_plot_type == 'Pie Chart':
            fig = px.pie(df_grouped, values=selected_columns[0], names=groupby_column)

        if fig is not None:
            st.plotly_chart(fig)

    # Download links
    generate_excel_download_link(df)
    if fig is not None:
        generate_html_download_link(fig)
