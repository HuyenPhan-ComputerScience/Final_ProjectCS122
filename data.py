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
 
#ploting data by selecting days
@app.route('/ticker/<ticker>', methods=['GET', 'POST'])
def ticker(ticker):
    if request.method == 'GET':
        return render_template('ticker_form.html', stock_symbol=ticker)
    else:
        stock_symbol = ticker
        start_date = request.form['start_date']
        end_date = request.form['end_date']  
        # Fetch historical data using yfinance
        df = yf.download(stock_symbol, start=start_date, end=end_date)

        # Check if the DataFrame is empty
        if df.empty:
            return render_template('ticker.html', stock_symbol=stock_symbol, data=None, plot_url=None)

        # Process data as needed
        data = df.reset_index().to_dict(orient='records')
        plot_url = generate_plot(df, stock_symbol)

        return render_template('ticker.html', stock_symbol=stock_symbol, data=data, plot_url=plot_url)
    

#ploting data in 2 5 30 days
@app.route('/plot/<ticker>', methods=["GET"])
def plot(ticker):
    stock_symbol = ticker
    selected_days = request.args.get('days', '30')  # Use request.args for query parameters
    

    # Define the start and end dates based on the selected_days
    if selected_days == '10':
        end_date = pd.Timestamp.now().date()
        start_date = end_date - pd.DateOffset(days=10)
    elif selected_days == '2':
        end_date = pd.Timestamp.now().date()
        start_date = end_date - pd.DateOffset(days=2)
    elif selected_days == '15':
        end_date = pd.Timestamp.now().date()
        start_date = end_date - pd.DateOffset(days=15)
    elif selected_days == '30':
        end_date = pd.Timestamp.now().date()
        start_date = end_date - pd.DateOffset(days=30)
    else:
        end_date = pd.Timestamp.now().date()
        start_date = end_date - pd.DateOffset(days=30)

    # Fetch historical data using yfinance
    df = yf.download(stock_symbol, start=start_date, end=end_date)

    # Check if the DataFrame is empty
    if df.empty:
        return render_template('ticker_form.html', stock_symbol=stock_symbol, plot_url=None)

    # Process data as needed
    # (You might want to add more code here based on what you want to do with the data)

    # Generate and save the plot
    plot_url = generate_plot(df, stock_symbol)  # Assuming you have a function named generate_plot

    return render_template('ticker_form.html', stock_symbol=stock_symbol, plot_url=plot_url,selected_days=selected_days)


def generate_plot(df, ticker):
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

    return plot_url


# searching symbol with the same alphabet
@app.route('/search', methods=['POST'])
def search():
    
    search = request.form['search']
    df=pd.read_csv('data/sp500.csv')
    #getting symbol with same fist alphabet
    df1=df[df['Symbol'].str.startswith(search)]
    return render_template('search.html',column_names=df1.columns.values, row_data=list(df1.values.tolist()),
                           link_column="Symbol", zip=zip)
   



#real time data

def web_content_div(web_content, class_path):
    web_content_div = web_content.find('div', class_=class_path)
    try:
        fin_stream = web_content_div.find_all('fin-streamer')  
        texts = [fin_stream[0].get_text(), fin_stream[1].get_text(), fin_stream[2].get_text()]
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

@app.route('/realtime', methods=['GET'])
def index():
    if request.method == 'GET':
        stock_code = request.args.get('stock_code')
        if stock_code:
            price, change, percent = real_time_price(stock_code)
            return render_template('realtime.html', stock_code=stock_code, price=price, change=change, percent=percent)
        # else:
        #     # Handle the case where no stock code is provided
        #     return render_template('error.html', error_message="Please provide a stock code.")
#finding top 5 companies in the same GICS sectorwith the Ticker is chosen
@app.route('/top5/<ticker>', methods=['POST'])
def top5(ticker):
    df=pd.read_csv('data/sp500.csv')
    df1=df[df['Symbol']==ticker]
    sector=df1['GICS Sector'].values[0]
    df2=df[df['GICS Sector']==sector]
    df3=df2.sort_values(by=['CIK'],ascending=False)
    df4=df3.head(5)
    return render_template('top5.html',column_names=df4.columns.values, row_data=list(df4.values.tolist()),
                           link_column="Symbol", zip=zip)





   

if __name__ == '__main__':
    app.run(debug=True)
