# Factor Diagnosis And Experiments

Start with evidence, then explain mechanisms. Avoid reverse-engineering a story from a grade.

## Diagnostic Questions

1. Is the return spread monotonic across groups or concentrated in one tail?
2. Do both long and short legs contribute, or does one leg carry the result?
3. Is performance broadly distributed across time or concentrated in a short episode?
4. Does drawdown coincide with market, volatility, liquidity, or coverage changes visible in the
   evidence?
5. Is turnover consistent with the intended economic horizon?
6. Are missingness and cross-sectional size sufficient for the reported statistics?
7. Could the signal be a proxy for size, liquidity, momentum, value, or market exposure?

## Evidence Ladder

- **Observed:** quote exact trusted metrics, chart patterns, and manifest status.
- **Inference:** state the mechanism that could connect those observations.
- **Alternative:** name at least one plausible competing explanation for consequential claims.
- **Experiment:** define the smallest controlled test that distinguishes them.

Use causal language only when the supplied evidence supports causality. Backtest association alone
does not establish a causal mechanism.

## Controlled Experiment Templates

- **Turnover control:** apply one smoothing or rebalance change; expect lower turnover and define the
  maximum acceptable loss in spread or Sharpe.
- **Tail robustness:** change only the selection breadth; expect the same direction with less tail
  concentration if the mechanism is broad.
- **Direction test:** invert only the factor direction; expect degradation if the claimed direction
  is real.
- **Coverage test:** tighten only the data-validity threshold; expect stability if missingness is not
  driving the result.
- **Style control:** neutralize or stratify one suspected style; expect residual spread if the factor
  has incremental content.
- **Window stability:** rerun the same definition on a distinct declared window when the product
  workflow supports it. Do not call current external-agent evidence OOS.

For each proposal, state the independent variable, expected change, confirmation metric, and
tradeoff. Prefer two or three high-information tests over a long optimization list.

## Decision Language

- **Reject:** evidence contradicts the mechanism or integrity is unreliable.
- **Investigate:** important evidence is missing or alternatives remain unresolved.
- **Revise:** a specific mechanism-level change is justified.
- **Hand off:** evidence is adequate for a user-confirmed Strategy experiment, not for automatic
  promotion.
