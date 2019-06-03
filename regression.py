import sys
import random
import numpy as np
import datetime
from sklearn.linear_model import LinearRegression as LR
from yahoo_finance_api2 import share
from yahoo_finance_api2.exceptions import YahooFinanceError

def transform_symbol_data(symbol_data):
    stock_data = []
    for i in range(len(symbol_data['timestamp'])):
        time = symbol_data['timestamp'][i]
        time = time / 1000
        fix_time = datetime.datetime.utcfromtimestamp(time)
        symbol_data['timestamp'][i] = fix_time
    stock_header = []
    keys = list(symbol_data.keys())
    for key in keys:
        stock_header.append(key)
    for i in range(len(symbol_data['timestamp'])):
        row = [symbol_data[keys[0]][i], symbol_data[keys[1]][i], symbol_data[keys[2]][i], symbol_data[keys[3]][i], symbol_data[keys[4]][i], symbol_data[keys[5]][i]]
        stock_data.append(row)

    return stock_data, stock_header

def open_file(stock):
    # stock_data = []

    stock_share = share.Share(stock)
    symbol_data = None

    try:
        symbol_data = stock_share.get_historical(share.PERIOD_TYPE_YEAR,
                                          500,
                                          share.FREQUENCY_TYPE_DAY,
                                          1)
    except YahooFinanceError as e:
        print(e.message)
        sys.exit(1)

    return transform_symbol_data(symbol_data)

def make_header_dict(header):
    stock_dict = {}
    count = 0
    for key in header:
        stock_dict[key] = count
        count += 1
    return stock_dict

def extract_data(row, header_dict):
    extracted = []
    extracted.append(row[header_dict['open']])
    extracted.append(row[header_dict['high']])
    extracted.append(row[header_dict['low']])
    extracted.append(row[header_dict['close']])
    extracted.append(row[header_dict['volume']])
    return extracted

def print_statistics(model, train_x, train_y):
    r_sq = model.score(train_x, train_y)
    print('Coefficient of determination: ', r_sq)
    print('intercept:', model.intercept_)
    print('slope:', model.coef_)

def run_trials(model, train_x, train_y, stock_data, header_dict):
    '''
    this function predicts on 5 randomly chose dates
    mostly for testing purposees
    '''
    num_trials = 5
    for i in range(num_trials):
        index = random.randint(0,len(train_x))
        test_x = [train_x[index]]
        predicted_y = model.predict(test_x)[0][0]

        actual_y = train_y[index][0]
        old_y = stock_data[index][header_dict['open']]

        #((y / old) - 1) * 100 <- percentage change
        actual_change = ((float(actual_y) / float(old_y)) - 1) * 100
        predicted_change = ((float(predicted_y) / float(old_y)) - 1) * 100

        predict_date = stock_data[index+1][header_dict['timestamp']]
        print("date: ", predict_date.strftime('%Y-%m-%d'))
        print("actual change: ", actual_change, '%')
        print("predicted change: ", predicted_change, '%', end=' ')
        print('\n')

def find_date_data(target, stock_data, header_dict):
    target = target.strftime('%Y-%m-%d')
    for i,row in enumerate(stock_data):
        date = row[header_dict['timestamp']].strftime('%Y-%m-%d')
        if target == date:
            return i,row
    raise Exception('The date entered [{}] does not exist in the data'.format(target))

def predict(model, train_x, stock_data, header_dict, date):
    index, row = find_date_data(date, stock_data, header_dict)
    #transform data to be use-able in predict
    row = extract_data(row, header_dict)
    row_array = np.array(row).astype(np.float64)

    predicted_value = model.predict([row_array])[0][0]
    prev_value = stock_data[index][header_dict['open']]
    predicted_change = ((float(predicted_value) / float(prev_value)) - 1) * 100

    print("date:", date.strftime('%Y-%m-%d'))
    print("predicted change:", predicted_change, '%', end=' ')
    print('\n')

    return predicted_change

def linear_regression(stock, latest_date):
    '''
    this function creates the linear regression model
    '''
    stock_data, stock_header = open_file(stock)
    header_dict = make_header_dict(stock_header)
    print("Stock:", stock)
    #print('Stock Header:\n', stock_header)

    train_x = []
    train_y = []
    for i in range(len(stock_data)):
        row = stock_data[i]
        if row[header_dict['timestamp']] > latest_date: break #only train on data up to the date we are predicting for
        train_x.append(extract_data(row,header_dict))
        if i + 1 < len(stock_data):
            train_y.append([stock_data[i+1][header_dict['open']]])
    #del train_x[-1]

    train_x = np.array(train_x).astype(np.float64)
    train_y = np.array(train_y).astype(np.float64)
    model = LR()
    train_y = train_y #small data fix to match list lenghts
    model.fit(train_x, train_y)

    #print_statistics(model, train_x, train_y)

    #run_trials(model, train_x, train_y, stock_data, header_dict)
    return model, train_x, train_y, stock_data, header_dict

def main():
    stock = 'GOOG'
    date = datetime.datetime(2019, 5, 31)
    assert date < datetime.datetime.now()
    model, train_x, train_y, stock_data, header_dict = linear_regression(stock, date)
    predict(model, train_x, stock_data, header_dict, date)

if __name__ == '__main__':
	main()
