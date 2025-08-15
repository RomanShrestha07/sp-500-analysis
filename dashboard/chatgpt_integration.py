from openai import OpenAI

client = OpenAI(
    api_key="openai_api_key",  ## use your OpenAI API key here
)


def get_stock_insight(sp500_data, macro_factors, date):
    """
    Function to generate a summary based on stock movement, macroeconomic factors, and news.

    :param sp500_data: S&P 500 data
    :param macro_factors: macroeconomic factors that could explain stock movements
    :param date: the date for which the analysis is requested
    :return: GPT-4o-mini generated explanation
    """

    macro_data_str = "\n".join([f"{key}: {value}" for key, value in macro_factors.items()])

    prompt = f"""
    Here, is the S&P 500 stock market data for your reference: {sp500_data}.
    
    The macroeconomic factors that could explain the change on {date} are: {macro_data_str}
    
    Based on these information and the knowledge you possess, please provide a detailed analysis on what might have 
    caused this price change, including any possible market reactions or external factors.
    
    Always give real non-financial APNews news headlines looking back at least a few months that might have influenced the price change, with a short explanation of it. 
    
    These will be two sections called: Possible Causes and Relevant Events. Don't mention APNews. 
    
    Also, don't give any extra information, text or conversation. Be very concise and precise.    
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        max_tokens=4096,
        temperature=0.1,
        messages=[
            {
                "role": "system",
                "content": "You are an expert stock analyst for S&P 500."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    explanation = response.choices[0].message.content.strip()
    return explanation
