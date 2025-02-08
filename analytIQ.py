import pymongo
from apiCaller import calculation
from apiCaller import getStockInfo
#import cvxpy as cp


# MongoDB client setup (update your connection string)
import matplotlib.pyplot as plt

import streamlit as st
import numpy as np
import pandas as pd

# Creating a hashmap for stock names and their corresponding stock codes

# Title of the webpage
st.title('Portfolio Optimiser')

stockHashMap = {
    'Apple': 'AAPL',
    'Microsoft': 'MSFT',
    'Amazon': 'AMZN',
    'Tesla': 'TSLA',
    'Meta (Facebook)': 'META',
    'Nvidia': 'NVDA',
    'Netflix': 'NFLX',
    'Alphabet (Google)': 'GOOGL',
    'Adobe': 'ADBE',
    'PayPal': 'PYPL',
    'Intel': 'INTC',
    'Cisco': 'CSCO',
    'Zoom Video Communications': 'ZM',
    'Advanced Micro Devices (AMD)': 'AMD',
    'Qualcomm': 'QCOM',
    'Salesforce': 'CRM',
    'Alphabet (Google) Class A': 'GOOGL',
    'Spotify': 'SPOT',
    'Twitter': 'TWTR',
    'Snapchat': 'SNAP',
    'Pinduoduo': 'PDD',
    'Activision Blizzard': 'ATVI',
    'AMD': 'AMD',
    'Intuit': 'INTU',
    'Shopify': 'SHOP',
    'JD.com': 'JD',
    'Biogen': 'BIIB',
    'ASML': 'ASML',
    'Square': 'SQ',
    'Twilio': 'TWLO',
    'Exxon Mobil': 'XOM',
    'Micron Technology': 'MU',
    'Electronic Arts': 'EA',
    'PayPal Holdings': 'PYPL',
    'AbbVie': 'ABBV',
    'Moderna': 'MRNA',
    'Bristol Myers Squibb': 'BMY',
    'Mercado Libre': 'MELI',
    'Roku': 'ROKU',
    'Xilinx': 'XLNX',
    'Qualcomm': 'QCOM',
    'Altria': 'MO',
    'Illumina': 'ILMN',
    'Applied Materials': 'AMAT',
    'Autodesk': 'ADSK',
    'Pinterest': 'PINS',
    'Lululemon Athletica': 'LULU',
    'PepsiCo': 'PEP',
    'Cognizant': 'CTSH',
    'Workday': 'WDAY',
    'Wynn Resorts': 'WYNN',
    'Mylan': 'MYL',
    'NXP Semiconductors': 'NXPI',
    'Lam Research': 'LRCX',
    'Regeneron Pharmaceuticals': 'REGN',
    'Kroger': 'KR',
    'Palo Alto Networks': 'PANW',
    'Spotify Technology': 'SPOT',
    'Tesla Motors': 'TSLA',
    'Nvidia Corporation': 'NVDA',
    'Fortinet': 'FTNT',
    'Lucid Motors': 'LCID',
    'Zscaler': 'ZS',
    'Sea Limited': 'SE',
    'Palantir Technologies': 'PLTR',
    'Lumen Technologies': 'LUMN',
    'Ciena': 'CIEN',
    'Okta': 'OKTA',
    'Datadog': 'DDOG',
    'Illumina Inc.': 'ILMN',
    'Docusign': 'DOCU',
    'Uber Technologies': 'UBER',
    'Zoom Video': 'ZM',
    'Cloudflare': 'NET',
    'Unity Software': 'U',
    'Datadog Inc.': 'DDOG',
    'Baidu': 'BIDU',
    'Expedia Group': 'EXPE',
    'Charles Schwab Corporation': 'SCHW',
    'Mosaic': 'MOS',
    'VeriSign': 'VRSN',
    'Align Technology': 'ALGN',
    'Boston Scientific': 'BSX',
    'Xcel Energy': 'XEL',
    'JD Health International': 'JD',
    'Cloudflare': 'NET',
    'Dropbox': 'DBX',
    'RingCentral': 'RNG',
    'Bill.com': 'BILL',
    'Square Inc.': 'SQ',
    'Etsy': 'ETSY',
    'Shopify Inc.': 'SHOP',
    'Snowflake Inc.': 'SNOW',
    'Shopify': 'SHOP',
    'Atlassian': 'TEAM',
    'Wayfair': 'W',
    'Square (now Block)': 'SQ',
    'Crowdstrike': 'CRWD',
    '3D Systems': 'DDD',
    'SiriusXM': 'SIRI',
    'Illumina': 'ILMN'
}



def graphTest():
    chart_data = pd.DataFrame(
        np.random.randn(20, 3),
        columns=['a', 'b', 'c'])

    st.line_chart(chart_data)
    st.dataframe(chart_data)


def mapTest():
    map_data = pd.DataFrame(
        np.random.randn(1000, 2) / [50, 50] + [37.76, 152.4],
        columns=['lat', 'lon']
    )
    st.map(map_data)
#mapTest()
#graphTest()

def diversification():

    diversificationMin = st.slider("whats the minimal percentage you want invested in each stock?", 1, 10, 5)
    st.write("your minimal diversification percentage is: ", diversificationMin)

    return diversificationMin * 0.01

divMin = diversification()

def riskAversion():
    lambdaRiskAversionParameter = st.slider("Shift this parameter to alter the portfolio focus between maximising returns and minimising risk", 2.00, 5.00, 3.50)
    st.write("your risk aversion parameter is: ",  lambdaRiskAversionParameter)

    return lambdaRiskAversionParameter

lrap = riskAversion()

def divMinDisplay(dm, lrap):
    st.write(f"It is: {dm}")
    st.write(f"It is {lrap}")

divMinDisplay(divMin,lrap)


def stockAmount():
    options = 0
    amount = [5, 6, 7, 8, 9, 10]
    
    st.session_state.investmentArray = []
    #investmentArray must be declared like this so values can be stored during reruns

    options = st.selectbox(
        "How many stocks would you like to invest in?",
        amount)
    
    "you chose: ", options

    df = pd.DataFrame({
        "stocks": list(stockHashMap.keys())
    })

    if 'symbolArray' not in st.session_state:
        st.session_state.symbolArray = ['AAPL'] 

    
    selectedStocks = st.multiselect(
        "choose em", 
        df["stocks"]
    )

    if (len(selectedStocks)) > options:
        st.warning("too many!!")
        selectedStocks = selectedStocks[:options]

    if selectedStocks:

        st.session_state.investmentArray.extend(selectedStocks)
        

        st.write("current stock selection: ", st.session_state.investmentArray)
    else:
        st.write("No stocks selected")

    prevStocks = st.session_state.symbolArray.copy()

    for stock in selectedStocks:
        # extend adds new parts bit by bit
        # append adds the entire current state as well as the new addition
        x = ''.join(stockHashMap[stock])
        if x not in st.session_state.symbolArray:
            st.session_state.symbolArray.append(x)

    for stock in prevStocks:
        if stock not in[stockHashMap[stock] for stock in selectedStocks]:
            st.session_state.symbolArray.remove(stock)
    #print(stock, x)
    #print("stock symbols:", st.session_state.symbolArray)
    #print("stock symbols:", st.session_state.investmentArray)
    qp = np.array(st.session_state.symbolArray)
    pq = np.array(st.session_state.investmentArray)
    #print(qp)
    #print(pq)

    return qp, pq, options

sArray, iArray, amount = stockAmount()

print(sArray)
print(iArray)
print(amount)
        
#stockAmount()

def pieChart(optimalStocks):
    sizes = 100 * optimalStocks
    labels = iArray

    fig1, ax1 = plt.subplots()
    ax1.pie(optimalStocks, labels=labels, autopct='%1.1f%%',
            shadow=True, startangle=90)
    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

    st.pyplot(fig1)

#pieChart(calculation(sArray, lrap, divMin))


prompt = st.text_input("stock of interest?")
st.write(f"the stock is: {prompt}")



print (prompt)

#BULK:

if st.button("optimise stocks"):
    print (getStockInfo(sArray))

    if len(iArray) != amount:
        print((len(iArray)), amount)
        st.write(f"you didnt choose the amount of stocks you selected")
    elif getStockInfo(sArray) == "None":
        st.write(f"API call limit has been reached, try again later")

    else:
        pieChart(calculation(sArray, lrap, divMin))