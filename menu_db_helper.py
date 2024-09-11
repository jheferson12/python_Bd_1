import os
import streamlit as st
import pandas as pd
import mysql.connector
from mysql.connector import Error


def extract_combined_data_from_excel(files):
    
    try:
        dfs = [pd.read_excel(file) for file in files]
        
        
        all_columns = set()
        for df in dfs:
            all_columns.update(df.columns)
        
        
        for i in range(len(dfs)):
            for column in all_columns:
                if column not in dfs[i].columns:
                    dfs[i][column] = pd.NA
        
        combined_df = pd.concat(dfs, ignore_index=True)
        return combined_df
    except Exception as e:
        st.error(f"Error reading the Excel files: {e}")
        return pd.DataFrame()  


def insert_data_to_db(df):
    
    try:
        connection = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
        if connection.is_connected():
            cursor = connection.cursor()
            
            
            query = """
            INSERT INTO uploadmenu (CATEGORY, MENUITEM, DISHOFFERS, GENERALPRICE, ORDERCODE, HOUSEADRESS, PRICE)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            
            
            data = [
                (
                    row.get('CATEGORY', pd.NA),
                    row.get('MENUITEM', pd.NA),
                    row.get('DISHOFFERS', pd.NA),
                    row.get('GENERALPRICE', pd.NA),
                    row.get('ORDERCODE', pd.NA),
                    row.get('HOUSEADRESS', pd.NA),
                    row.get('PRICE', pd.NA)
                )
                for index, row in df.iterrows()
            ]
            
            cursor.executemany(query, data)
            connection.commit()
            cursor.close()
            st.success("Data has been successfully saved to the database")
    
    except Error as e:
        st.error(f"Error connecting to database: {e}")
    
    finally:
        if connection and connection.is_connected():
            connection.close()


st.title("Upload and Save Excel Data")


uploaded_files = st.file_uploader("Drag and drop two Excel files", type=["xlsx"], accept_multiple_files=True)


if uploaded_files and len(uploaded_files) == 2:
    combined_df = extract_combined_data_from_excel(uploaded_files)

   
    if not combined_df.empty:
        st.write("Combined DataFrame:")
        st.write(combined_df)

        
        st.write(f"Tipo de combined_df: {type(combined_df)}")
        
        if st.button("Save Data to Database"):
            insert_data_to_db(combined_df)
    else:
        st.write("Error: No data to display or save.")
else:
    st.write("Please upload exactly two Excel files.")