# -*- coding: utf-8 -*-
"""homeowrk1.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1dcMtOce1z7i_TYWrf9Fq_uvFOxdKOuX4

### 0) Imports
"""

# install the main library YFinance
!pip install yfinance

# IMPORTS
import numpy as np
import pandas as pd

#Fin Data Sources
import yfinance as yf
import pandas_datareader as pdr

#Data viz
import plotly.graph_objs as go
import plotly.express as px

import time
from datetime import date

"""### Question 1: [Index] S&P 500 Stocks Added to the Index

1.
"""

# Web Scraping for Macro
# can't call directly via pd.read_html() as it returns 403 (forbidden) --> need to do a bit of work, but still no Selenium
import requests
from bs4 import BeautifulSoup


url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
}

response = requests.get(url, headers=headers)

df = pd.read_html(url)

snp500_components_df = df[0]

snp500_components_df

# Assuming snp500_components_df is already loaded and contains the data from the Wikipedia page
# Select the relevant columns and rename them
snp500_additions_df = snp500_components_df[['Symbol', 'Security', 'Date added']].copy()

# Convert the 'Add Year' column to datetime and then extract the year
snp500_additions_df['Date added'] = pd.to_datetime(snp500_additions_df['Date added']).dt.year

snp500_additions_df.sort_values(by='Date added', ascending=False, inplace=True)

print (f'Question 1 answer: {snp500_additions_df.head()}')

"""2."""

additions_by_year_df = snp500_additions_df['Date added'].value_counts().sort_index()

additions_by_year_df

"""3."""

# Exclude the year 1957
additions_by_year_x1957_df = additions_by_year[additions_by_year.index != 1957]

max_additions_amount_df = additions_by_year_x1957_df.max()

# Find all years that have the maximum number of additions
max_additions_year_df = list(additions_by_year_x1957_df[additions_by_year_x1957_df == max_additions_amount_df].index)

print(f"The maximum number of S&P 500 additions (excluding 1957) is: {max_additions_amount_df}")
print(f"The years with the highest number of S&P 500 additions (excluding 1957) are: {max_additions_year_df}")

"""### Question 2: [Macro] Indexes YTD (as of 1 May 2025)"""

url = "https://finance.yahoo.com/markets/world-indices/"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
}

response = requests.get(url, headers=headers)

response.raise_for_status() # This will raise an HTTPError for bad responses (4xx or 5xx)

world_indices_df = pd.read_html(response.text)

world_indices_df = world_indices_df[0]

world_indices_df

# ['change%'] = world_indices_df['change%'].str.replace('%', '').astype(float)

# List of symbols for the desired indices
selected_symbols = [
    '^GSPC',      # United States - S&P 500
    '000001.SS',  # China - Shanghai Composite
    '^HSI',       # Hong Kong - HANG SENG INDEX
    '^AXJO',      # Australia - S&P/ASX 200
    '^NSEI',      # India - Nifty 50
    '^GSPTSE',    # Canada - S&P/TSX Composite
    '^GDAXI',     # Germany - DAX
    '^FTSE',      # United Kingdom - FTSE 100
    '^N225',      # Japan - Nikkei 225
    '^MXX',       # Mexico - IPC Mexico
    '^BVSP'       # Brazil - Ibovespa
]

# Filter the DataFrame to include only rows where the 'Symbol' is in the selected_symbols list
filtered_indices_df = world_indices_df[world_indices_df['Symbol'].isin(selected_symbols)].copy()


# Assuming 'Symbol' is the correct column name and '^GSPC' is the symbol for S&P 500
try:
    sp500_row = filtered_indices_df[filtered_indices_df['Symbol'] == '^GSPC'].iloc[0]
except IndexError:
    print("S&P 500 ('^GSPC') not found in the DataFrame.")
    # Handle the case where S&P 500 is not in the table if necessary
    # For now, we will stop execution if not found
    raise

# Print the column names to inspect them
print(filtered_indices_df.columns)

# Get the S&P 500's YTD return. Replace 'change%' with the correct column name if it's different.
# Based on inspecting Yahoo Finance's World Indices page, the column name is 'Change %'
sp500_ytd_return_str = sp500_row['Change %']

# Convert the 'Change %' column to numeric
# It's a string like "+10.56%" or "-2.34%"
# We need to remove the '%' sign and convert to float
# Use the correct column name 'Change %' here as well
filtered_indices_df['Change %'] = filtered_indices_df['Change %'].str.replace('%', '').astype(float)

# Get the numeric YTD return for S&P 500
sp500_ytd_return_numeric = filtered_indices_df[filtered_indices_df['Symbol'] == '^GSPC']['Change %'].iloc[0]

# Filter out the S&P 500 itself for comparison
other_indices_df = filtered_indices_df[filtered_indices_df['Symbol'] != '^GSPC'].copy()

# Count how many other indices have a better YTD return
better_performing_indices_count = (other_indices_df['Change %'] > sp500_ytd_return_numeric).sum()

# Get the total number of indices compared (excluding S&P 500)
total_indices_compared = len(other_indices_df)

print(f"The S&P 500 YTD return is: {sp500_ytd_return_str}")
print(f"Out of {total_indices_compared} other indexes listed, {better_performing_indices_count} have better year-to-date returns than the US (S&P 500) as of {date.today()}.")

# Display the indexes with better returns if you want
better_performing_indices_df = other_indices_df[other_indices_df['Change %'] > sp500_ytd_return_numeric]
print("\nIndexes with better YTD returns:")
print(better_performing_indices_df[['Symbol', 'Name', 'Change %']]) # Use 'Change %' here too if displaying

"""### Question 3. [Index] S&P 500 Market Corrections Analysis"""

# Download S&P 500 historical data (1950-present) using yfinance
# Define the ticker symbol for S&P 500
ticker = "^GSPC"
# Define the start and end dates
start_date = "1950-01-01"
end_date = date.today().strftime('%Y-%m-%d') # Use today's date as the end date

# Download the data
sp500_data = yf.download(ticker, start=start_date, end=end_date)

# We only need the 'Close' price for this analysis
# sp500_close is a DataFrame with 'Close' as a column
sp500_close = sp500_data[['Close']]

# Identify all-time high points
# Calculate a cumulative maximum to find all-time highs
# Apply cummax() to the 'Close' column
all_time_highs = sp500_close['Close'].cummax()

# Find the dates where a new all-time high is reached
# Use the Series for finding ATH dates
ath_dates = sp500_close['Close'][sp500_close['Close'] == all_time_highs].index

# Initialize lists to store correction data
correction_starts = []
correction_ends = []
correction_lows = []
correction_drawdowns = []
correction_durations = []

# Iterate through the all-time high dates to find corrections
# We start from the second all-time high because a correction happens after reaching a new high
for i in range(1, len(ath_dates)):
    start_date_correction = ath_dates[i-1]
    end_date_correction = ath_dates[i]

    # Get the data between the two consecutive all-time highs
    # Use the DataFrame for slicing
    correction_period_data = sp500_close.loc[start_date_correction:end_date_correction, 'Close']

    # Find the minimum price in between the two all-time highs
    correction_low = correction_period_data.min()

    # The all-time high before the correction is the start price
    # Access the 'Close' price for the specific date using .loc
    ath_value = sp500_close.loc[start_date_correction, 'Close']

    # Calculate drawdown percentage: (high - low) / high * 100
    drawdown_percentage = ((ath_value - correction_low) / ath_value) * 100

    # If the drawdown is at least 5%, consider it a correction
    # Extract the scalar value from the Series using .item()
    if drawdown_percentage.item() >= 5:
        # Find the date of the correction low
        low_date = correction_period_data.idxmin()

        correction_starts.append(start_date_correction)
        correction_ends.append(low_date) # The end of the drawdown is the date of the low
        correction_lows.append(correction_low.item()) # Also extract scalar for lists
        correction_drawdowns.append(drawdown_percentage.item()) # Also extract scalar for lists

        # Calculate the duration in days for each correction period
        # Ensure both are scalar Timestamps before subtracting
        duration = (low_date.item() - start_date_correction).days
        correction_durations.append(duration)


# Create a DataFrame to store the correction data
corrections_df = pd.DataFrame({
    'Start Date': correction_starts,
    'End Date': correction_ends,
    # Get the actual ATH value using .loc
    'All-Time High': [sp500_close.loc[date, 'Close'].item() for date in correction_starts], # Extract scalar
    'Correction Low': correction_lows,
    'Drawdown (%)': correction_drawdowns,
    'Duration (days)': correction_durations
})

# Determine the 25th, 50th (median), and 75th percentiles for correction durations
percentiles = corrections_df['Duration (days)'].quantile([0.25, 0.5, 0.75])

print("S&P 500 Market Correction Duration Percentiles (>= 5% Drawdown):")
print(f"25th Percentile: {percentiles[0.25]:.2f} days")
print(f"50th Percentile (Median): {percentiles[0.50]:.2f} days")
print(f"75th Percentile: {percentiles[0.75]:.2f} days")

# Display the first few corrections found (optional)
corrections_df.head()

# Sort the DataFrame by 'Drawdown (%)' in descending order
largest_corrections_df = corrections_df.sort_values(by='Drawdown (%)', ascending=False)

largest_corrections_df.head(10)