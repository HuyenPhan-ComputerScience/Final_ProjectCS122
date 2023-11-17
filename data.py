from flask import Flask, render_template, request
import yfinance as yf

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/', methods=['GET', 'POST'])
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

@app.route('/realtime', methods=['GET', 'POST'])
def real_time_data():
    if request.method == 'POST':
        stock_symbol = request.form['stock_symbol']

        try:
            # Fetch real-time data using yfinance
            stock_info = yf.Ticker(stock_symbol)
            current_price = stock_info.info['last_price']
        except:
            current_price = "N/A"  # Handle the case where real-time data is not available

        return render_template('realtime_data.html', stock_symbol=stock_symbol, current_price=current_price)

    return render_template('realtime_form.html')

if __name__ == '__main__':
    app.run(debug=True)
