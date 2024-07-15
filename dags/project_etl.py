#!/usr/bin/env python
# coding: utf-8

import os  # Imports the os module to interact with the operating system
import sqlite3  # Imports the sqlite3 module to interact with SQLite databases
import requests  # Imports the requests module to make HTTP requests
import datetime  # Imports the datetime module to handle dates and times
import pandas as pd  # Imports the pandas module to handle dataframes

def extract_data_from_api():
    """
    Extracts current weather data from the WeatherAPI for Rio de Janeiro.

    Returns:
        pd.DataFrame: A dataframe containing the weather data including temperature,
                      wind speed, condition, precipitation, humidity, feels-like temperature,
                      pressure, visibility, day/night indicator, and timestamp.
    """
    # Gets the current date and time
    today = datetime.datetime.now()
    
    # Makes a GET request to the weather API
    data_api = requests.get("http://api.weatherapi.com/v1/current.json?key=2dcc8a8d61ef44a38e6194440241207&q=Rio de Janeiro&aqi=yes")
    
    # Converts the API response to JSON
    data_json = data_api.json()

    # Creates a dictionary with the relevant data extracted from the JSON response
    dictionary_data = {
        "temperature": [data_json["current"]["temp_c"]],
        "wind_speed": [data_json["current"]["wind_kph"]],
        "condition": [data_json["current"]["condition"]["text"]],
        "precipitation": [data_json["current"]["precip_mm"]],
        "humidity": [data_json["current"]["humidity"]],
        "feels_like_temp": [data_json["current"]["feelslike_c"]],
        "pressure": [data_json["current"]["pressure_mb"]],
        "visibility": [data_json["current"]["vis_km"]],
        "is_day": [data_json["current"]["is_day"]],
        "timestamp": [today]
    }

    # Converts the dictionary to a pandas DataFrame
    return pd.DataFrame(dictionary_data)

def data_quality_process(df_data):
    """
    Checks the quality of the extracted data.

    Args:
        df_data (pd.DataFrame): The dataframe containing the extracted data.

    Returns:
        bool: False if the data is empty or has missing values, otherwise None.
    """
    # Checks if the DataFrame is empty
    if df_data.empty:
        print("Data was not extracted")
        return False
    
    # Checks if there are any missing values in the DataFrame
    if df_data.isnull().values.any():
        print("Missing values detected. Data cleaning will be necessary.")

def data_transform_process(df_data):
    """
    Transforms the extracted data for further processing.

    Args:
        df_data (pd.DataFrame): The dataframe containing the extracted data.

    Returns:
        pd.DataFrame: The transformed dataframe.
    """
    # Converts the "is_day" column to boolean
    df_data["is_day"] = df_data["is_day"].astype(bool)
    
    # Creates an "ID" column by combining the timestamp and temperature
    df_data["ID"] = df_data['timestamp'].astype(str) + "-" + df_data["temperature"].astype(str)
    
    return df_data

def extract_transform_process():
    """
    Runs the data extraction and transformation processes.

    Returns:
        pd.DataFrame: The dataframe containing the extracted and transformed data.
    """
    # Extracts data from the API
    df_data = extract_data_from_api()
    
    # Transforms the extracted data
    df_data = data_transform_process(df_data)

    # Checks the quality of the data
    data_quality_process(df_data)
    
    return df_data

def etl_weather():
    """
    Main ETL (Extract, Transform, Load) function for weather data.
    Extracts data from the API, transforms it, and loads it into a CSV file and SQLite database.
    """
    # Runs the extraction and transformation process
    df = extract_transform_process()
    
    # Defines the file path for the CSV file to save the data
    file_path = "/opt/airflow/dags/data_weather.csv"
    
    # Checks if the file already exists to determine if the header should be included
    header = not os.path.isfile(file_path)
    
    # Saves the transformed data to a CSV file
    df.to_csv(file_path, mode='a', index=False, header=header)

    # Connects to the SQLite database
    conn = sqlite3.connect('/opt/airflow/dags/database_weather.db')

    # Saves the transformed data to the 'data_weather' table in the database
    df.to_sql('data_weather', conn, if_exists='append', index=False)

    # Closes the connection to the database
    conn.close()
