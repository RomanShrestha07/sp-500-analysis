import pandas as pd
from bs4 import BeautifulSoup
import requests
import yfinance as yf


# function for web scraping
def fetch_table_data(url, columns, start_date='1990-01-01'):
    # Fetch the web page
    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'html.parser')

    # for finding the table element
    table = soup.find('table')

    # Extract rows from the table
    rows = []
    for row in table.find_all('tr'):
        cols = row.find_all('td')
        cols = [ele.text.strip() for ele in cols]
        if cols:
            rows.append(cols)

    # Create DataFrame and filter by start date
    data = pd.DataFrame(rows, columns=columns)
    data['Date'] = pd.to_datetime(data['Date'])
    data = data[data['Date'] >= start_date]
    return data


# S&P 500 by Weekly
ticker_symbol = "^GSPC"
sp500_data = yf.download(ticker_symbol, interval="1wk", start="1990-01-01")
sp500_data.index = sp500_data.index.tz_localize(None)
sp500_data = sp500_data.reset_index()
print("S&P 500 Weekly Data:")
print(sp500_data)

# S&P 500 Dividend by Month
url_dividend = "https://www.multpl.com/s-p-500-dividend/table/by-month"
dividend_data = fetch_table_data(url_dividend, ["Date", "Dividend Value"])
print("S&P 500 Dividend Data:")
print(dividend_data)

# S&P 500 Earnings
url_sp500_earning = "https://www.multpl.com/s-p-500-earnings/table/by-month"
sp500_earnings_data = fetch_table_data(url_sp500_earning, ["Date", "S&P 500 Earnings Value"])
print("\nS&P 500 Earnings:")
print(sp500_earnings_data)

# S&P 500 PE Ratio by Month
url_pe_ratio = "https://www.multpl.com/s-p-500-pe-ratio/table/by-month"
pe_ratio_data = fetch_table_data(url_pe_ratio, ["Date", "PE Ratio Value"])
print("\nS&P 500 PE Ratio by Month:")
print(pe_ratio_data)

# S&P 500 Historical Prices by Month
url_historical = "https://www.multpl.com/s-p-500-historical-prices/table/by-month"
historical_data = fetch_table_data(url_historical, ["Date", "Historical Prices"])
print("\nS&P 500 Historical Prices by Month:")
print(historical_data)

# US CPI data
url_cpi = "https://www.multpl.com/cpi/table/by-month"
cpi_data = fetch_table_data(url_cpi, ["Date", "CPI Value"])
print("\nCPI Data:")
print(cpi_data)

# US GDP by Quarter
url_gdp = "https://www.multpl.com/us-gdp/table/by-quarter"
gdp_data = fetch_table_data(url_gdp, ["Date", "GDP Value"])
print("\nUS GDP by Quarter:")
print(gdp_data)

# US Inflation Rate by Month
url_inflation = "https://www.multpl.com/inflation/table/by-month"
inflation_data = fetch_table_data(url_inflation, ["Date", "Inflation Rate"])
print("\nUS Inflation Rate by Month:")
print(inflation_data)

# Reset the column MultiIndex if it exists
if isinstance(sp500_data.columns, pd.MultiIndex):
    sp500_data.columns = ['_'.join(col).strip() for col in sp500_data.columns.values]

# Save datasets to a single Excel file with different sheets
with pd.ExcelWriter("../data/financial_data.xlsx") as writer:
    sp500_data.to_excel(writer, sheet_name="Weekly S&P 500", index=False)
    dividend_data.to_excel(writer, sheet_name="S&P 500 Dividend", index=False)
    sp500_earnings_data.to_excel(writer, sheet_name="S&P 500 Earnings", index=False)
    pe_ratio_data.to_excel(writer, sheet_name="PE Ratio", index=False)
    historical_data.to_excel(writer, sheet_name="Historical Prices", index=False)
    cpi_data.to_excel(writer, sheet_name="CPI", index=False)
    gdp_data.to_excel(writer, sheet_name="US GDP", index=False)
    inflation_data.to_excel(writer, sheet_name="Inflation Rate", index=False)
