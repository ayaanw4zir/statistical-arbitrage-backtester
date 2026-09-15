# Statistical Arbitrage Backtester

I built this project to learn how pairs trading works and how statistical methods can be used to test whether two stocks have a relationship that may be suitable for mean-reversion trading.

The current version uses Visa (`V`) and Mastercard (`MA`).

## Project idea

Pairs trading focuses on the **relationship between two stocks** rather than trying to predict whether one stock will simply go up or down.

If two stocks usually move together, but their relationship temporarily moves far away from normal, the strategy assumes that the difference may later move back towards its usual level.

The program:

- downloads historical stock prices
- measures the relationship between Visa and Mastercard
- tests whether their spread appears mean-reverting
- creates rolling z-score trading signals
- tests several entry thresholds
- includes transaction costs
- measures return, Sharpe ratio and drawdown
- compares the strategy with buying and holding each stock

## Data

Historical closing prices are downloaded using `yfinance` from 2018 to the end of 2025.

The data is split into:

- **Training period:** 2018-2022
- **Test period:** 2023-2025

The training period is used for the initial statistical tests. The later period is then used to test how the strategy would have performed on data that was not part of those initial tests.

## Measuring the relationship

### Correlation

I calculate the correlation between the daily returns of Visa and Mastercard.

Correlation measures how closely two variables move together. A value close to `1` means their daily movements are strongly related, while a value closer to `0` means there is less of a relationship.

Visa and Mastercard have a high return correlation of approximately `0.91`, which makes them a reasonable pair to investigate further.

Correlation alone is not enough for pairs trading because two stocks can move together in the short term without having a stable long-term price relationship.

### OLS regression

I use Ordinary Least Squares regression to estimate the relationship between the two prices:

```text
A = alpha + beta * B
```

where:

- `A` = Visa
- `B` = Mastercard
- `alpha` = constant part of the relationship
- `beta` = how strongly A changes relative to B

The regression gives an estimated Visa price based on Mastercard's price.

The difference between the actual price and the estimated price is the **spread**:

```text
spread = actual A - predicted A
```

A positive spread means Visa is above the level suggested by the regression, while a negative spread means it is below it.

## Testing for mean reversion

### ADF test

The Augmented Dickey-Fuller test is applied to the training spread to test whether it appears **stationary**.

A stationary spread tends to move around a relatively stable level rather than continuously drifting away. This is important because the trading strategy relies on the idea that unusually large movements in the spread may eventually reverse.

The training spread produced an ADF p-value of approximately `0.0016`.

### Cointegration test

I also use an Engle-Granger cointegration test on Visa and Mastercard prices.

Cointegration tests whether two price series appear to share a stable long-term relationship, even if the individual stock prices themselves trend over time.

The cointegration p-value was approximately `0.0078`, providing evidence of a long-term relationship during the training period.

## Rolling model

The relationship between two stocks may change over time, so I do not keep one fixed alpha and beta throughout the test period.

For each date in the test period, the program takes the **previous 60 trading days** and runs another OLS regression.

This produces a rolling alpha and beta for each date.

The current date is excluded from the regression window, so the model only uses information that would have already been available at that point.

The test spread is calculated as:

```text
spread = A - (alpha + beta * B)
```

## Rolling z-score

The program calculates the rolling mean and standard deviation of the spread over 60 trading days.

The z-score is then:

```text
z-score = (spread - rolling mean) / rolling standard deviation
```

The z-score measures how unusual the current spread is compared with its recent history.

- `0` means the spread is close to its recent average
- `+2` means it is about two standard deviations above its recent average
- `-2` means it is about two standard deviations below its recent average

The larger the absolute z-score, the further the relationship has moved away from its recent average.

![Rolling Z-Score](https://raw.githubusercontent.com/ayaanw4zir/statistical-arbitrage-backtester/7bfd0e93e8247cc4220315fdffd809ffc79b6e3a/Figure_1.png)

The dashed lines show the `+3` and `-3` entry levels for the most selective threshold tested.

## Trading strategy

The strategy tests entry thresholds of:

```text
1.5, 2.0, 2.5, 3.0
```

For each threshold:

- z-score above the threshold -> **short the spread**
- z-score below the negative threshold -> **long the spread**
- absolute z-score below `0.5` -> **close the position**
- otherwise -> **keep the previous position**

Positions are stored as:

```text
1 = long spread
-1 = short spread
0 = no position
```

A long spread position expects the spread to rise back towards normal, while a short spread position expects it to fall back towards normal.

The daily pair return is calculated using the rolling hedge ratio:

```text
pair return = return of A - beta * return of B
```

The trading signal is shifted forward by one day so that a signal calculated using today's prices is applied to the following day's return.

A transaction cost of `0.1%` is also applied whenever the position changes.

## Performance measures

For each threshold I calculate:

- **Cumulative return** - total compounded return over the test period
- **Sharpe ratio** - return relative to the volatility of those returns
- **Maximum drawdown** - the largest fall from a previous portfolio peak
- **Position changes** - how often the strategy changed position

### Threshold results

| Entry threshold | Cumulative return | Sharpe ratio | Maximum drawdown | Position changes |
| --- | ---: | ---: | ---: | ---: |
| 1.5 | -4.20% | -0.15 | -12.47% | 44 |
| 2.0 | -3.02% | -0.13 | -12.56% | 27 |
| 2.5 | -2.20% | -0.14 | -10.17% | 17 |
| 3.0 | **+5.90%** | **0.55** | **-3.58%** | **9** |

The `3.0` threshold performed best during this particular 2023-2025 test period. The lower thresholds entered more frequently and produced negative returns.

### Cumulative returns

The graph below shows the growth of £1 for the `3.0` threshold. Flat periods occur when the strategy has no open position.

![Cumulative Returns](https://raw.githubusercontent.com/ayaanw4zir/statistical-arbitrage-backtester/7bfd0e93e8247cc4220315fdffd809ffc79b6e3a/Figure_2.png)

### Drawdown

Drawdown shows how far the strategy is below its previous highest portfolio value. A value of `0` means the strategy is at a peak, while negative values show a fall from that peak.

![Drawdown](https://raw.githubusercontent.com/ayaanw4zir/statistical-arbitrage-backtester/7bfd0e93e8247cc4220315fdffd809ffc79b6e3a/Figure_3.png)

## Comparison with buy and hold

I also compare the strategy with simply buying and holding Visa and Mastercard over the same test period.

| Investment | Cumulative return | Sharpe ratio | Maximum drawdown |
| --- | ---: | ---: | ---: |
| Pairs strategy | +5.90% | 0.55 | -3.58% |
| Visa | +72.97% | 1.08 | -15.01% |
| Mastercard | +67.53% | 1.01 | -16.73% |

Buy-and-hold produced much higher total returns and higher Sharpe ratios during this period, while the pairs strategy had a much smaller maximum drawdown.

![Strategy vs Buy and Hold](https://raw.githubusercontent.com/ayaanw4zir/statistical-arbitrage-backtester/7bfd0e93e8247cc4220315fdffd809ffc79b6e3a/Figure_4.png)

## Libraries used

- pandas
- NumPy
- Matplotlib
- statsmodels
- yfinance
