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
        df = read_excel_file(file)
        if not df.empty:
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
    
    connection = None
    cursor = None

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
                LOAD DATA LOCAL INFILE 'C:/path/to/your/file/2024-09-09T19-15_export.csv'
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

    except Error as e:
        st.error(f"Error connecting to database: {e}")

    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()


st.title("Upload for Save Excel in plattform")


file_paths = ["restauranttable_large.xlsx", "restaurant_table_bd2_large.xlsx"]


dataframes = load_and_show_excel_files(file_paths)
combined_df = combine_dataframes(dataframes)


if not combined_df.empty:
    st.write("Combined DataFrame:", combined_df)
    if st.button("Load Data to Database"):
        load_data_infile()
else:
    st.write("No data to display or save.")













