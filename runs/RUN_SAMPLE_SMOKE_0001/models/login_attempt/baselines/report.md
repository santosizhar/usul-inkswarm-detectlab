# Baseline Report — login_attempt

- run_id: `RUN_SAMPLE_SMOKE_0001`
- target_fpr: 0.01
- rows: train=8142, time_eval=1184, user_holdout=1476

## Summary table

| label | model | train PR-AUC | train thr | train FPR | train recall | time_eval PR-AUC | time_eval FPR | time_eval recall | user_holdout PR-AUC | user_holdout FPR | user_holdout recall |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| label_replicators | logreg | 0.0508 | 0.854924 | 0.0100 | 0.0191 | 0.0212 | 0.0155 | 0.0000 | 0.0274 | 0.0069 | 0.0000 |
| label_replicators | rf | 0.9999 | 0.11 | 0.0097 | 1.0000 | 0.0246 | 0.0415 | 0.0385 | 0.0273 | 0.0472 | 0.0000 |
| label_the_mule | logreg | 0.0410 | 0.930137 | 0.0099 | 0.0206 | 0.0153 | 0.0129 | 0.0000 | 0.0149 | 0.0165 | 0.0000 |
| label_the_mule | rf | 1.0000 | 0.07 | 0.0096 | 1.0000 | 0.0158 | 0.0214 | 0.0000 | 0.0145 | 0.0316 | 0.0526 |
| label_the_chameleon | logreg | 0.0390 | 0.881367 | 0.0099 | 0.0201 | 0.0323 | 0.0243 | 0.0000 | 0.0204 | 0.0125 | 0.0000 |
| label_the_chameleon | rf | 0.9927 | 0.0853276 | 0.0093 | 0.9866 | 0.0356 | 0.0330 | 0.0323 | 0.0225 | 0.0381 | 0.0000 |

## Per-label metrics

### label_replicators
- **logreg**
  - train (threshold selection): PR-AUC=0.0508, thr=0.854924, FPR=0.0100, recall=0.0191
  - threshold candidates (train, FPR<=target):
    | rank | thr | fpr | recall | precision |
    |---:|---:|---:|---:|---:|
    | 1 | 0.854924 | 0.0100 | 0.0191 | 0.0482 |
    | 2 | 0.857058 | 0.0098 | 0.0191 | 0.0488 |
    | 3 | 0.859043 | 0.0097 | 0.0191 | 0.0494 |
  - time_eval (apply train threshold): PR-AUC=0.0212, ROC-AUC=0.4693, thr=0.854924, FPR=0.0155, recall=0.0000
  - user_holdout (apply train threshold): PR-AUC=0.0274, ROC-AUC=0.4712, thr=0.854924, FPR=0.0069, recall=0.0000
  - top_features:
    - ip_7d__challenge_cnt: -0.732302
    - ip_6h__support_contacted_cnt: -0.67496
    - ip_7d__lockout_cnt: +0.59017
    - ip_7d__uniq_device_fingerprint_hash_cnt: -0.548779
    - ip_7d__uniq_user_id_cnt: -0.548779
    - ip_24h__failure_rate: +0.544562
    - ip_7d__success_rate: -0.53531
    - ip_6h__support_handle_seconds_sum: +0.522663
    - ip_7d__failure_rate: -0.517263
    - ip_24h__success_rate: +0.4833
- **rf**
  - train (threshold selection): PR-AUC=0.9999, thr=0.11, FPR=0.0097, recall=1.0000
  - threshold candidates (train, FPR<=target):
    | rank | thr | fpr | recall | precision |
    |---:|---:|---:|---:|---:|
    | 1 | 0.11 | 0.0097 | 1.0000 | 0.7308 |
    | 2 | 0.113333 | 0.0088 | 1.0000 | 0.7491 |
    | 3 | 0.116667 | 0.0083 | 1.0000 | 0.7600 |
  - time_eval (apply train threshold): PR-AUC=0.0246, ROC-AUC=0.4984, thr=0.11, FPR=0.0415, recall=0.0385
  - user_holdout (apply train threshold): PR-AUC=0.0273, ROC-AUC=0.5679, thr=0.11, FPR=0.0472, recall=0.0000
  - top_features:
    - ip_7d__success_rate: 0.0191165
    - ip_7d__attempt_cnt: 0.0179234
    - user_7d__challenge_rate: 0.0169775
    - user_7d__attempt_cnt: 0.0165963
    - device_7d__success_rate: 0.0164816
    - ip_7d__failure_rate: 0.0164397
    - user_7d__failure_rate: 0.0161391
    - ip_7d__challenge_rate: 0.01613
    - ip_7d__success_cnt: 0.0161232
    - device_7d__success_cnt: 0.0160199

### label_the_mule
- **logreg**
  - train (threshold selection): PR-AUC=0.0410, thr=0.930137, FPR=0.0099, recall=0.0206
  - threshold candidates (train, FPR<=target):
    | rank | thr | fpr | recall | precision |
    |---:|---:|---:|---:|---:|
    | 1 | 0.930137 | 0.0099 | 0.0206 | 0.0244 |
    | 2 | 0.930401 | 0.0098 | 0.0206 | 0.0247 |
    | 3 | 0.930739 | 0.0097 | 0.0206 | 0.0250 |
  - time_eval (apply train threshold): PR-AUC=0.0153, ROC-AUC=0.4859, thr=0.930137, FPR=0.0129, recall=0.0000
  - user_holdout (apply train threshold): PR-AUC=0.0149, ROC-AUC=0.5430, thr=0.930137, FPR=0.0165, recall=0.0000
  - top_features:
    - ip_1h__support_handle_seconds_sum: -2.16658
    - ip_7d__support_wait_seconds_sum: -1.90107
    - ip_1h__support_cost_usd_sum: -1.25577
    - ip_24h__failure_rate: +1.18209
    - ip_7d__failure_cnt: -1.16706
    - user_7d__support_wait_seconds_sum: +1.15894
    - device_7d__support_wait_seconds_sum: +1.15894
    - ip_1h__support_contacted_cnt: +1.08613
    - ip_24h__success_cnt: +0.946227
    - ip_7d__support_handle_seconds_sum: +0.797547
- **rf**
  - train (threshold selection): PR-AUC=1.0000, thr=0.07, FPR=0.0096, recall=1.0000
  - threshold candidates (train, FPR<=target):
    | rank | thr | fpr | recall | precision |
    |---:|---:|---:|---:|---:|
    | 1 | 0.07 | 0.0096 | 1.0000 | 0.5575 |
    | 2 | 0.0733333 | 0.0092 | 1.0000 | 0.5673 |
    | 3 | 0.0766667 | 0.0081 | 1.0000 | 0.5988 |
  - time_eval (apply train threshold): PR-AUC=0.0158, ROC-AUC=0.4926, thr=0.07, FPR=0.0214, recall=0.0000
  - user_holdout (apply train threshold): PR-AUC=0.0145, ROC-AUC=0.4435, thr=0.07, FPR=0.0316, recall=0.0526
  - top_features:
    - device_7d__success_rate: 0.0184748
    - device_7d__failure_rate: 0.0181024
    - user_7d__attempt_cnt: 0.0180602
    - user_7d__failure_rate: 0.0173925
    - ip_24h__failure_rate: 0.0172511
    - user_7d__success_rate: 0.0167307
    - ip_7d__success_rate: 0.0165728
    - ip_7d__failure_rate: 0.016566
    - device_7d__attempt_cnt: 0.0157763
    - device_7d__success_cnt: 0.0156865

### label_the_chameleon
- **logreg**
  - train (threshold selection): PR-AUC=0.0390, thr=0.881367, FPR=0.0099, recall=0.0201
  - threshold candidates (train, FPR<=target):
    | rank | thr | fpr | recall | precision |
    |---:|---:|---:|---:|---:|
    | 1 | 0.881367 | 0.0099 | 0.0201 | 0.0366 |
    | 2 | 0.881769 | 0.0098 | 0.0201 | 0.0370 |
    | 3 | 0.882251 | 0.0098 | 0.0134 | 0.0250 |
  - time_eval (apply train threshold): PR-AUC=0.0323, ROC-AUC=0.5427, thr=0.881367, FPR=0.0243, recall=0.0000
  - user_holdout (apply train threshold): PR-AUC=0.0204, ROC-AUC=0.4575, thr=0.881367, FPR=0.0125, recall=0.0000
  - top_features:
    - ip_1h__lockout_cnt: -1.36938
    - ip_1h__lockout_rate: +0.909376
    - ip_24h__failure_cnt: -0.896826
    - ip_7d__lockout_cnt: +0.843047
    - ip_24h__failure_rate: +0.717964
    - ip_7d__success_cnt: -0.665183
    - ip_24h__success_rate: +0.622197
    - ip_7d__failure_rate: -0.595733
    - ip_1h__support_wait_seconds_sum: -0.566916
    - ip_24h__lockout_cnt: +0.509686
- **rf**
  - train (threshold selection): PR-AUC=0.9927, thr=0.0853276, FPR=0.0093, recall=0.9866
  - threshold candidates (train, FPR<=target):
    | rank | thr | fpr | recall | precision |
    |---:|---:|---:|---:|---:|
    | 1 | 0.0853276 | 0.0093 | 0.9866 | 0.6652 |
    | 2 | 0.0866667 | 0.0091 | 0.9866 | 0.6682 |
    | 3 | 0.09 | 0.0081 | 0.9866 | 0.6934 |
  - time_eval (apply train threshold): PR-AUC=0.0356, ROC-AUC=0.5969, thr=0.0853276, FPR=0.0330, recall=0.0323
  - user_holdout (apply train threshold): PR-AUC=0.0225, ROC-AUC=0.4804, thr=0.0853276, FPR=0.0381, recall=0.0000
  - top_features:
    - device_7d__success_rate: 0.0188884
    - user_7d__success_rate: 0.018603
    - ip_7d__attempt_cnt: 0.0179644
    - user_7d__failure_rate: 0.0177404
    - ip_7d__success_rate: 0.0175941
    - ip_7d__failure_rate: 0.017584
    - device_7d__failure_rate: 0.0173218
    - device_7d__challenge_rate: 0.0168501
    - user_7d__challenge_rate: 0.0167447
    - device_7d__attempt_cnt: 0.0164981

