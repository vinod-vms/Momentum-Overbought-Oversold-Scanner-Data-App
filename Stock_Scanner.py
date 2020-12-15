import streamlit as st
import yfinance as yf
from datetime import datetime
from datetime import timedelta
import mplfinance as mpf
from ta.momentum import RSIIndicator

#dataset

nse50 = 'ADANIPORTS.NS ASIANPAINT.NS AXISBANK.NS BAJAJ-AUTO.NS BAJFINANCE.NS BAJAJFINSV.NS BPCL.NS BHARTIARTL.NS BRITANNIA.NS CIPLA.NS COALINDIA.NS DIVISLAB.NS DRREDDY.NS EICHERMOT.NS GAIL.NS GRASIM.NS HCLTECH.NS HDFCBANK.NS HDFCLIFE.NS HEROMOTOCO.NS HINDALCO.NS HINDUNILVR.NS HDFC.NS ICICIBANK.NS ITC.NS IOC.NS INDUSINDBK.NS INFY.NS JSWSTEEL.NS KOTAKBANK.NS LT.NS M&M.NS MARUTI.NS NTPC.NS NESTLEIND.NS ONGC.NS POWERGRID.NS RELIANCE.NS SBILIFE.NS SHREECEM.NS SBIN.NS SUNPHARMA.NS TCS.NS TATAMOTORS.NS TATASTEEL.NS TECHM.NS TITAN.NS UPL.NS ULTRACEMCO.NS WIPRO.NS'
dataset = nse50

#Fetching and caching data

@st.cache(ttl=60*10)
def get_data():
    return yf.download(dataset, period="max", group_by="ticker")

data = get_data()

#Setting the date in the sidebar

today = datetime.utcnow().date()
now = datetime.utcnow()
time_930am = now.replace(hour=4, minute=1, second=0, microsecond=0)
day_of_week = datetime.weekday(now)

if day_of_week == 5:
    current_date = today - timedelta(days=1)
elif day_of_week == 6:
    current_date = today - timedelta(days=2)
elif day_of_week == 0 and now < time_930am:
    current_date = today - timedelta(days=3)
elif (day_of_week != 5 or day_of_week != 6) and now > time_930am:
    current_date = today
elif (day_of_week != 5 or day_of_week != 6) and now < time_930am:
    current_date = today - timedelta(days=1)

#firstdate in charts
data_for_chart = data.tail(200)
print(data.shape)

# UI

st.title("NSE-50 Momentum Stock Scanner")

st.sidebar.header('Input Variables')
st.sidebar.write('Scans the NSE-50 index stocks. This \'nifty\' tool can be used to identify overbought/oversold stocks using 14-day RSI.  Please change the parameters below. ')


def user_input_features():
    enddate = st.sidebar.text_input("End Date", current_date)
    threshold = st.sidebar.text_input("RSI Threshold", 70)
    comp_op = st.sidebar.selectbox("Comparison Operator", ['greater_than', 'less_than'])
    plot_chart = st.sidebar.selectbox('Plot Chart?', [False, True])
    st.sidebar.write('For example, all NSE-50 stocks with RSI greater than 70 on ', current_date)
    st.sidebar.write('''&copy;[Vinod Mathew Sebastian](https://vinod-vms.netlify.app)''')

    return enddate,threshold,comp_op,plot_chart

enddate,threshold,comp_op,plot_chart = user_input_features()


#Variables
name = 'NSE-50'
enddate = enddate
plot_chart = plot_chart
comp_op = comp_op
threshold = int(threshold)

newList = []
# try ... except is not necessary. Streamlit handles exceptions.
try:

    def stock_scan(ticker_set,name, comp_op, rsi_threshold,enddate, plot_chart=False):
        ''' A tool to scan stocks using RSI. 
        Checks for oversold/overbought conditions. 
        Written by Vinod Mathew Sebastian'''
        dataset = []
        newList = []
        dataset = ticker_set.split(" ")
        if comp_op == "greater_than":
            checking_state_message_0 = 'Overbought?'
            checking_state_message_1 = 'over'
        if comp_op == "less_than":
            checking_state_message_0 = 'Oversold?'
            checking_state_message_1 = 'below'
 # Program Logic               
        message = False
        for stock in dataset:
            data1 = data_for_chart[stock]
            data2 = data1['Adj Close']
            rsii = RSIIndicator(close=data2, window=20, fillna = True)                    
            rs = rsii.rsi()
            rsplt = mpf.make_addplot(rs,panel=1)
            if comp_op == "greater_than":
                condition = rs[enddate]>threshold
            elif comp_op == "less_than":
                condition = rs[enddate]<threshold
            if condition:
                newList.append(stock)
                if plot_chart:
                    fig, axes = mpf.plot(data1, type='candle', volume=True,addplot=rsplt, returnfig=True, main_panel=0,volume_panel=2,panel_ratios=(6,2,1))
                    axes[0].legend("")
                    axes[0].set_title(stock)
                    st.write(fig)
                    if not message:
                        st.write("If you do not like to view the chart(s), change Plot Chart = False in the left pane ")
                        message = True;
                    
        if (newList):
            st.subheader("{} Stocks: RSI {} {}".format(checking_state_message_0, checking_state_message_1, threshold))
            for ech in newList:
                st.write(ech)
            if not plot_chart:
                st.write("If you like to view the chart(s), change Plot Chart = True in the left pane ")
        else:
            st.write("No {} stocks matching your criteria: RSI {} {}".format(name,checking_state_message_1, threshold))

        newList.clear()
# exception handling is done by Streamlit
except KeyError as e:
    st.write(repr(e))
    

stock_scan(dataset, name,comp_op,threshold, enddate,plot_chart)




