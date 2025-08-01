import pandas as pd

file_path = "../data/financial_data.xlsx"


def clean_date(df, date_column="Date"):
    df[date_column] = pd.to_datetime(df[date_column]).dt.strftime('%Y-%m-%d')
    return df


with pd.ExcelFile(file_path) as xls:
    sp500_weekly_data = pd.read_excel(xls, sheet_name="Weekly S&P 500")
    dividend_data = pd.read_excel(xls, sheet_name="S&P 500 Dividend")
    sp500_earnings_data = pd.read_excel(xls, sheet_name="S&P 500 Earnings")
    pe_ratio_data = pd.read_excel(xls, sheet_name="PE Ratio")
    historical_data = pd.read_excel(xls, sheet_name="Historical Prices")
    cpi_data = pd.read_excel(xls, sheet_name="CPI")
    gdp_data = pd.read_excel(xls, sheet_name="US GDP")
    inflation_data = pd.read_excel(xls, sheet_name="Inflation Rate")

# S&P 500 Weekly Data
sp500_weekly_data = sp500_weekly_data[['Date_', 'High_^GSPC', 'Open_^GSPC', 'Close_^GSPC', 'Low_^GSPC']].copy()
sp500_weekly_data.rename(
    columns={
        'Date_': 'Date',
        'High_^GSPC': 'High',
        'Open_^GSPC': 'Open',
        'Close_^GSPC': 'Close',
        'Low_^GSPC': 'Low',
    },
    inplace=True
)

sp500_weekly_data = sp500_weekly_data.iloc[::-1].reset_index(drop=True)

# Date formatting
sp500_weekly_data = clean_date(sp500_weekly_data, date_column="Date")
dividend_data = clean_date(dividend_data, date_column="Date")
sp500_earnings_data = clean_date(sp500_earnings_data, date_column="Date")
pe_ratio_data = clean_date(pe_ratio_data, date_column="Date")
historical_data = clean_date(historical_data, date_column="Date")
cpi_data = clean_date(cpi_data, date_column="Date")
gdp_data = clean_date(gdp_data, date_column="Date")
inflation_data = clean_date(inflation_data, date_column="Date")

# PE Ratio Data
pe_ratio_data['PE Ratio Value'] = pe_ratio_data['PE Ratio Value'].str.replace(r'[^0-9.]+', '', regex=True).astype(float)

# US GDP Data
gdp_data['GDP Value'] = gdp_data['GDP Value'].str.replace(' trillion', '', regex=False).astype(float)
gdp_data.rename(columns={'GDP Value': 'GDP Value - trillion'}, inplace=True)

# Inflation Rate Data
inflation_data['Inflation Rate'] = inflation_data['Inflation Rate'].str.replace('%', '', regex=False).astype(float)
inflation_data.rename(columns={'Inflation Rate': 'Inflation Rate %'}, inplace=True)

print(sp500_weekly_data.head())
print(dividend_data.head())
print(sp500_earnings_data.head())
print(pe_ratio_data.head())
print(historical_data.head())
print(cpi_data.head())
print(gdp_data.head())
print(inflation_data.head())

sp500_weekly_data.sort_values(by='Date', inplace=True)
dividend_data.sort_values(by='Date', inplace=True)
sp500_earnings_data.sort_values(by='Date', inplace=True)
pe_ratio_data.sort_values(by='Date', inplace=True)
historical_data.sort_values(by='Date', inplace=True)
cpi_data.sort_values(by='Date', inplace=True)
gdp_data.sort_values(by='Date', inplace=True)
inflation_data.sort_values(by='Date', inplace=True)

sp500_weekly_data.set_index('Date', inplace=True)
dividend_data.set_index('Date', inplace=True)
sp500_earnings_data.set_index('Date', inplace=True)
pe_ratio_data.set_index('Date', inplace=True)
historical_data.set_index('Date', inplace=True)
cpi_data.set_index('Date', inplace=True)
gdp_data.set_index('Date', inplace=True)
inflation_data.set_index('Date', inplace=True)

output_file_path = "../data/cleaned_data.xlsx"
with pd.ExcelWriter(output_file_path) as writer:
    sp500_weekly_data.to_excel(writer, sheet_name='Weekly S&P 500')
    dividend_data.to_excel(writer, sheet_name='S&P 500 Dividend')
    sp500_earnings_data.to_excel(writer, sheet_name='S&P 500 Earnings')
    pe_ratio_data.to_excel(writer, sheet_name='PE Ratio')
    historical_data.to_excel(writer, sheet_name='Historical Prices')
    cpi_data.to_excel(writer, sheet_name='CPI')
    gdp_data.to_excel(writer, sheet_name='US GDP')
    inflation_data.to_excel(writer, sheet_name='Inflation Rate')

print(f"Cleaned data saved to {output_file_path}")
