import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression  # Corrected import statement
from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import LabelEncoder
from snowflake.snowpark.context import get_active_session

# Title and introduction
st.title("Card Transaction Time Series Analysis")
st.write("This app analyzes card transaction data over time.")

# Connect to Snowflake
session = get_active_session()

# Function to fetch distinct card types (cached using st.cache_data)
@st.cache_data
def get_card_types():
    return session.sql("SELECT DISTINCT CARD_TYPE FROM BI.ASRA.MERCHANT_BATCH_DETAIL_PASSPORT_ONE_MONTH").collect()

# Input for selecting the card type
selected_card_type = st.selectbox(
    "Select Card Type",
    options=[row['CARD_TYPE'] for row in get_card_types()],
    index=0,
    help="Select a card type to analyze",
)

# Date range picker for filtering the data
start_date, end_date = st.date_input(
    "Select Date Range",
    value=[pd.to_datetime('2023-11-01'), pd.to_datetime('2023-12-31')],
    help="Select the start and end dates for the time series analysis",
)

# Fetch and display data based on user input
def fetch_and_display_data(card_type, start, end):
    # Querying the transaction data
    query = """
    SELECT TXN_DATE, SUM(AUTH_AMOUNT) as TOTAL_AUTH_AMOUNT
    FROM BI.ASRA.MERCHANT_BATCH_DETAIL_PASSPORT_ONE_MONTH
    WHERE CARD_TYPE = ?
    AND TXN_DATE BETWEEN ? AND ?
    GROUP BY TXN_DATE
    ORDER BY TXN_DATE
    """
    params = [card_type, str(start), str(end)]
    df = session.sql(query, params).to_pandas()

    # Check if dataframe is empty
    if df.empty:
        st.error("No data available for the selected range and card type.")
        return

    # Time Series Plot
    st.subheader("Time Series Analysis")
    plt.figure(figsize=(10, 4))
    plt.plot(df['TXN_DATE'], df['TOTAL_AUTH_AMOUNT'])
    plt.xlabel('Date')
    plt.ylabel('Total Authorization Amount')
    plt.title(f'Time Series Analysis for {card_type}')
    st.pyplot(plt)

# Call function to fetch and display data
if st.button('Analyze'):
    fetch_and_display_data(selected_card_type, start_date, end_date)

# Transaction Count by Card Type (Bar Chart)
if st.checkbox('Show Transaction Count by Card Type'):
    card_type_count_query = """
    SELECT CARD_TYPE, COUNT(*) as TRANSACTION_COUNT
    FROM BI.ASRA.MERCHANT_BATCH_DETAIL_PASSPORT_ONE_MONTH
    GROUP BY CARD_TYPE
    """
    card_type_count_df = session.sql(card_type_count_query).to_pandas()

    st.subheader("Transaction Count by Card Type")
    plt.figure(figsize=(10, 4))
    sns.barplot(data=card_type_count_df, x='CARD_TYPE', y='TRANSACTION_COUNT')
    plt.xlabel('Card Type')
    plt.ylabel('Transaction Count')
    plt.title('Transaction Count by Card Type')
    st.pyplot(plt)

# Additional analyses and visualizations can be added here

# Machine Learning Model (Optional, execute only if required)
if st.checkbox('Run Machine Learning Model'):
    # Add your ML code here
    pass
