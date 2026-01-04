# Quality scorecards

This repo now treats **quality** as a first-class artifact: it’s not enough to “run the pipeline” — we want quick signals that outputs are *usable*.

## Cluster quality

If you have noisy clusters (over-merged topics, fragmented groups, unstable assignments), use:

```bash
detectlab quality cluster --data <dataset.parquet> --out <runs/<run_id>/reports/quality/>
```

Options:
- `--cluster-col` (default: `cluster`)
- `--label-col` (optional): enables ARI/NMI (requires ground-truth)
- `--feature-col <col>` repeatable (optional): explicitly choose feature columns
- `--sample-n <N>` for speed

Outputs:
- `cluster_quality.json`
- `cluster_quality.md`

### Notes on interpretation
- Silhouette near **1** = clean separation; near **0** = overlap; negative suggests misassignment.
- Davies–Bouldin lower is better; Calinski–Harabasz higher is better (dataset-dependent).
- ARI/NMI only make sense when you provide a ground-truth label column.

## Next (planned)
- Dataset drift scorecard (train vs eval shift)
- Feature sparsity / leakage checks
- Model calibration + slice stability bundle
