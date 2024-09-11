import os
import streamlit as st
import pandas as pd
import mysql.connector
from mysql.connector import Error


def extract_combined_data_from_excel(files):
    
    try:
        combined_df = pd.concat([pd.read_excel(file) for file in files], ignore_index=True)
        return combined_df
    except Exception as e:
        st.error(f"Error reading the Excel files: {e}")
        return pd.DataFrame()  


def insert_data_to_db(df):
    
    connection = None
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
            LOAD DATA INFILE 'C:\\xampp\\mysql\\data\\2024-09-10T19-00_export.csv'
            INTO TABLE uploadmenu
            FIELDS TERMINATED BY ','
            ENCLOSED BY '"'
            LINES TERMINATED BY '\n'
            IGNORE 1 ROWS
            (CATEGORY, MENUITEM, DISHOFFERS, GENERALPRICE, ORDERCODE,PRICE);
            """
            
           
            data = [
                (
                    df.at[i, 'ORDERCODE'],
                    df.at[i, 'MENUITEM'],
                    df.at[i, 'PRICE'],
                    df.at[i, 'GENERALPRICE'],
                    df.at[i, 'CATEGORY'],                    
                    df.at[i, 'DISHOFFERS']
                ) for i in range(len(df))
            ]
            
            cursor.execute(query, data)
            connection.commit()
            cursor.close()
            st.success("Data has been successfully saved to the database")
    
    except Error as e:
        st.error(f"Error connecting to database: {e}")
    
    finally:
        if connection and connection.is_connected():
            connection.close()


st.title("Upload for create a menu restaurant")


uploaded_files = st.file_uploader("Drag and drop two Excel files", type=["xlsx"], accept_multiple_files=True)


if uploaded_files and len(uploaded_files) == 2:
    combined_df = extract_combined_data_from_excel(uploaded_files)

    
    if not combined_df.empty:
        st.write("Combined DataFrame:")
        
        
        st.dataframe(combined_df, use_container_width=True)
        
        if st.button("Save Data to Database"):
            insert_data_to_db(combined_df)
    else:
        st.write("Error: No data to display or save.")
else:
    st.write("Please upload exactly two Excel files.")