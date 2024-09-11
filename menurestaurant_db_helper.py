import os
import pandas as pd
import streamlit as st
import mysql.connector
from mysql.connector import Error

def extract_combined_data_from_excel(file_paths):
    
    try:
       
        combined_df = pd.concat([pd.read_excel(file) for file in file_paths], ignore_index=True)
        
        
        combined_df = clean_dataframe(combined_df)
        
        return combined_df
    except Exception as e:
        st.error(f"Error reading the Excel files: {e}")
        return pd.DataFrame()  

def clean_dataframe(df):
    
    
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    
    df = df.applymap(lambda x: str(x) if pd.notna(x) else '')
    return df

def insert_menu_items_in_bulk(df):
    
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
                (row['CATEGORY'], row['MENUITEM'], row['DISHOFFERS'], row['GENERALPRICE'], row['ORDERCODE'], row['HOUSEADRESS'], row['PRICE'])
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