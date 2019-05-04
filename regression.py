import csv
import random
import numpy as np
from sklearn.linear_model import LinearRegression as LR

def open_file(stock):
    stock_data = []
    path = 'historic_data/' + stock + '.csv'
    with open(path, 'r') as csv_data:
        stock_data_temp = csv.reader(csv_data)
        stock_header = next(stock_data_temp)
        for row in stock_data_temp:
            stock_data += [row]
    return stock_data, stock_header

def make_header_dict(header):
    stock_dict = {}
    count = 0
    for key in header:
        stock_dict[key] = count
        count += 1
    return stock_dict

def extract_data(row, header_dict):
    extracted = []
    extracted.append(row[header_dict['Open']])
    extracted.append(row[header_dict['High']])
    extracted.append(row[header_dict['Low']])
    extracted.append(row[header_dict['Close']])
    extracted.append(row[header_dict['Adj Close']])
    extracted.append(row[header_dict['Volume']])
    return extracted

def print_statistics(model, train_x, train_y):
    r_sq = model.score(train_x, train_y)
    print('Coefficient of determination: ', r_sq)
    print('intercept:', model.intercept_)
    print('slope:', model.coef_)

def run_trials(model, train_x, train_y, stock_data, header_dict):
    num_trials = 5
    for i in range(num_trials):
        index = random.randint(0,len(train_x))
        test_x = [train_x[index]]
        predicted_y = 5
        predicted_y = model.predict(test_x)[0][0]
        
        actual_y = train_y[index][0]
        old_y = stock_data[index][header_dict['Open']]

        #((y / old) - 1) * 100 <- percentage change
        actual_change = ((float(actual_y) / float(old_y)) - 1) * 100
        predicted_change = ((float(predicted_y) / float(old_y)) - 1) * 100
        
        predict_date = stock_data[index+1][header_dict['Date']]
        print("date: ", predict_date)
        print("actual change: ", actual_change, '%')
        print("predicted change: ", predicted_change, '%', end=' ')
        print('\n')


def main():
    stock = 'FB'
    stock_data, stock_header = open_file(stock)
    header_dict = make_header_dict(stock_header)
    print("Stock: ", stock)
    print('Stock Header:\n', stock_header)

    train_x = []
    train_y = []
    for i in range(len(stock_data)):
        row = stock_data[i]
        train_x.append(extract_data(row,header_dict))
        if i + 1 < len(stock_data):
            train_y.append([stock_data[i+1][header_dict['Open']]])
    del train_x[-1]

    train_x = np.array(train_x).astype(np.float64)
    train_y = np.array(train_y).astype(np.float64)
    model = LR()
    model.fit(train_x, train_y)

    run_trials(model, train_x, train_y, stock_data, header_dict)
    #print_statistics(model, train_x, train_y)

if __name__ == '__main__':
	main()