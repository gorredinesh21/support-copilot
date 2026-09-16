# Slow Databricks jobs
## Investigate
1. Spark UI: stage skew (max task vs median), spill (memory bytes spilled).
2. Ganglia: CPU/IO saturation on executors.
3. Data delta: has the input grown or the partition count changed?
## Fixes
- Skew: salt the hot key or use AQE skew join (`spark.sql.adaptive.skewJoin.enabled=true`).
- Spill: increase executor memory or repartition before wide transformations.
- Small files: run OPTIMIZE (Delta) before the job window.