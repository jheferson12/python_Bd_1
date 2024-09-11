import os
import streamlit as st
import pandas as pd
import mysql.connector
from mysql.connector import Error

def read_excel_file(file):
    
    try:
        return pd.read_excel(file)
    except Exception as e:
        st.error(f"Error reading the Excel file: {e}")
        return pd.DataFrame()

def load_and_show_excel_files(files):
    
    dataframes = []
    for file in files:
        st.write(f"*File:* {file.name}")
        df = read_excel_file(file)
        if not df.empty:
            st.write(df)
            dataframes.append(df)
        else:
            st.error(f"Error: The file {file.name} is empty or could not be read.")
    return dataframes

def combine_dataframes(dataframes):
    
    if len(dataframes) == 0:
        st.error("No DataFrames to combine.")
        return pd.DataFrame()
    
    try:
        combined_df = pd.concat(dataframes, ignore_index=True)
        return combined_df
    except Exception as e:
        st.error(f"Error combining the DataFrames: {e}")
        return pd.DataFrame()

def load_data_infile():
    
    try:
        connection = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME"),
            allow_local_infile=True  
        )
        
        if connection.is_connected():
            st.write("Connected to the database")
            cursor = connection.cursor()
            
            query = """
                LOAD DATA LOCAL INFILE 'C:\\xampp\\mysql\\data\\2024-09-10T19-00_export.csv'
                INTO TABLE uploadmenu
                FIELDS TERMINATED BY ','
                ENCLOSED BY '"'
                LINES TERMINATED BY '\\n'
                IGNORE 1 ROWS
                (CATEGORY, MENUITEM, DISHOFFERS, GENERALPRICE, ORDERCODE, PRICE);
            """            
            
            cursor.execute(query)
            connection.commit()
            
            rows_affected = cursor.rowcount
            st.success(f"Data loaded successfully. Rows affected: {rows_affected}")

            cursor.close()
            connection.close()

    except Error as e:
        st.error(f"Error connecting to database: {e}")

st.sidebar.title("Menu Options")
menu_option = st.sidebar.selectbox("Select Option", ["Upload Data", "Create Menu Restaurant"])

if menu_option == "Upload Data":
    st.title("Upload and Save Excel Data")
    uploaded_files = st.file_uploader("Drag and drop two Excel files", type=["xlsx"], accept_multiple_files=True, key="file_uploader_1")

    if uploaded_files:
        if len(uploaded_files) >= 2:
            dataframes = load_and_show_excel_files(uploaded_files)
            if len(dataframes) >= 2:
                if st.button("Combine Files"):
                    combined_df = combine_dataframes(dataframes)
                    st.write("Combined DataFrame:", combined_df)
                    st.button("Load Data to Database", on_click=load_data_infile)
