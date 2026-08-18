# Factor Metric Semantics

Apply the artifact's own schema and labels first. Use these rules when the matching metric is
present; never synthesize a missing value.

## Return And Drawdown

- Cross-sectional net return is the portfolio return after the artifact's modeled fees and costs.
- `cs_return` is annualized as `365 * mean(net_r)` under the current calculation contract.
- `cs_max_drawdown` is a signed negative drawdown computed from log NAV. A more negative value is a
  deeper drawdown; do not silently convert it to a positive magnitude.
- Compare Sharpe, return, and drawdown over the same declared window. Do not mix metrics from
  different scopes or windows.

## Turnover

- Factor cross-sectional turnover is `mean(sum(abs(delta weight)))`.
- It is not divided by two. Do not compare the number directly with Strategy daily turnover without
  naming the convention difference.
- High turnover is evidence of implementation pressure, not proof that realized performance will
  fail. Test fee sensitivity and signal smoothing as controlled experiments.

## Signal Persistence

- `factor_autocorr_lag1` is the lag-one Pearson correlation of the daily cross-sectional
  equal-weight signal mean.
- Fewer than ten valid days produces null, not zero.
- High persistence can support lower turnover but can also indicate slow-moving style exposure.
  Interpret it with the charts and factor mechanism.

## Cross-Sectional Evidence

- Group ordering and spread matter more than a single headline score.
- Monotonic group returns support an ordering mechanism. A result driven only by one extreme group
  is more fragile.
- Inspect long and short legs separately. A neutral spread may be dominated by only one side.
- Small or irregular daily cross sections reduce confidence in quantile and correlation evidence.

## Grade And Score

- Grade or score is QuantAI-relayed evidence.
- It is not a promotion decision, research approval, or guarantee of robustness.
- Explain the underlying metrics and evidence gaps instead of treating the grade as the conclusion.
