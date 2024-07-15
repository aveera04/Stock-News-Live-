import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import os

load_dotenv("Python\projects\Stock_news\stock-news-hard-start\private.env")

# Define the stock parameters
STOCK = "NVDA"
COMPANY_NAME = "Nvidia Corp"
stock_params = {
    "function" : "TIME_SERIES_DAILY",
    "symbol" : STOCK ,
    "outputsize" : "compact",
    "apikey": os.environ["STOCK_API_KEY"]
}

STOCK_ENDPOINT = "https://www.alphavantage.co/query"

# Get the stock data
stock_response = requests.get(STOCK_ENDPOINT, params=stock_params)
stock_response.raise_for_status()
data = stock_response.json()

# Print the keys of the stock data
print(data.keys())

# Extract the time series data
time_series = data["Time Series (Daily)"]
dates = sorted(time_series.keys())
yesterday = dates[-1]
day_before_yesterday = dates[-2]
yesterday_ltp = float(time_series[yesterday]["4. close"])
day_before_yesterday_ltp = float(time_series[day_before_yesterday]["4. close"])

# Print the last two closing prices
print(yesterday_ltp, day_before_yesterday_ltp)

# Calculate the difference between the last two closing prices
difference  = (yesterday_ltp - day_before_yesterday_ltp)

# Define a function to determine if the stock price went up or down
def up_down(difference):
    if difference > 0:
        return "🔼"
    else:
        return "🔻"

# Call the up_down function to get the up/down symbol
up_down = up_down(difference)

# Calculate the percentage change
percentage = abs(difference / yesterday_ltp * 100)

# Print the up/down symbol and percentage change
print(up_down, percentage)

# Define the news parameters
news_params= {
    "qInTitle" : "Nvidia" ,
    "from" : yesterday,
    "to" : day_before_yesterday,
    "language" : "en",
    "apiKey" : os.environ["NEWS_API_KEY"]
}

NEWS_ENDPOINT = "https://newsapi.org/v2/everything"

# Get the news articles
news_response = requests.get(NEWS_ENDPOINT, params=news_params)
news_response.raise_for_status()
top3_articles = news_response.json()["articles"][:3]

# Format the articles
formatted_articles = [f"Headline : {article['title']}. \nBrief : {article['description']}" for article in top3_articles]

# Print the formatted articles
print(formatted_articles)

# Send a separate message with each article's title and description to your phone number. 
with smtplib.SMTP("smtp.gmail.com") as connection:
    connection.starttls()
    connection.login(user=os.environ["EMAIL_ID"], password= os.environ["PASSWORD"])
    for article in formatted_articles:
        msg = MIMEMultipart()
        msg['From'] = os.environ["EMAIL_ID"]
        msg['To'] = os.environ["RECIEVER_EMAIL_ID"]
        msg['Subject'] = f"{COMPANY_NAME} is {up_down}{percentage}"
        msg.attach(MIMEText(article, 'plain', 'utf-8'))
        connection.sendmail(
            from_addr=os.environ["EMAIL_ID"],
            to_addrs=os.environ["RECIEVER_EMAIL_ID"],
            msg=msg.as_string())
            
        print("sent successfully")

