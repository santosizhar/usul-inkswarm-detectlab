/* Inkswarm DetectLab — MVP Results Viewer (static) */
window.__RUN_DATA__ = {
  "schema_version": 1,
  "generated_at_utc": "2025-12-19T20:43:24Z",
  "runs": [
    {
      "schema_version": 1,
      "generated_at_utc": "2025-12-19T20:43:24.330263Z",
      "run_id": "RR_FAST_001_A",
      "timezone": "America/Argentina/Buenos_Aires",
      "signature": {
        "config_hash": "d86322c149e1bbf789e8b67583982ebae1ce20a335f91fde53c362ded81483f2",
        "github_sha": null,
        "seed": 1337,
        "schema_version": "v1"
      },
      "artifacts": {
        "baseline_report_md": "runs/RR_FAST_001_A/reports/baselines_login_attempt.md",
        "run_summary_md": "runs/RR_FAST_001_A/reports/summary.md"
      },
      "baselines": {
        "login_attempt": {
          "target_fpr": 0.01,
          "status": "ok",
          "labels": {
            "label_replicators": {
              "logreg": {
                "meta": {},
                "model_path": "RR_FAST_001_A/models/login_attempt/baselines/label_replicators__logreg.joblib",
                "status": "ok",
                "time_eval": {
                  "fpr": 0.047619047619047616,
                  "pr_auc": 0.058823529411764705,
                  "precision": 0.0,
                  "recall": 0.0,
                  "roc_auc": 0.23809523809523814,
                  "threshold_used": 0.9720541968413928
                },
                "top_features": [
                  {
                    "feature": "cross__checkout_attempt__ip_6h__success_rate",
                    "weight": 0.7090417065230928
                  },
                  {
                    "feature": "cross__checkout_attempt__user_6h__success_rate",
                    "weight": 0.7090417065230928
                  },
                  {
                    "feature": "cross__checkout_attempt__device_6h__success_rate",
                    "weight": 0.7090417065230928
                  },
                  {
                    "feature": "device_24h__success_rate",
                    "weight": -0.606209774368048
                  },
                  {
                    "feature": "user_24h__success_rate",
                    "weight": -0.606209774368048
                  },
                  {
                    "feature": "ip_24h__success_rate",
                    "weight": -0.606209774368048
                  },
                  {
                    "feature": "cross__checkout_attempt__device_6h__payment_value_sum",
                    "weight": -0.4701604501647082
                  },
                  {
                    "feature": "cross__checkout_attempt__user_6h__payment_value_sum",
                    "weight": -0.4701604501647082
                  },
                  {
                    "feature": "cross__checkout_attempt__ip_6h__payment_value_sum",
                    "weight": -0.4701604501647082
                  },
                  {
                    "feature": "ip_6h__failure_cnt",
                    "weight": 0.32345873782193246
                  },
                  {
                    "feature": "user_6h__failure_cnt",
                    "weight": 0.32345873782193246
                  },
                  {
                    "feature": "device_6h__failure_cnt",
                    "weight": 0.32345873782193246
                  },
                  {
                    "feature": "device_24h__failure_rate",
                    "weight": -0.2878968304637088
                  },
                  {
                    "feature": "user_24h__failure_rate",
                    "weight": -0.2878968304637088
                  },
                  {
                    "feature": "ip_24h__failure_rate",
                    "weight": -0.2878968304637088
                  },
                  {
                    "feature": "user_6h__success_rate",
                    "weight": -0.2718234233586376
                  },
                  {
                    "feature": "ip_6h__success_rate",
                    "weight": -0.2718234233586376
                  },
                  {
                    "feature": "device_6h__success_rate",
                    "weight": -0.2718234233586376
                  },
                  {
                    "feature": "device_6h__challenge_cnt",
                    "weight": 0.24998984674898803
                  },
                  {
                    "feature": "ip_6h__challenge_cnt",
                    "weight": 0.24998984674898803
                  }
                ],
                "train": {
                  "fpr": 0.006622516556291391,
                  "pr_auc": 0.7124999999999999,
                  "precision": 0.6666666666666666,
                  "recall": 0.4,
                  "threshold_for_fpr": 0.9720541968413928,
                  "threshold_table_top3": [
                    {
                      "fpr": 0.006622516556291391,
                      "precision": 0.75,
                      "recall": 0.6,
                      "threshold": 0.9297517034780215
                    },
                    {
                      "fpr": 0.006622516556291391,
                      "precision": 0.6666666666666666,
                      "recall": 0.4,
                      "threshold": 0.9720541968413928
                    },
                    {
                      "fpr": 0.0,
                      "precision": 1.0,
                      "recall": 0.4,
                      "threshold": 0.9873380878232644
                    }
                  ]
                },
                "user_holdout": {
                  "fpr": 0.043478260869565216,
                  "pr_auc": 0.125,
                  "precision": 0.0,
                  "recall": 0.0,
                  "roc_auc": 0.717391304347826,
                  "threshold_used": 0.9720541968413928
                }
              },
              "rf": {
                "meta": {},
                "model_path": "RR_FAST_001_A/models/login_attempt/baselines/label_replicators__rf.joblib",
                "status": "ok",
                "time_eval": {
                  "fpr": 0.047619047619047616,
                  "pr_auc": 0.045454545454545456,
                  "precision": 0.0,
                  "recall": 0.0,
                  "roc_auc": 0.16666666666666669,
                  "threshold_used": 0.2114155844155844
                },
                "top_features": [
                  {
                    "feature": "cross__checkout_attempt__ip_24h__payment_value_sum",
                    "importance": 0.02485290755723147
                  },
                  {
                    "feature": "cross__checkout_attempt__device_24h__payment_value_mean",
                    "importance": 0.022150058965387225
                  },
                  {
                    "feature": "device_24h__challenge_rate",
                    "importance": 0.022050170740732004
                  },
                  {
                    "feature": "cross__checkout_attempt__device_24h__payment_value_sum",
                    "importance": 0.021504706209512375
                  },
                  {
                    "feature": "user_1h__uniq_ip_hash_cnt",
                    "importance": 0.021234452022563553
                  },
                  {
                    "feature": "user_1h__uniq_device_fingerprint_hash_cnt",
                    "importance": 0.021221569444795255
                  },
                  {
                    "feature": "cross__checkout_attempt__ip_6h__payment_value_sum",
                    "importance": 0.02083747397277285
                  },
                  {
                    "feature": "ip_24h__challenge_rate",
                    "importance": 0.020822390075969262
                  },
                  {
                    "feature": "user_24h__challenge_rate",
                    "importance": 0.019867535594537977
                  },
                  {
                    "feature": "user_24h__success_rate",
                    "importance": 0.018058448556056907
                  },
                  {
                    "feature": "cross__checkout_attempt__ip_24h__payment_value_mean",
                    "importance": 0.017804806049476873
                  },
                  {
                    "feature": "cross__checkout_attempt__user_24h__payment_value_mean",
                    "importance": 0.017212282390685486
                  },
                  {
                    "feature": "ip_1h__uniq_user_id_cnt",
                    "importance": 0.01684633471118402
                  },
                  {
                    "feature": "device_24h__success_rate",
                    "importance": 0.01632502434202964
                  },
                  {
                    "feature": "cross__checkout_attempt__device_6h__payment_value_mean",
                    "importance": 0.016233560307375702
                  },
                  {
                    "feature": "cross__checkout_attempt__user_6h__payment_value_mean",
                    "importance": 0.016107871592794528
                  },
                  {
                    "feature": "cross__checkout_attempt__device_24h__event_cnt",
                    "importance": 0.01574677509917982
                  },
                  {
                    "feature": "device_1h__uniq_ip_hash_cnt",
                    "importance": 0.015098306196026975
                  },
                  {
                    "feature": "cross__checkout_attempt__device_24h__success_cnt",
                    "importance": 0.014801579126495835
                  },
                  {
                    "feature": "ip_24h__attempt_cnt",
                    "importance": 0.014622627576587452
                  }
                ],
                "train": {
                  "fpr": 0.006622516556291391,
                  "pr_auc": 0.8769230769230769,
                  "precision": 0.8,
                  "recall": 0.8,
                  "threshold_for_fpr": 0.2114155844155844,
                  "threshold_table_top3": [
                    {
                      "fpr": 0.006622516556291391,
                      "precision": 0.8,
                      "recall": 0.8,
                      "threshold": 0.2114155844155844
                    },
                    {
                      "fpr": 0.0,
                      "precision": 1.0,
                      "recall": 0.8,
                      "threshold": 0.6020502645502646
                    },
                    {
                      "fpr": 0.0,
                      "precision": 1.0,
                      "recall": 0.6,
                      "threshold": 0.6166666666666667
                    }
                  ]
                },
                "user_holdout": {
                  "fpr": 0.0,
                  "pr_auc": 0.08333333333333333,
                  "precision": 0.0,
                  "recall": 0.0,
                  "roc_auc": 0.5434782608695652,
                  "threshold_used": 0.2114155844155844
                }
              }
            },
            "label_the_chameleon": {
              "logreg": {
                "meta": {},
                "model_path": "RR_FAST_001_A/models/login_attempt/baselines/label_the_chameleon__logreg.joblib",
                "status": "ok",
                "time_eval": {
                  "fpr": 0.0,
                  "pr_auc": 0.05263157894736842,
                  "precision": 0.0,
                  "recall": 0.0,
                  "roc_auc": 0.16666666666666669,
                  "threshold_used": 0.17462959649666546
                },
                "top_features": [
                  {
                    "feature": "user_1h__success_rate",
                    "weight": 0.5385115382890399
                  },
                  {
                    "feature": "ip_1h__success_rate",
                    "weight": 0.5385115382890399
                  },
                  {
                    "feature": "device_1h__success_rate",
                    "weight": 0.5385115382890399
                  },
                  {
                    "feature": "cross__checkout_attempt__user_6h__event_cnt",
                    "weight": 0.3599269047379656
                  },
                  {
                    "feature": "cross__checkout_attempt__device_6h__event_cnt",
                    "weight": 0.3599269047379656
                  },
                  {
                    "feature": "cross__checkout_attempt__ip_6h__event_cnt",
                    "weight": 0.3599269047379656
                  },
                  {
                    "feature": "cross__checkout_attempt__user_6h__success_cnt",
                    "weight": 0.3599269047379656
                  },
                  {
                    "feature": "cross__checkout_attempt__ip_6h__success_cnt",
                    "weight": 0.3599269047379656
                  },
                  {
                    "feature": "cross__checkout_attempt__device_6h__success_cnt",
                    "weight": 0.3599269047379656
                  },
                  {
                    "feature": "ip_6h__failure_rate",
                    "weight": 0.2572505523636886
                  },
                  {
                    "feature": "user_6h__failure_rate",
                    "weight": 0.2572505523636886
                  },
                  {
                    "feature": "device_6h__failure_rate",
                    "weight": 0.2572505523636886
                  },
                  {
                    "feature": "device_1h__success_cnt",
                    "weight": 0.23502950293759053
                  },
                  {
                    "feature": "user_1h__success_cnt",
                    "weight": 0.23502950293759053
                  },
                  {
                    "feature": "ip_1h__success_cnt",
                    "weight": 0.23502950293759053
                  },
                  {
                    "feature": "user_6h__failure_cnt",
                    "weight": 0.1987266908999497
                  },
                  {
                    "feature": "ip_6h__failure_cnt",
                    "weight": 0.1987266908999497
                  },
                  {
                    "feature": "device_6h__failure_cnt",
                    "weight": 0.1987266908999497
                  },
                  {
                    "feature": "ip_1h__uniq_device_fingerprint_hash_cnt",
                    "weight": 0.16889865094454856
                  },
                  {
                    "feature": "ip_1h__uniq_user_id_cnt",
                    "weight": 0.16889865094454856
                  }
                ],
                "train": {
                  "fpr": 0.0064516129032258064,
                  "pr_auc": 1.0,
                  "precision": 0.5,
                  "recall": 1.0,
                  "threshold_for_fpr": 0.17462959649666546,
                  "threshold_table_top3": [
                    {
                      "fpr": 0.0064516129032258064,
                      "precision": 0.5,
                      "recall": 1.0,
                      "threshold": 0.17462959649666546
                    },
                    {
                      "fpr": 0.0,
                      "precision": 1.0,
                      "recall": 1.0,
                      "threshold": 0.9953460681766846
                    }
                  ]
                },
                "user_holdout": {
                  "fpr": 0.08333333333333333,
                  "pr_auc": 0.0,
                  "precision": 0.0,
                  "recall": 0.0,
                  "roc_auc": 0.0,
                  "threshold_used": 0.17462959649666546
                }
              },
              "rf": {
                "meta": {},
                "model_path": "RR_FAST_001_A/models/login_attempt/baselines/label_the_chameleon__rf.joblib",
                "status": "ok",
                "time_eval": {
                  "fpr": 0.09523809523809523,
                  "pr_auc": 0.045454545454545456,
                  "precision": 0.0,
                  "recall": 0.0,
                  "roc_auc": 0.35714285714285715,
                  "threshold_used": 0.08333333333333333
                },
                "top_features": [
                  {
                    "feature": "ip_1h__success_rate",
                    "importance": 0.03954122553592959
                  },
                  {
                    "feature": "device_1h__success_rate",
                    "importance": 0.03824769925612079
                  },
                  {
                    "feature": "user_1h__success_cnt",
                    "importance": 0.03202913951384755
                  },
                  {
                    "feature": "user_1h__success_rate",
                    "importance": 0.030907712296508627
                  },
                  {
                    "feature": "ip_24h__failure_rate",
                    "importance": 0.030382691594119465
                  },
                  {
                    "feature": "cross__checkout_attempt__user_6h__success_cnt",
                    "importance": 0.030242287395467908
                  },
                  {
                    "feature": "device_24h__success_cnt",
                    "importance": 0.029587146109985765
                  },
                  {
                    "feature": "cross__checkout_attempt__user_6h__payment_value_sum",
                    "importance": 0.02759409605138972
                  },
                  {
                    "feature": "device_24h__failure_rate",
                    "importance": 0.026598742693906757
                  },
                  {
                    "feature": "cross__checkout_attempt__device_6h__success_cnt",
                    "importance": 0.025807962021608417
                  },
                  {
                    "feature": "cross__checkout_attempt__user_24h__payment_value_sum",
                    "importance": 0.025397573503524246
                  },
                  {
                    "feature": "device_1h__attempt_cnt",
                    "importance": 0.025284378333211486
                  },
                  {
                    "feature": "cross__checkout_attempt__ip_24h__payment_value_mean",
                    "importance": 0.023213625343419322
                  },
                  {
                    "feature": "user_6h__failure_rate",
                    "importance": 0.023154773510134334
                  },
                  {
                    "feature": "ip_24h__success_rate",
                    "importance": 0.022226934669996014
                  },
                  {
                    "feature": "ip_1h__success_cnt",
                    "importance": 0.02208861336671457
                  },
                  {
                    "feature": "device_6h__failure_rate",
                    "importance": 0.02029918421422478
                  },
                  {
                    "feature": "user_1h__attempt_cnt",
                    "importance": 0.020212174224304318
                  },
                  {
                    "feature": "ip_6h__failure_rate",
                    "importance": 0.019800046435972735
                  },
                  {
                    "feature": "cross__checkout_attempt__user_24h__payment_value_mean",
                    "importance": 0.01813907018610145
                  }
                ],
                "train": {
                  "fpr": 0.0064516129032258064,
                  "pr_auc": 1.0,
                  "precision": 0.5,
                  "recall": 1.0,
                  "threshold_for_fpr": 0.08333333333333333,
                  "threshold_table_top3": [
                    {
                      "fpr": 0.0064516129032258064,
                      "precision": 0.5,
                      "recall": 1.0,
                      "threshold": 0.08333333333333333
                    },
                    {
                      "fpr": 0.0,
                      "precision": 1.0,
                      "recall": 1.0,
                      "threshold": 0.59
                    }
                  ]
                },
                "user_holdout": {
                  "fpr": 0.0,
                  "pr_auc": 0.0,
                  "precision": 0.0,
                  "recall": 0.0,
                  "roc_auc": 0.0,
                  "threshold_used": 0.08333333333333333
                }
              }
            },
            "label_the_mule": {
              "logreg": {
                "meta": {},
                "model_path": "RR_FAST_001_A/models/login_attempt/baselines/label_the_mule__logreg.joblib",
                "status": "ok",
                "time_eval": {
                  "fpr": 0.0,
                  "pr_auc": 0.0,
                  "precision": 0.0,
                  "recall": 0.0,
                  "roc_auc": 0.0,
                  "threshold_used": 0.9972894449481727
                },
                "top_features": [
                  {
                    "feature": "cross__checkout_attempt__ip_24h__success_rate",
                    "weight": 0.828067132458823
                  },
                  {
                    "feature": "cross__checkout_attempt__user_24h__success_rate",
                    "weight": 0.828067132458823
                  },
                  {
                    "feature": "cross__checkout_attempt__device_24h__success_rate",
                    "weight": 0.828067132458823
                  },
                  {
                    "feature": "device_6h__success_rate",
                    "weight": 0.5751464476884027
                  },
                  {
                    "feature": "user_6h__success_rate",
                    "weight": 0.5751464476884027
                  },
                  {
                    "feature": "ip_6h__success_rate",
                    "weight": 0.5751464476884027
                  },
                  {
                    "feature": "device_24h__failure_rate",
                    "weight": -0.47440413707068113
                  },
                  {
                    "feature": "ip_24h__failure_rate",
                    "weight": -0.47440413707068113
                  },
                  {
                    "feature": "user_24h__failure_rate",
                    "weight": -0.47440413707068113
                  },
                  {
                    "feature": "user_24h__uniq_device_fingerprint_hash_cnt",
                    "weight": -0.44606850005383336
                  },
                  {
                    "feature": "ip_24h__uniq_device_fingerprint_hash_cnt",
                    "weight": -0.44606850005383336
                  },
                  {
                    "feature": "user_24h__uniq_ip_hash_cnt",
                    "weight": -0.44606850005383336
                  },
                  {
                    "feature": "ip_24h__uniq_user_id_cnt",
                    "weight": -0.44606850005383336
                  },
                  {
                    "feature": "device_24h__uniq_ip_hash_cnt",
                    "weight": -0.44606850005383336
                  },
                  {
                    "feature": "device_24h__uniq_user_id_cnt",
                    "weight": -0.44606850005383336
                  },
                  {
                    "feature": "cross__checkout_attempt__user_24h__payment_value_sum",
                    "weight": -0.3972371372630186
                  },
                  {
                    "feature": "cross__checkout_attempt__device_24h__payment_value_sum",
                    "weight": -0.3972371372630186
                  },
                  {
                    "feature": "cross__checkout_attempt__ip_24h__payment_value_sum",
                    "weight": -0.3972371372630186
                  },
                  {
                    "feature": "cross__checkout_attempt__ip_6h__success_rate",
                    "weight": -0.34013531983954115
                  },
                  {
                    "feature": "cross__checkout_attempt__device_6h__success_rate",
                    "weight": -0.34013531983954115
                  }
                ],
                "train": {
                  "fpr": 0.006493506493506494,
                  "pr_auc": 0.26785714285714285,
                  "precision": 0.0,
                  "recall": 0.0,
                  "threshold_for_fpr": 0.9972894449481727,
                  "threshold_table_top3": [
                    {
                      "fpr": 0.006493506493506494,
                      "precision": 0.0,
                      "recall": 0.0,
                      "threshold": 0.9972894449481727
                    }
                  ]
                },
                "user_holdout": {
                  "fpr": 0.0,
                  "pr_auc": 0.0,
                  "precision": 0.0,
                  "recall": 0.0,
                  "roc_auc": 0.0,
                  "threshold_used": 0.9972894449481727
                }
              },
              "rf": {
                "meta": {},
                "model_path": "RR_FAST_001_A/models/login_attempt/baselines/label_the_mule__rf.joblib",
                "status": "ok",
                "time_eval": {
                  "fpr": 0.0,
                  "pr_auc": 0.0,
                  "precision": 0.0,
                  "recall": 0.0,
                  "roc_auc": 0.0,
                  "threshold_used": 0.6133333333333333
                },
                "top_features": [
                  {
                    "feature": "user_24h__attempt_cnt",
                    "importance": 0.06814592106278836
                  },
                  {
                    "feature": "device_24h__success_cnt",
                    "importance": 0.06717849439756216
                  },
                  {
                    "feature": "user_24h__success_cnt",
                    "importance": 0.06571516117248245
                  },
                  {
                    "feature": "device_24h__attempt_cnt",
                    "importance": 0.06229140976252313
                  },
                  {
                    "feature": "ip_24h__attempt_cnt",
                    "importance": 0.057971138407853
                  },
                  {
                    "feature": "ip_24h__success_cnt",
                    "importance": 0.038299485720766586
                  },
                  {
                    "feature": "cross__checkout_attempt__device_24h__payment_value_sum",
                    "importance": 0.023995440852859772
                  },
                  {
                    "feature": "device_1h__uniq_user_id_cnt",
                    "importance": 0.023403856983771655
                  },
                  {
                    "feature": "ip_1h__uniq_device_fingerprint_hash_cnt",
                    "importance": 0.018350624273130674
                  },
                  {
                    "feature": "cross__checkout_attempt__user_24h__payment_value_sum",
                    "importance": 0.01736379800765475
                  },
                  {
                    "feature": "cross__checkout_attempt__ip_24h__payment_value_mean",
                    "importance": 0.016645371486553602
                  },
                  {
                    "feature": "cross__checkout_attempt__user_24h__payment_value_mean",
                    "importance": 0.015861418075700538
                  },
                  {
                    "feature": "ip_24h__success_rate",
                    "importance": 0.015816074796195213
                  },
                  {
                    "feature": "user_1h__uniq_ip_hash_cnt",
                    "importance": 0.01524936060860668
                  },
                  {
                    "feature": "user_24h__success_rate",
                    "importance": 0.015236364612978157
                  },
                  {
                    "feature": "user_24h__uniq_ip_hash_cnt",
                    "importance": 0.014970233617030638
                  },
                  {
                    "feature": "device_24h__uniq_ip_hash_cnt",
                    "importance": 0.014793328836016527
                  },
                  {
                    "feature": "device_24h__uniq_user_id_cnt",
                    "importance": 0.014251682261790029
                  },
                  {
                    "feature": "device_6h__success_cnt",
                    "importance": 0.014070270992052525
                  },
                  {
                    "feature": "device_24h__success_rate",
                    "importance": 0.013414903639639129
                  }
                ],
                "train": {
                  "fpr": 0.0,
                  "pr_auc": 0.75,
                  "precision": 1.0,
                  "recall": 0.5,
                  "threshold_for_fpr": 0.6133333333333333,
                  "threshold_table_top3": [
                    {
                      "fpr": 0.0,
                      "precision": 1.0,
                      "recall": 0.5,
                      "threshold": 0.6133333333333333
                    }
                  ]
                },
                "user_holdout": {
                  "fpr": 0.0,
                  "pr_auc": 0.0,
                  "precision": 0.0,
                  "recall": 0.0,
                  "roc_auc": 0.0,
                  "threshold_used": 0.6133333333333333
                }
              }
            }
          },
          "meta": {
            "env": {
              "pandas": "2.2.3",
              "platform": "Linux-4.4.0-x86_64-with-glibc2.36",
              "pyarrow": "16.1.0",
              "python": "3.11.2 (main, Apr 28 2025, 14:11:48) [GCC 12.2.0]",
              "sklearn": "1.8.0",
              "threadpools": [
                {
                  "architecture": "SkylakeX",
                  "filepath": "/opt/pyvenv/lib/python3.11/site-packages/numpy.libs/libscipy_openblas64_-56d6093b.so",
                  "internal_api": "openblas",
                  "num_threads": 56,
                  "prefix": "libscipy_openblas",
                  "threading_layer": "pthreads",
                  "user_api": "blas",
                  "version": "0.3.29"
                },
                {
                  "architecture": "SkylakeX",
                  "filepath": "/opt/pyvenv/lib/python3.11/site-packages/scipy.libs/libscipy_openblas-c128ec02.so",
                  "internal_api": "openblas",
                  "num_threads": 56,
                  "prefix": "libscipy_openblas",
                  "threading_layer": "pthreads",
                  "user_api": "blas",
                  "version": "0.3.27.dev"
                },
                {
                  "filepath": "/opt/pyvenv/lib/python3.11/site-packages/scikit_learn.libs/libgomp-e985bcbb.so.1.0.0",
                  "internal_api": "openmp",
                  "num_threads": 56,
                  "prefix": "libgomp",
                  "user_api": "openmp",
                  "version": null
                }
              ]
            },
            "n_failed": 0,
            "n_ok": 6,
            "time_eval_rows": 22,
            "train_rows": 156,
            "user_holdout_rows": 24
          },
          "paths": {
            "metrics_json": "runs/RR_FAST_001_A/models/login_attempt/baselines/metrics.json",
            "report_md": "runs/RR_FAST_001_A/reports/baselines_login_attempt.md",
            "baselines_log": "runs/RR_FAST_001_A/logs/baselines.log"
          }
        }
      },
      "eval": {
        "login_attempt": {
          "slices_report": "runs/RR_FAST_001_A/reports/eval_slices_login_attempt.md",
          "stability_report": "runs/RR_FAST_001_A/reports/eval_stability_login_attempt.md",
          "stability_summary": {
            "primary_split": "user_holdout",
            "rows": [],
            "status": "partial"
          }
        }
      },
      "notes": []
    }
  ]
};
(function() {
  const $ = (id) => document.getElementById(id);
  const content = $("content");
  const metricSel = $("metric");
  const detailSel = $("detail");

  function fmt(x) {
    if (x === null || x === undefined) return "—";
    if (typeof x === "number") return x.toFixed(4);
    return String(x);
  }

  function pickCell(entry, metricKey, detail) {
    if (!entry || entry.status !== "ok") {
      const err = entry && entry.error ? entry.error : "missing";
      return `<span class="fail">failed</span><div class="small">${err}</div>`;
    }
    const split = entry[metricKey] || {};
    if (detail === "summary") {
      return `
        <div><span class="badge">PR-AUC</span> <b>${fmt(split.pr_auc)}</b></div>
        <div class="small">Recall @ train thr: <b>${fmt(split.recall)}</b> (FPR=${fmt(split.fpr)})</div>
      `;
    }
    return `
      <div><span class="badge">PR-AUC</span> <b>${fmt(split.pr_auc)}</b></div>
      <div class="small">Threshold used: <code>${fmt(split.threshold_used ?? entry.train?.threshold_for_fpr)}</code></div>
      <div class="small">Recall: <b>${fmt(split.recall)}</b> • Precision: <b>${fmt(split.precision)}</b> • FPR: <b>${fmt(split.fpr)}</b></div>
      <div class="small">ROC-AUC: <b>${fmt(split.roc_auc)}</b></div>
    `;
  }

  function render() {
    const metricKey = metricSel.value;
    const detail = detailSel.value;
    const runs = (window.__RUN_DATA__ && window.__RUN_DATA__.runs) || [];
    content.innerHTML = "";

    runs.forEach((r) => {
      const base = r.baselines && r.baselines.login_attempt;
      const labels = base && base.labels ? base.labels : {};
      const target = base && base.target_fpr;
      const env = base && base.meta && base.meta.env ? base.meta.env : null;
      const sig = r.signature || null;

      const noteBits = [];
      if (target !== null && target !== undefined) noteBits.push(`<span class="pill">Target FPR: <b>${fmt(target)}</b></span>`);
      if (env && env.python) noteBits.push(`<span class="pill">Python: <b>${env.python.split(" ")[0]}</b></span>`);
      if (env && env.platform) noteBits.push(`<span class="pill">Platform: <b>${env.platform}</b></span>`);
      if (sig && sig.config_hash) noteBits.push(`<span class="pill">Config: <b>${sig.config_hash.slice(0,8)}</b></span>`);
      if (sig && sig.github_sha) noteBits.push(`<span class="pill">Code: <b>${sig.github_sha.slice(0,8)}</b></span>`);

      const card = document.createElement("section");
      card.className = "card";
      card.innerHTML = `
        <h2>Run: <code>${r.run_id}</code></h2>
        <div class="small">Generated: ${r.generated_at_utc || "—"} • Timezone: ${r.timezone || "—"}</div>
        <div class="kv">${noteBits.join("")}</div>
      `;

      const tbl = document.createElement("table");
      const head = document.createElement("thead");
      head.innerHTML = `<tr><th>Label</th><th>logreg</th><th>rf</th></tr>`;
      tbl.appendChild(head);

      const body = document.createElement("tbody");
      const labelNames = Object.keys(labels).sort();
      if (labelNames.length === 0) {
        const tr = document.createElement("tr");
        tr.innerHTML = `<td colspan="3"><span class="fail">No baselines found</span><div class="small">Run may be pre-baselines or baselines failed.</div></td>`;
        body.appendChild(tr);
      } else {
        labelNames.forEach((lab) => {
          const byModel = labels[lab] || {};
          const tr = document.createElement("tr");
          tr.innerHTML = `
            <td><b>${lab}</b></td>
            <td>${pickCell(byModel.logreg, metricKey, detail)}</td>
            <td>${pickCell(byModel.rf, metricKey, detail)}</td>
          `;
          body.appendChild(tr);
        });
      }
      tbl.appendChild(body);
      card.appendChild(tbl);


      // Diagnostics (Slices + Stability)
      const ev = r.eval && r.eval.login_attempt ? r.eval.login_attempt : null;
      if (ev) {
        const diag = document.createElement("div");
        diag.className = "panel";
        let html = `<h3>Diagnostics</h3>`;
        if (ev.stability_summary && ev.stability_summary.rows && ev.stability_summary.rows.length) {
          const rows = ev.stability_summary.rows.slice(0);
          html += `<div class="small">Primary truth split: <b>${ev.stability_summary.primary_split || "user_holdout"}</b></div>`;
          html += `<table class="mini"><thead><tr><th>Label</th><th>Model</th><th>Holdout PR-AUC</th><th>Holdout Recall@thr</th><th>Time Recall@thr</th><th>ΔRecall (Hold-Time)</th></tr></thead><tbody>`;
          rows.forEach((rr) => {
            html += `<tr><td><code>${rr.label}</code></td><td><code>${rr.model}</code></td><td>${fmt(rr.holdout_pr_auc)}</td><td>${fmt(rr.holdout_recall)}</td><td>${fmt(rr.time_recall)}</td><td>${fmt(rr.delta_recall_hold_minus_time)}</td></tr>`;
          });
          html += `</tbody></table>`;
          html += `<div class="small">For deeper breakdowns, see the slice report: <code>${(ev.slices_report || "reports/eval_slices_login_attempt.md")}</code></div>`;
        } else {
          html += `<div class="small"><span class="warn">Diagnostics not found</span> — run may have skipped evaluation or artifacts are missing.</div>`;
        }
        if (ev.stability_report) {
          html += `<div class="small">Stability report path: <code>${ev.stability_report}</code></div>`;
        }
        diag.innerHTML = html;
        card.appendChild(diag);
      }

      // Notes
      if (r.notes && r.notes.length) {
        const n = document.createElement("div");
        n.className = "small";
        n.style.marginTop = "10px";
        n.innerHTML = `<b>Notes:</b><ul>${r.notes.map(x => `<li>${x}</li>`).join("")}</ul>`;
        card.appendChild(n);
      }

      content.appendChild(card);
    });
  }

  metricSel.addEventListener("change", render);
  detailSel.addEventListener("change", render);
  render();
})();
