# Statistical Arbitrage Backtester

I built this project to learn more about pairs trading and how statistical methods can be used to test relationships between stocks.

The current version uses Visa (`V`) and Mastercard (`MA`) and tests whether changes in the relationship between their prices can be used to generate trading signals.

## How it works

The program downloads historical stock data from 2018 to 2025 using `yfinance`.

I split the data into:

- Training data: 2018 to 2022
- Test data: 2023 to 2025

The training data is used to test the relationship between the two stocks, while the later data is used to test the trading strategy.

I use OLS regression to model the relationship:

```text
A = alpha + beta * B
```

The difference between the actual price of A and the price predicted by the regression creates the spread.

I then use:

- correlation to see how closely the stocks move together
- the ADF test to check whether the spread is stationary
- a cointegration test to check for a long-term relationship between the two stocks

During the test period, the regression is recalculated using the previous 60 trading days so that alpha and beta can change over time.

A rolling z-score is then used to measure how far the spread is from its recent average.

## Trading rules

The strategy tests entry thresholds of `1.5`, `2.0`, `2.5` and `3.0`.

- if the z-score is above the entry threshold, the strategy shorts the spread
- if the z-score is below the negative entry threshold, the strategy goes long the spread
- if the z-score returns within `0.5` of zero, the position is closed
- otherwise, the previous position is kept

The signal is shifted by one day so that today's signal is applied to the next day's return.

I also included a simple transaction cost whenever the position changes.

## Results

For each threshold, the program calculates:

- cumulative return
- Sharpe ratio
- maximum drawdown
- number of position changes

For Visa and Mastercard, the `3.0` threshold performed best during the 2023-2025 test period.

It produced approximately:

- 5.9% cumulative return
- 0.55 Sharpe ratio
- -3.6% maximum drawdown

The strategy is also compared with simply buying and holding Visa and Mastercard over the same period.

Buy-and-hold produced much higher returns, but the pairs strategy had a much smaller maximum drawdown.

## Libraries used

- Python
- pandas
- NumPy
- Matplotlib
- statsmodels
- yfinance

## Notes

This is a simplified backtester and was built as a learning project. The results are based on historical data and do not mean the strategy would make money in the future.
