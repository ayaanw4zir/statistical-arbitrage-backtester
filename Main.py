import yfinance as yf #allows me to get historical stock data
import statsmodels.api as sm
from statsmodels.tsa.stattools import adfuller, coint #adfuller test - testing whether the spread behaves like a stationary process or a trend/drift.
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

A = "V"
B = "MA"

tickers = [A,B]

data = yf.download(
    tickers,
    start="2018-01-01",
    end="2026-01-01"
)

prices = data["Close"]

returns = prices.pct_change()  #pct_change() calculates the return on consecutive days

correlation = returns[A].corr((returns[B]))

print("Correlation:", correlation)

train = prices.loc["2018-01-01":"2022-12-31"] #splitting timeline to prevent look-ahead bias
test = prices.loc["2023-01-01":"2025-12-31"]

test_returns = test.pct_change()

Y_train = train[A]
X_train = train[B]
X_train = sm.add_constant(X_train)

model = sm.OLS(Y_train, X_train)
train_results = model.fit() #finds the best alpha and beta etc values to minimise residual (real price - expected price)

rolling_window = 60

rolling_alpha = pd.Series(index=test.index, dtype=float)
rolling_beta = pd.Series(index=test.index, dtype=float)

for date in test.index:

    end_loc = prices.index.get_loc(date)

    Y_window = prices[A].iloc[end_loc - rolling_window:end_loc]
    X_window = prices[B].iloc[end_loc - rolling_window:end_loc]

    X_window = sm.add_constant(X_window)

    model = sm.OLS(Y_window, X_window)
    results = model.fit()

    rolling_alpha.loc[date] = results.params["const"]
    rolling_beta.loc[date] = results.params[B]


spread_train = train_results.resid #calculates spread of expected data compared to real data, smaller residual = better

adf_result = adfuller(spread_train) #many values - p value most important

print("ADF p-value:", adf_result[1])

cointegration_result = coint(train[A], train[B])

print("Cointegration p-value:", cointegration_result[1])

Y_test = test[A]
X_test = test[B]

alpha = rolling_alpha
beta = rolling_beta

spread_test = Y_test - (alpha + beta * X_test)

window = 60

rolling_mean = spread_test.rolling(window).mean()
rolling_std = spread_test.rolling(window).std()
rolling_z_score = (spread_test - rolling_mean) / rolling_std

thresholds = [1.5, 2.0, 2.5, 3.0]

results = []

for entry_threshold in thresholds:

    position = pd.Series(0, index=rolling_z_score.index)

    for i in range(1, len(rolling_z_score)):
        z = rolling_z_score.iloc[i]
        previous_position = position.iloc[i - 1]

        if z > entry_threshold:
            position.iloc[i] = -1
        elif z < -entry_threshold:
            position.iloc[i] = 1
        elif abs(z) < 0.5:
            position.iloc[i] = 0
        else:
            position.iloc[i] = previous_position   #loop that decides on the position, -1 is short, 1 is long, and 0 is neutral.

    pair_returns = test_returns[A] - beta * test_returns[B]
    strategy_returns = position.shift(1) * pair_returns #todays signal is tomorrows return

    position_change = position.diff()
    transaction_costs = abs(0.001 * position_change)

    net_strategy_returns = strategy_returns - transaction_costs

    cumulative_returns = (1 + net_strategy_returns).cumprod()

    mean_return = net_strategy_returns.mean()
    std_return = net_strategy_returns.std()

    sharpe_ratio = (mean_return / std_return) * np.sqrt(252) #return based on volatility (252 trading days)

    running_peak = cumulative_returns.cummax()

    drawdown = (cumulative_returns - running_peak) / running_peak

    max_drawdown = drawdown.min()

    results.append({
        "threshold": entry_threshold,
        "cumulative_return": cumulative_returns.iloc[-1] - 1,
        "sharpe_ratio": sharpe_ratio,
        "max_drawdown": max_drawdown,
        "position_changes": (position.diff() != 0).sum()
    })

results_df = pd.DataFrame(results)

print(results_df)

A_cumulative_returns = (1 + test_returns[A].fillna(0)).cumprod()
B_cumulative_returns = (1 + test_returns[B].fillna(0)).cumprod()

print(A, "Cumulative Return:", A_cumulative_returns.iloc[-1] - 1)
print(B, "Cumulative Return:", B_cumulative_returns.iloc[-1] - 1)

A_sharpe = (test_returns[A].mean() / test_returns[A].std()) * np.sqrt(252)
B_sharpe = (test_returns[B].mean() / test_returns[B].std()) * np.sqrt(252)

A_running_peak = A_cumulative_returns.cummax()
A_drawdown = (A_cumulative_returns - A_running_peak) / A_running_peak
A_max_drawdown = A_drawdown.min()

B_running_peak = B_cumulative_returns.cummax()
B_drawdown = (B_cumulative_returns - B_running_peak) / B_running_peak
B_max_drawdown = B_drawdown.min()

print(A, "Sharpe Ratio:", A_sharpe)
print(A, "Maximum Drawdown:", A_max_drawdown)

print(B, "Sharpe Ratio:", B_sharpe)
print(B, "Maximum Drawdown:", B_max_drawdown)


plt.figure()

plt.plot(rolling_z_score)

plt.axhline(entry_threshold, linestyle="--")
plt.axhline(-entry_threshold, linestyle="--")
plt.axhline(0, linestyle="-")

plt.title("Rolling Z-Score")
plt.xlabel("Date")
plt.ylabel("Z-Score")


plt.figure()

plt.plot(cumulative_returns)

plt.axhline(1, linestyle="--")

plt.title("Cumulative Returns")
plt.xlabel("Date")
plt.ylabel("Growth of £1")


plt.figure()

plt.plot(drawdown)

plt.axhline(0, linestyle="--")

plt.title("Drawdown")
plt.xlabel("Date")
plt.ylabel("Drawdown")


plt.figure()

plt.plot(cumulative_returns, label="Pairs Strategy")
plt.plot(A_cumulative_returns, label=A)
plt.plot(B_cumulative_returns, label=B)

plt.title("Strategy vs Buy and Hold")
plt.xlabel("Date")
plt.ylabel("Growth of £1")

plt.legend()

plt.show()
