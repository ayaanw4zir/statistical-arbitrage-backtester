# Statistical Arbitrage Backtester

A Python pairs-trading backtester that tests whether two related stocks show a mean-reverting relationship and evaluates a simple long-short trading strategy.

The current example uses Visa (`V`) and Mastercard (`MA`).

## Overview

The project:

- downloads historical stock data using `yfinance`
- measures the correlation between the two stocks
- splits the data into training and test periods to reduce look-ahead bias
- uses OLS regression to estimate the relationship between the two stocks
- tests the training spread using the Augmented Dickey-Fuller test and an Engle-Granger cointegration test
- recalculates rolling alpha and beta values using the previous 60 trading days
- creates rolling z-score trading signals
- tests several entry thresholds
- includes transaction costs
- evaluates cumulative return, Sharpe ratio and maximum drawdown
- compares the strategy with buy-and-hold benchmarks

## Data Split

Historical prices are downloaded from 2018 to the end of 2025.

- Training period: 2018-01-01 to 2022-12-31
- Test period: 2023-01-01 to 2025-12-31

The training period is used for the initial statistical tests, while strategy performance is evaluated on the later test period.

## Strategy Logic

The regression models stock A as a function of stock B:

```text
A = alpha + beta * B
```

The spread is the difference between the actual value of A and the value predicted by the regression.

During the test period, alpha and beta are recalculated using the previous 60 trading days. A rolling z-score then measures how far the current spread is from its recent mean.

Trading rules:

- z-score above the entry threshold: short the spread
- z-score below the negative entry threshold: long the spread
- absolute z-score below 0.5: close the position
- otherwise: keep the previous position

Signals are shifted forward by one day so that a signal calculated using today's prices is applied to the following day's return.

## Threshold Testing

The backtester compares entry thresholds of:

```text
1.5, 2.0, 2.5, 3.0
```

For each threshold it reports:

- cumulative return
- Sharpe ratio
- maximum drawdown
- number of position changes

In the current V/MA test period, the 3.0 threshold was the strongest of the tested thresholds, while lower thresholds traded more frequently and produced negative returns. This result is specific to this sample and should not be treated as a universally optimal parameter.

## Benchmarking

The strategy is also compared with buy-and-hold performance for both stocks over the same test period.

This comparison provides context, although a long-short pairs strategy has a different risk profile from simply holding either stock.

## Limitations

This is a simplified educational backtester. In particular:

- the pair-return calculation is a simplified hedge-ratio return rather than a fully capital-normalised portfolio
- transaction costs are charged when the position changes, but not for smaller rebalancing caused by changes in the rolling hedge ratio
- results are based on historical data and do not imply future profitability
- testing several thresholds on the same test period can introduce parameter-selection bias

## Requirements

Install the required libraries with:

```bash
pip install -r requirements.txt
```

## Run

```bash
python Main.py
```

The script prints the main statistical tests, threshold results and benchmark metrics, and displays plots for the rolling z-score, cumulative returns, drawdown and the strategy versus buy-and-hold benchmarks.
