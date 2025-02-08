import requests
import datetime
import pandas as pd
import statistics
import numpy as np
import cvxopt
#import matplotlib as plt
import cvxpy as cp
oo = 0

today = datetime.datetime.today().date()
past  = today - datetime.timedelta(days = 150)


# Your API key from Alpha Vantage
apiKey = ''  # Replace with your actual API key



# Define the stock symbol (e.g., AAPL for Apple)


# Define the URL endpoint and parameters
url = 'https://www.alphavantage.co/query'

#x = str(input("what stock are you interested in?"))
#ifx != None:
def getStockInfo(symbols):
    #symbol = x
    paramsTimeSeriesDaily = {
        'function': 'TIME_SERIES_DAILY',  # Real-time stock data
        'symbol': symbols,                    # Stock symbol (e.g., 'AAPL')
        #'interval': '5min',                  # Interval of stock price (e.g., '1min', '5min', '15min')
        'apikey': apiKey                    # Your API key
    }

    # Send the GET request
    responseTimeSeriesDaily = requests.get(url, params=paramsTimeSeriesDaily)

    # Check if the request was successful (HTTP status code 200)
    if responseTimeSeriesDaily.status_code == 200:
        # Parse the JSON response data
        dataTimeSeriesDaily = responseTimeSeriesDaily.json()

        if 'Time Series (Daily)' not in dataTimeSeriesDaily:
            print("No data for that stock code")
            return ("None")
            #print(dataTimeSeriesDaily)
            
        else:
            timeSeries = dataTimeSeriesDaily['Time Series (Daily)']

            closingPrices = [float(stats['4. close']) for date, stats in timeSeries.items()]
            dfClosingPrices = pd.Series(closingPrices)
            #print(closingPrices)
            allPchanges =(dfClosingPrices.pct_change().dropna())#dropna removes any nulls such as comparisons with non-existent days
            mean = (dfClosingPrices.pct_change().dropna().mean(), dfClosingPrices.pct_change().dropna().std())#includes std as well
            # Extract the most recent data point (latest price)
            highestPrice  = float("-inf")#start from rock bottom then compare upwards
            lowestPrice = float("inf")# vice versa
            highestDate = None
            lowestDate = None
            currentPrice = None
            
            for date, stats in timeSeries.items():
                dateObj = datetime.datetime.strptime(date, '%Y-%m-%d').date()

                if dateObj >= past:
                    highPrice = float(stats['2. high'])
                    lowPrice = float(stats['3. low'])
                    current = float(stats['4. close'])

                    if highPrice > highestPrice:
                        highestPrice = highPrice
                        highestDate = date

                    if lowPrice < lowestPrice:
                        lowestPrice = lowPrice
                        lowestDate = date

                    if currentPrice is None or dateObj == today:
                        currentPrice = current

                
           # if highestDate and lowestDate:
           #     print(f"The highest price for {symbols} in the past 150 days was ${highestPrice} on {highestDate}.")
           #     print(f"The lowest price for {symbols} in the past 150 days was ${lowestPrice} on {lowestDate}.")
           #     print(f"The current price of {symbols} is: ${currentPrice} on {today}")
           # else:
           #     print("No data found for the past year.")
    else:
        print("Error:", responseTimeSeriesDaily.status_code)

    paramsGlobalQuote = {
        'function': 'GLOBAL_QUOTE',  # Real-time stock data
        'symbol': symbols,                    # Stock symbol (e.g., 'AAPL')
        'interval': '5min',                  # Interval of stock price (e.g., '1min', '5min', '15min')
        'apikey': apiKey                    # Your API key
    }

    responseGlobalQuote = requests.get(url, params=paramsGlobalQuote)

    if responseGlobalQuote.status_code == 200:
        dataGlobalQuote = responseGlobalQuote.json()

        if 'Global Quote' in dataGlobalQuote:
            globalQuote = dataGlobalQuote['Global Quote']


            

            #currentPrice = float(globalQuote['05. price'])  # Current price
            change = float(globalQuote['09. change'])  # Price change
            changePercent = globalQuote['10. change percent']  # Percent change
            previousClose = float(globalQuote['08. previous close'])  # Previous close
            volume = int(globalQuote['06. volume'])  # Volume traded

            return {#returning a dictionary
                "symbol": symbols,
                "currentPrice": currentPrice,
                "highestPrice": highestPrice,
                "highestDate": highestDate,
                "lowestPrice": lowestPrice,
                "lowestDate": lowestDate,
                "meanReturn": mean[0],
                #"std_dev": std_dev,
                "change": change,
                "change_percent": changePercent,
                "previous_close": previousClose,
                "volume": volume,
                "allPercentages": allPchanges,
            }
        
        else:
            print(f"Error fetching Global Quote data for {symbols}: {responseGlobalQuote.status_code}")
            return None
        
    else:
        print(f"Error fetching data for {symbols}: {responseTimeSeriesDaily.status_code}")
        return None
    
#stocks = ["AMZN", "NVDA", "AAPL", "META", "TSLA"]



def calculation(stocks, lambdaRiskAversion, minWeight):
    stockInfo = []
    returnsMatrix = []
    returnsVector = []
    for stock in stocks:
        print("fetching data for: ", stock)
        stockData = getStockInfo(stock)
        if stockData:
            stockInfo.append(stockData)
            returnsMatrix.append(stockData['allPercentages'])
            returnsVector.append(stockData['meanReturn'])

    #returnsMatrix = np.array(returnsMatrix)
    returnsVector = np.array(returnsVector)

    covMatrix = np.cov(returnsMatrix)  # Calculate the full covariance matrix at once


    covMatrix = np.array(covMatrix)



    Q = 0.5 * covMatrix



    Q = cvxopt.matrix(Q) * (10 ** 5)

    weights = cp.Variable(len(stocks))


    #lambdaRiskAversion = 1.25 #* (10 ** -5)

    solutions = cp.Maximize(returnsVector.T @ weights - 0.5 * lambdaRiskAversion * cp.quad_form(weights, Q))
    constraints = [cp.sum(weights) == 1, weights >= minWeight]
    problem = cp.Problem(solutions, constraints)
    problem.solve()

    def testing(Q, weights, covMatrix, returnsMatrix, returnsVector, solutions):
        print("------------------")
        #print(Q.shape)
        print("------------------")
        print(weights)
        print("------------------")
        print(covMatrix)
        print(covMatrix.shape)
        print("------------------")
        print (returnsMatrix, len(returnsMatrix))
        print("------------------")
        #print(matrix)
        print(returnsVector)
        print("------------------")
        print(weights)
        print(Q)
        #print(Q.shape)
        print("------------------")
        print("------------------")
        print (solutions)
        print("------------------")
        print(weights.value)

    #testing(Q, weights, covMatrix, returnsMatrix, returnsVector, solutions)
    print(stocks, lambdaRiskAversion, minWeight)
    print("-----")
    print(problem)
    print("-----")
    print(solutions)
    print(weights)
    print(weights.value)
    optimalStocks = np.array(weights.value)
    print(optimalStocks)
    print(optimalStocks.shape)
    pieChartData = []
    for i in range (len(stocks)):
        pieChartData.append(optimalStocks[i])

    return (pieChartData)

#print(calculation(["AMZN", "NVDA", "AAPL", "META", "TSLA"], 1.25, 0.1))