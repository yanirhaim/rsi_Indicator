# Relative strength index
# Created by Yanir Haim

# Libraries required
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import requests
import json

ticker = 'AAPL'  # Add ticker for looking data
period = 14  # Value of the RSI period

# Get data from URL
data = requests.get("https://fmpcloud.io/api/v3/historical-price-full/"+ ticker +"?serietype=line&apikey=demo")
# Load the Content of the data that is in a json file
data = json.loads(data.content)
data = data['historical']  # Because it is in a dictionary, we have to look for the 'historical' content

dates = []  # List where we are going to save the dates values
close = []  # List where we are going to save the close values

# ForLoop for saving the data into the lists
for item in data:
    dates.append(pd.to_datetime(item['date']))  # getting the date as a pandas time-series
    close.append(float(item['close']))  # getting the close price as a float

# Reversing the content of the list, because we don't want the last close as our first value
close.reverse()
dates.reverse()

# Creating a pandas DataFrame with the values
df = pd.DataFrame(close, index=dates, columns=['Close'])

# Creating a function where it will store the value of change per day, but just the ones that are increasing, on a df
def upward_c(close_p):
    mask = (close_p - close_p.shift(1)) > 0  # Condition for looking just increasing change per day
    v1 = close_p - close_p.shift(1)  # In case it is increasing it will store this value
    v2 = 0  # In case it is not increasing it will store this value
    df['Upward change'] = np.where(mask, v1, v2)  # Assigning the condition to the df, to assign the values

upward_c(df['Close'])  # Calling the function with the Close Values

# Creating a function where it will store the value of change per day, but just the ones that are decreasing, on a df
def downward_c(close_p):
    mask = (close_p - close_p.shift(1)) < 0  # Condition for looking just decreasing change per day
    v1 = (close_p - close_p.shift(1))*-1  # In case it is decreasing it will store this value
    v2 = 0  # In case it is not decreasing it will store this value
    df['Downward change'] = np.where(mask, v1, v2)  # Assigning the condition to the df, to assign the values

downward_c(df['Close'])  # Calling the function with the Close Values

# Creating a function where it return an average change in relationship with the period, returning a list of values
def av_m(change):
    x = 1
    y = 0
    f_value = 0
    avm = []
    while y != period:
        avm.append(np.nan)
        y += 1
    while x != period+1:
        f_value += change[x]
        x += 1
    f_value = f_value/period
    avm.append(f_value)
    for up_ch in change[period+1:]:
        avm.append(((f_value*(period-1))+up_ch)/period)
        f_value = ((f_value*(period-1))+up_ch)/period
    return avm

df['Average UM'] = av_m(df['Upward change'])  # Getting the average upward movement values and storing them on a df
df['Average DM'] = av_m(df['Downward change'])  # Getting the average downward movement values and storing them on a df

df['RS'] = df['Average UM']/df['Average DM']  # Getting the Relative Strength, and storing the values on a df

# Function to obtain the Relative Strength index from the RS values, and returning a list.
def rsi(rs):
    x = 0
    rsi_l = []
    while x != period:
        rsi_l.append(np.nan)
        x += 1
    for val in rs[period:]:
        rsi_l.append(100-(100/(val+1)))

    return rsi_l

df['RSI'] = rsi(df['RS'])  # Storing the list of values of the RSI on a df

# The next part is to create a function wich allow as to know if whats the status of the stock, for this we would define like this:
# 10 means Overbought 
# 11 means UpwardTrend
# 20 means Oversold
# 22 means DownwardTrend
# 90 for value we are not going to work (Nan)
 
def status(value):
    # Creating a df with the RSI with a condition
    mask = (value > 70)  # Condition where it only works with the values greater than 70
    v1 = 10  # If the value is greter than 70, the value changes to 10
    v2 = value  # If not, it will remain the same
    df['Status'] = np.where(mask, v1, v2)  # Creates the df with the conditions 

    # Function to delete all the Nan values from the df, wich has a relationship with the period
    x = 0
    while x != period:
        df['Status'][x] = 90
        x += 1 

    # For loop to find the values that are below 30 and assign them a value of 20, in case they aren't, it will remain the same
    x = 0 
    for item in df['Status']:
        if item == 10:
            df['Status'][x] = item
            x += 1
        elif item < 30:
            df['Status'][x] = 20
            x += 1
        else:
            df['Status'][x] = item
            x += 1

    # For loop to find the trend of the values that are between 70 and 30
    # The For loop works like this, if the current value is 0, 10 or 20 it will reamain the same 
    # If the values are between, this are the conditions:
    # If the value is not 10, but the previous value was 10, then we assign that value with 22, wich means downward
    # If the value is not 10, but the previuos value was 22, then we assign that value with 22, wich means it continous the downward
    # If the value is not 20, but the previous value was 20, then we assign that value with 11, wich means upward trend
    # If the value is not 20, but the previous value was 11, then we assign that value with 11, wich means it continous the upward
    # In case the non of the conditions works, then we would assign the variable with 90
    x = 0
    for item in df['Status']:
        if item == 90:
            df['Status'][x] = 90
            x += 1
        elif item == 10:
            df['Status'][x] = item
            x += 1
        elif item == 20:
            df['Status'][x] = item
            x += 1
        elif (item != 10) & (df['Status'][x-1] == 10):
            df['Status'][x] = 22
            x += 1
        elif (item != 10) & (df['Status'][x-1] == 22):
            df['Status'][x] = 22
            x += 1
        elif (item != 20) & (df['Status'][x-1] == 20):
            df['Status'][x] = 11
            x += 1
        elif (item != 20) & (df['Status'][x-1] == 11):
            df['Status'][x] = 11
            x += 1
        else: 
            df['Status'][x] = 90
            x += 1

status(df['RSI']) # Calling the function to get the status

# Graphing data
# Values for creating a dividing line at the value of 70
x_values_70 = [df.index[0], df.index[-1]]
y_values_70 = [70, 70]

# Values for creating a dividing line ar the value of 30
x_values_30 = [df.index[0], df.index[-1]]
y_values_30 = [30, 30]

# We create a variable call status, where we plug the last value of the status df, and see what does it mean
if df['Status'][-1] == 10:
    status = "Overbought"
elif df['Status'][-1] == 20:
    status = "Oversold"
elif df['Status'][-1] == 11:
    status = "In the middle of an UPWARD TREND"
elif df['Status'][-1] == 22:
    status = "In the middle of a DOWNWARD TREND"
else:
    status = "IDK"

print("------------------------------------------------------------")
print("Status: {}".format(status)) # Printing the status of the stock
print("------------------------------------------------------------")
print(df)  # Printing the dataFrame

# Plotting the RSI Values, with the 2 dividing lines
df['RSI'].plot(figsize=(14,5))
plt.plot(x_values_70, y_values_70, color='red', linestyle='--')
plt.plot(x_values_30, y_values_30, color='green', linestyle='--')

plt.show()  # Showing the graph
