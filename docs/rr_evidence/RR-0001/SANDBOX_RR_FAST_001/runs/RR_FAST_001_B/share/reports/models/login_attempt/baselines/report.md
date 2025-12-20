# Baseline Report — login_attempt

- run_id: `RR_FAST_001_B`
- target_fpr: 0.01
- rows: train=156, time_eval=22, user_holdout=24

## Summary table

| label | model | train PR-AUC | train thr | train FPR | train recall | time_eval PR-AUC | time_eval FPR | time_eval recall | user_holdout PR-AUC | user_holdout FPR | user_holdout recall |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| label_replicators | logreg | 0.7125 | 0.972054 | 0.0066 | 0.4000 | 0.0588 | 0.0476 | 0.0000 | 0.1250 | 0.0435 | 0.0000 |
| label_replicators | rf | 0.8769 | 0.211416 | 0.0066 | 0.8000 | 0.0455 | 0.0476 | 0.0000 | 0.0833 | 0.0000 | 0.0000 |
| label_the_mule | logreg | 0.2679 | 0.997289 | 0.0065 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| label_the_mule | rf | 0.7500 | 0.613333 | 0.0000 | 0.5000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| label_the_chameleon | logreg | 1.0000 | 0.17463 | 0.0065 | 1.0000 | 0.0526 | 0.0000 | 0.0000 | 0.0000 | 0.0833 | 0.0000 |
| label_the_chameleon | rf | 1.0000 | 0.0833333 | 0.0065 | 1.0000 | 0.0455 | 0.0952 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |

## Per-label metrics

### label_replicators
- **logreg**
  - train (threshold selection): PR-AUC=0.7125, thr=0.972054, FPR=0.0066, recall=0.4000
  - threshold candidates (train, FPR<=target):
    | rank | thr | fpr | recall | precision |
    |---:|---:|---:|---:|---:|
    | 1 | 0.929752 | 0.0066 | 0.6000 | 0.7500 |
    | 2 | 0.972054 | 0.0066 | 0.4000 | 0.6667 |
    | 3 | 0.987338 | 0.0000 | 0.4000 | 1.0000 |
  - time_eval (apply train threshold): PR-AUC=0.0588, ROC-AUC=0.2381, thr=0.972054, FPR=0.0476, recall=0.0000
  - user_holdout (apply train threshold): PR-AUC=0.1250, ROC-AUC=0.7174, thr=0.972054, FPR=0.0435, recall=0.0000
  - top_features:
    - cross__checkout_attempt__ip_6h__success_rate: +0.709042
    - cross__checkout_attempt__user_6h__success_rate: +0.709042
    - cross__checkout_attempt__device_6h__success_rate: +0.709042
    - device_24h__success_rate: -0.60621
    - user_24h__success_rate: -0.60621
    - ip_24h__success_rate: -0.60621
    - cross__checkout_attempt__device_6h__payment_value_sum: -0.47016
    - cross__checkout_attempt__user_6h__payment_value_sum: -0.47016
    - cross__checkout_attempt__ip_6h__payment_value_sum: -0.47016
    - ip_6h__failure_cnt: +0.323459
- **rf**
  - train (threshold selection): PR-AUC=0.8769, thr=0.211416, FPR=0.0066, recall=0.8000
  - threshold candidates (train, FPR<=target):
    | rank | thr | fpr | recall | precision |
    |---:|---:|---:|---:|---:|
    | 1 | 0.211416 | 0.0066 | 0.8000 | 0.8000 |
    | 2 | 0.60205 | 0.0000 | 0.8000 | 1.0000 |
    | 3 | 0.616667 | 0.0000 | 0.6000 | 1.0000 |
  - time_eval (apply train threshold): PR-AUC=0.0455, ROC-AUC=0.1667, thr=0.211416, FPR=0.0476, recall=0.0000
  - user_holdout (apply train threshold): PR-AUC=0.0833, ROC-AUC=0.5435, thr=0.211416, FPR=0.0000, recall=0.0000
  - top_features:
    - cross__checkout_attempt__ip_24h__payment_value_sum: 0.0248529
    - cross__checkout_attempt__device_24h__payment_value_mean: 0.0221501
    - device_24h__challenge_rate: 0.0220502
    - cross__checkout_attempt__device_24h__payment_value_sum: 0.0215047
    - user_1h__uniq_ip_hash_cnt: 0.0212345
    - user_1h__uniq_device_fingerprint_hash_cnt: 0.0212216
    - cross__checkout_attempt__ip_6h__payment_value_sum: 0.0208375
    - ip_24h__challenge_rate: 0.0208224
    - user_24h__challenge_rate: 0.0198675
    - user_24h__success_rate: 0.0180584

### label_the_mule
- **logreg**
  - train (threshold selection): PR-AUC=0.2679, thr=0.997289, FPR=0.0065, recall=0.0000
  - threshold candidates (train, FPR<=target):
    | rank | thr | fpr | recall | precision |
    |---:|---:|---:|---:|---:|
    | 1 | 0.997289 | 0.0065 | 0.0000 | 0.0000 |
  - time_eval (apply train threshold): PR-AUC=0.0000, ROC-AUC=0.0000, thr=0.997289, FPR=0.0000, recall=0.0000
  - user_holdout (apply train threshold): PR-AUC=0.0000, ROC-AUC=0.0000, thr=0.997289, FPR=0.0000, recall=0.0000
  - top_features:
    - cross__checkout_attempt__ip_24h__success_rate: +0.828067
    - cross__checkout_attempt__user_24h__success_rate: +0.828067
    - cross__checkout_attempt__device_24h__success_rate: +0.828067
    - device_6h__success_rate: +0.575146
    - user_6h__success_rate: +0.575146
    - ip_6h__success_rate: +0.575146
    - device_24h__failure_rate: -0.474404
    - ip_24h__failure_rate: -0.474404
    - user_24h__failure_rate: -0.474404
    - user_24h__uniq_device_fingerprint_hash_cnt: -0.446069
- **rf**
  - train (threshold selection): PR-AUC=0.7500, thr=0.613333, FPR=0.0000, recall=0.5000
  - threshold candidates (train, FPR<=target):
    | rank | thr | fpr | recall | precision |
    |---:|---:|---:|---:|---:|
    | 1 | 0.613333 | 0.0000 | 0.5000 | 1.0000 |
  - time_eval (apply train threshold): PR-AUC=0.0000, ROC-AUC=0.0000, thr=0.613333, FPR=0.0000, recall=0.0000
  - user_holdout (apply train threshold): PR-AUC=0.0000, ROC-AUC=0.0000, thr=0.613333, FPR=0.0000, recall=0.0000
  - top_features:
    - user_24h__attempt_cnt: 0.0681459
    - device_24h__success_cnt: 0.0671785
    - user_24h__success_cnt: 0.0657152
    - device_24h__attempt_cnt: 0.0622914
    - ip_24h__attempt_cnt: 0.0579711
    - ip_24h__success_cnt: 0.0382995
    - cross__checkout_attempt__device_24h__payment_value_sum: 0.0239954
    - device_1h__uniq_user_id_cnt: 0.0234039
    - ip_1h__uniq_device_fingerprint_hash_cnt: 0.0183506
    - cross__checkout_attempt__user_24h__payment_value_sum: 0.0173638

### label_the_chameleon
- **logreg**
  - train (threshold selection): PR-AUC=1.0000, thr=0.17463, FPR=0.0065, recall=1.0000
  - threshold candidates (train, FPR<=target):
    | rank | thr | fpr | recall | precision |
    |---:|---:|---:|---:|---:|
    | 1 | 0.17463 | 0.0065 | 1.0000 | 0.5000 |
    | 2 | 0.995346 | 0.0000 | 1.0000 | 1.0000 |
  - time_eval (apply train threshold): PR-AUC=0.0526, ROC-AUC=0.1667, thr=0.17463, FPR=0.0000, recall=0.0000
  - user_holdout (apply train threshold): PR-AUC=0.0000, ROC-AUC=0.0000, thr=0.17463, FPR=0.0833, recall=0.0000
  - top_features:
    - user_1h__success_rate: +0.538512
    - ip_1h__success_rate: +0.538512
    - device_1h__success_rate: +0.538512
    - cross__checkout_attempt__user_6h__event_cnt: +0.359927
    - cross__checkout_attempt__device_6h__event_cnt: +0.359927
    - cross__checkout_attempt__ip_6h__event_cnt: +0.359927
    - cross__checkout_attempt__user_6h__success_cnt: +0.359927
    - cross__checkout_attempt__ip_6h__success_cnt: +0.359927
    - cross__checkout_attempt__device_6h__success_cnt: +0.359927
    - ip_6h__failure_rate: +0.257251
- **rf**
  - train (threshold selection): PR-AUC=1.0000, thr=0.0833333, FPR=0.0065, recall=1.0000
  - threshold candidates (train, FPR<=target):
    | rank | thr | fpr | recall | precision |
    |---:|---:|---:|---:|---:|
    | 1 | 0.0833333 | 0.0065 | 1.0000 | 0.5000 |
    | 2 | 0.59 | 0.0000 | 1.0000 | 1.0000 |
  - time_eval (apply train threshold): PR-AUC=0.0455, ROC-AUC=0.3571, thr=0.0833333, FPR=0.0952, recall=0.0000
  - user_holdout (apply train threshold): PR-AUC=0.0000, ROC-AUC=0.0000, thr=0.0833333, FPR=0.0000, recall=0.0000
  - top_features:
    - ip_1h__success_rate: 0.0395412
    - device_1h__success_rate: 0.0382477
    - user_1h__success_cnt: 0.0320291
    - user_1h__success_rate: 0.0309077
    - ip_24h__failure_rate: 0.0303827
    - cross__checkout_attempt__user_6h__success_cnt: 0.0302423
    - device_24h__success_cnt: 0.0295871
    - cross__checkout_attempt__user_6h__payment_value_sum: 0.0275941
    - device_24h__failure_rate: 0.0265987
    - cross__checkout_attempt__device_6h__success_cnt: 0.025808

