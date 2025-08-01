from datetime import timedelta

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from streamlit_plotly_events import plotly_events

from chatgpt_integration import get_stock_insight

st.set_page_config(page_title="S&P 500", layout="wide")


@st.cache_data
def load_data():
    initial_data = pd.read_excel('../data/cleaned_data.xlsx')
    initial_data['Date'] = pd.to_datetime(initial_data['Date'])
    sorted_data = initial_data.sort_values('Date').reset_index(drop=True)

    sorted_data['Weekly Change (%)'] = sorted_data['Close'].pct_change() * 100

    bins = [-float('inf'), -3, -2, -1.5, -1, -0.5, 0, 0.5, 1, 1.5, 2, 3, float('inf')]
    labels = [
        'Extreme Decrease',
        'Large Decrease',
        'Significant Decrease',
        'Moderate Decrease',
        'Small Decrease',
        'Minimal Decrease',

        'Minimal Increase',
        'Small Increase',
        'Moderate Increase',
        'Significant Increase',
        'Large Increase',
        'Extreme Increase',
    ]

    sorted_data['Bins'] = pd.cut(sorted_data['Weekly Change (%)'], bins=bins, labels=labels)
    sorted_data['Bins'].fillna('Small Increase', inplace=True)

    sorted_data['Color'] = sorted_data['Bins'].apply(
        lambda x: 'rgba(12, 156, 132, 0.5)' if 'Increase' in x else 'rgba(242, 54, 69, 0.5)'
    )
    sorted_data['Dates'] = sorted_data['Date'].dt.strftime('%Y-%m-%d')

    return sorted_data


# Main UI
st.header("S&P 500 Dashboard")
st.subheader("S&P 500 Visualization with ChatGPT Integration")

left, middle, right = st.columns(3)

time_range = left.radio(
    "Time Range:",
    ["1M", "3M", "1Y", "5Y", "All"],
    horizontal=True
)

chart_type = right.selectbox(
    "Chart Type:",
    ["Candlestick", "Line", "Bar", "Table"]
)

# Handling time range change
with st.spinner("Loading data..."):
    data = load_data()

    latest_date = data['Date'].max()

    if time_range == "1M":
        start_date = latest_date - timedelta(weeks=4)
    elif time_range == "3M":
        start_date = latest_date - timedelta(weeks=13)
    elif time_range == "1Y":
        start_date = latest_date - timedelta(weeks=52)
    elif time_range == "5Y":
        start_date = latest_date - timedelta(weeks=260)
    else:  # Select earliest date for 'All'
        start_date = data['Date'].min()

    filtered_data = data[data['Date'] >= start_date]

# Handling chart type change
clicked_date = None
selected_points = None

with st.spinner("Updating chart..."):
    if chart_type == "Line":
        fig = go.Figure(
            data=[
                go.Scatter(
                    x=filtered_data['Date'],
                    y=filtered_data['Close'],
                    mode='lines+markers',
                    line=dict(color='#3366ff'),
                    hovertext=filtered_data['Bins'],
                    hoverinfo='x+text',
                )
            ]
        )
    elif chart_type == "Bar":
        fig = go.Figure(
            data=[
                go.Bar(
                    x=filtered_data['Date'],
                    y=filtered_data['Close'],
                    hovertext=filtered_data['Bins'],
                    hoverinfo='x+text',
                    marker=dict(color=filtered_data['Color'])
                )
            ]
        )
    elif chart_type == "Table":
        numeric_columns = ['Open', 'High', 'Low', 'Close', 'Weekly Change (%)']
        table_data = filtered_data[['Dates', 'Open', 'High', 'Low', 'Close', 'Weekly Change (%)', 'Bins']]
        table_data[numeric_columns] = table_data[numeric_columns].applymap(
            lambda x: round(x, 2) if x != 0 else 0
        )
        table_data.sort_values(by='Dates', inplace=True, ascending=False)

        st.markdown(
            f"<h4 style='color:white;'>S&P 500 Weekly Price Movement ({time_range})</h4>",
            unsafe_allow_html=True
        )
        event = st.dataframe(
            data=table_data,
            hide_index=True,
            on_select="rerun",
            selection_mode="single-row",
            use_container_width=True,
        )

        if len(event.selection["rows"]) > 0:
            selected_key = event.selection["rows"][0]
            selected_row = table_data.iloc[[selected_key]]
            clicked_date = selected_row['Dates'].squeeze()
    else:
        fig = go.Figure(
            data=[
                go.Candlestick(
                    x=filtered_data['Date'],
                    high=filtered_data['High'],
                    open=filtered_data['Open'],
                    close=filtered_data['Close'],
                    low=filtered_data['Low'],
                    decreasing_line_color='#f23645',
                    increasing_line_color='#0c9c84',
                    showlegend=False,
                    hovertext=filtered_data['Bins'],
                    hoverinfo='x+text',
                )
            ]
        )

if chart_type != "Table":
    fig.update_layout(
        title={
            'text': f"S&P 500 Weekly Price Movement ({time_range})",
            'font': {'color': 'white', 'size': 22}
        },
        yaxis_title="Price (USD)",
        xaxis_rangeslider_visible=False,
        clickmode='event+select',
    )

    selected_points = plotly_events(fig, click_event=True)

# Extract the clicked date
if selected_points:
    clicked_date = selected_points[0]['x']

if clicked_date:
    st.write(f"Selected Date: {clicked_date}")
else:
    st.write("Click on the graph to select a date.")

# Load macroeconomic factors
with pd.ExcelFile("../data/cleaned_data.xlsx") as xls:
    s_and_p_weekly = pd.read_excel(xls, sheet_name="Weekly S&P 500")
    s_and_p_dividend = pd.read_excel(xls, sheet_name="S&P 500 Dividend")
    s_and_p_earnings = pd.read_excel(xls, sheet_name="S&P 500 Earnings")
    pe_ratio = pd.read_excel(xls, sheet_name="PE Ratio")
    cpi = pd.read_excel(xls, sheet_name="CPI")
    us_gdp = pd.read_excel(xls, sheet_name="US GDP")
    inflation_rate = pd.read_excel(xls, sheet_name="Inflation Rate")

macro_factors = {
    "S&P 500 Dividend": s_and_p_dividend,
    "S&P 500 Earnings": s_and_p_earnings,
    "PE Ratio": pe_ratio,
    "CPI (Consumer Price Index)": cpi,
    "US GDP": us_gdp,
    "Inflation Rate": inflation_rate,
}

# Fetch insights if a date is clicked
if clicked_date:
    with st.spinner("Getting insights..."):
        insight = get_stock_insight(filtered_data, macro_factors, clicked_date)

    if insight:
        st.write(insight)
    else:
        st.write("No insights found.")
