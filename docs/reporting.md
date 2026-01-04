# Reporting (D-0006)

D-0006 introduces a stitched, operator-friendly **Final Report** generator that summarizes:

- the run identity + artifact inventory
- FeatureLab v0 summary (windows/groups/strict past-only)
- BaselineLab performance (if baselines were executed)
- narrative interpretation aligned with SKYNET / SPACING GUILD fiction layer
- explicit validation status (including deferred validation paths)

## Generate the final report

```bash
uv run detectlab report generate -c <CONFIG.yaml> --run-id <RUN_ID>
```

By default, this will refuse to overwrite an existing report.
To overwrite:

```bash
uv run detectlab report generate -c <CONFIG.yaml> --run-id <RUN_ID> --force
```

## Outputs

Written under:

- `runs/<RUN_ID>/reports/final_report.md`
- `runs/<RUN_ID>/reports/insights.json`

The run `manifest.json` is updated to include these artifacts.

## When baselines are missing

The final report can be generated **without** baseline artifacts.
In that case, it will clearly state that performance is unknown and will include commands to run baselines later.

## Parquet note (D-0005+)

Parquet is mandatory. If you have legacy CSV artifacts, migrate them first:

```bash
uv run detectlab dataset parquetify -c <CONFIG.yaml> --run-id <RUN_ID> --force
```
