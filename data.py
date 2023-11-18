from flask import Flask, render_template, request
import yfinance as yf
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

#getring history stock of the commpany
@app.route('/historical', methods=['GET', 'POST'])
def historical_data():
    if request.method == 'POST':
        stock_symbol = request.form['stock_symbol']
        start_date = request.form['start_date']
        end_date = request.form['end_date']

        # Fetch historical data using yfinance
        df = yf.download(stock_symbol, start=start_date, end=end_date)

        # Process data as needed
        # For example, you can convert the DataFrame to a list of dictionaries
        data = df.reset_index().to_dict(orient='records')

        return render_template('historical_data.html', stock_symbol=stock_symbol, data=data)

    return render_template('historical_form.html')

#real time stock price
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

#Route to real time stock price
@app.route('/realtime',methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        stock_code = request.form['stock_code']
        price, change, percent = real_time_price(stock_code)
        return render_template('realtime.html', price=price, change=change, percent=percent)
    return render_template('realtime_form.html')

if __name__ == '__main__':
    app.run(debug=True)
