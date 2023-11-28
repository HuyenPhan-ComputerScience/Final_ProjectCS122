from flask import Flask, render_template, request
import yfinance as yf
import pandas as pd
import datetime
import requests

from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import matplotlib
matplotlib.use('agg')
app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    
    df=pd.read_csv('data/sp500.csv')

    return render_template('home.html',column_names=df.columns.values, row_data=list(df.values.tolist()),
                           link_column="Symbol", zip=zip)
 

@app.route('/ticker/<ticker>', methods=['GET', 'POST'])
def ticker(ticker):
    if request.method == 'GET':
        return render_template('ticker_form.html', stock_symbol=ticker)
    else:
        stock_symbol =  ticker
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        print(stock_symbol, start_date, end_date)
        # Fetch historical data using yfinance
        df = yf.download(stock_symbol, start=start_date, end=end_date)

        # # Check if the DataFrame is empty
        if df.empty:
            return render_template('ticker.html', stock_symbol=stock_symbol, data=None, plot_url=None)
        
        print(df)
            # Process data as needed
        # For example, you can convert the DataFrame to a list of dictionaries
        data = df.reset_index().to_dict(orient='records')

        # Plotting the data
        plt.figure(figsize=(10, 6))
        plt.plot(df.index, df["Close"], label='Closing Price')
        plt.xlabel('Date')
        plt.ylabel('Closing Price')
        plt.title(f'Historical Stock Data for {ticker}')
        plt.legend()

        # Save the plot to a BytesIO object
        img = BytesIO()
        plt.savefig(img, format='png')
        img.seek(0)

        # Encode the image as base64 and convert it to a string
        plot_url = base64.b64encode(img.getvalue()).decode()

        return render_template('ticker.html', stock_symbol=stock_symbol, data=data, plot_url=plot_url)

#getting information about the company






#real time data

def web_content_div(web_content, class_path):
    web_content_div = web_content.find('div', class_=class_path)
    try:
        fin_stream = web_content_div.find_all('fin-streamer')  
        texts = [fin.get_text() for fin in fin_stream]
    except AttributeError:
        texts = []
    return texts

def real_time_price(stock_code):
    url = 'https://finance.yahoo.com/quote/' + stock_code + '?p=' + stock_code + '&.tsrc=fin-srch'
    try:
        r = requests.get(url)
        r.raise_for_status()  # Raise an HTTPError for bad requests
        web_content = BeautifulSoup(r.text, 'html.parser')
        texts = web_content_div(web_content, 'My(6px) Pos(r) smartphone_Mt(6px) W(100%)')
        if texts:
            price, change, percent = texts[0], texts[1], texts[2]
        else:
            price, change, percent = None, None, None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        price, change, percent = None, None, None
    return price, change, percent

@app.route('/realtime',methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        stock_code = request.form['stock_code']
        price, change, percent = real_time_price(stock_code)
        return render_template('realtime.html', price=price, change=change, percent=percent)
    return render_template('realtime_form.html')



   

if __name__ == '__main__':
    app.run(debug=True)
