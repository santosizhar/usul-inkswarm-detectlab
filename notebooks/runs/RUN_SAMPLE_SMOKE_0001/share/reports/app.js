/* Inkswarm DetectLab — MVP Results Viewer (static) */
window.__RUN_DATA__ = {
  "schema_version": 1,
  "generated_at_utc": "2025-12-23T03:57:24Z",
  "runs": [
    {
      "schema_version": 1,
      "generated_at_utc": "2025-12-23T03:57:24.404818Z",
      "run_id": "RUN_SAMPLE_SMOKE_0001",
      "timezone": "America/Argentina/Buenos_Aires",
      "signature": {
        "config_hash": "fbebdfff6f355c628b3adaf42bcd4903060534819fad58ff42902651aaa4fc58",
        "github_sha": null,
        "seed": 1337,
        "schema_version": "v1"
      },
      "artifacts": {
        "baseline_report_md": "runs\\RUN_SAMPLE_SMOKE_0001\\reports\\baselines_login_attempt.md",
        "run_summary_md": "runs\\RUN_SAMPLE_SMOKE_0001\\reports\\summary.md"
      },
      "baselines": {
        "login_attempt": {
          "target_fpr": 0.01,
          "status": "ok",
          "labels": {
            "label_replicators": {
              "logreg": {
                "meta": {},
                "model_path": "RUN_SAMPLE_SMOKE_0001\\models\\login_attempt\\baselines\\logreg\\label_replicators.joblib",
                "status": "ok",
                "time_eval": {
                  "fpr": 0.018134715025906734,
                  "pr_auc": 0.021371219342175923,
                  "precision": 0.0,
                  "recall": 0.0,
                  "roc_auc": 0.4503122093795669,
                  "threshold_used": 0.8570365303552929
                },
                "top_features": [
                  {
                    "feature": "ip_7d__challenge_cnt",
                    "weight": -0.7927460041818308
                  },
                  {
                    "feature": "ip_6h__support_contacted_cnt",
                    "weight": -0.7335528200174183
                  },
                  {
                    "feature": "cross__checkout_attempt__ip_6h__payment_value_mean",
                    "weight": 0.6816408447650187
                  },
                  {
                    "feature": "ip_7d__lockout_cnt",
                    "weight": 0.5978715544014908
                  },
                  {
                    "feature": "ip_7d__uniq_device_fingerprint_hash_cnt",
                    "weight": -0.5883201903961353
                  },
                  {
                    "feature": "ip_7d__uniq_user_id_cnt",
                    "weight": -0.5883201903961353
                  },
                  {
                    "feature": "ip_24h__failure_rate",
                    "weight": 0.5845330066873407
                  },
                  {
                    "feature": "ip_7d__failure_rate",
                    "weight": -0.5726220534361676
                  },
                  {
                    "feature": "ip_7d__success_rate",
                    "weight": -0.5703602602419808
                  },
                  {
                    "feature": "cross__checkout_attempt__ip_6h__payment_value_sum",
                    "weight": -0.5454314480866742
                  },
                  {
                    "feature": "ip_6h__support_handle_seconds_sum",
                    "weight": 0.54333170702529
                  },
                  {
                    "feature": "ip_24h__success_rate",
                    "weight": 0.5383274868009477
                  },
                  {
                    "feature": "ip_1h__uniq_device_fingerprint_hash_cnt",
                    "weight": -0.5094756400339974
                  },
                  {
                    "feature": "ip_1h__uniq_user_id_cnt",
                    "weight": -0.5094756400339974
                  },
                  {
                    "feature": "cross__checkout_attempt__ip_7d__success_rate",
                    "weight": -0.5051393257248512
                  },
                  {
                    "feature": "cross__checkout_attempt__user_1h__success_rate",
                    "weight": 0.5046715326818791
                  },
                  {
                    "feature": "cross__checkout_attempt__device_1h__success_rate",
                    "weight": 0.5046715326818791
                  },
                  {
                    "feature": "cross__checkout_attempt__ip_24h__event_cnt",
                    "weight": 0.4984964370211778
                  },
                  {
                    "feature": "cross__checkout_attempt__ip_24h__success_cnt",
                    "weight": 0.4939252299349941
                  },
                  {
                    "feature": "ip_24h__uniq_user_id_cnt",
                    "weight": 0.47997779525158746
                  }
                ],
                "train": {
                  "fpr": 0.009958401613513173,
                  "pr_auc": 0.05559491433489543,
                  "precision": 0.07058823529411765,
                  "recall": 0.028708133971291867,
                  "threshold_for_fpr": 0.8570365303552929,
                  "threshold_table_top3": [
                    {
                      "fpr": 0.009958401613513173,
                      "precision": 0.07058823529411765,
                      "recall": 0.028708133971291867,
                      "threshold": 0.8570365303552929
                    },
                    {
                      "fpr": 0.009832345896886424,
                      "precision": 0.07142857142857142,
                      "recall": 0.028708133971291867,
                      "threshold": 0.8589560924123216
                    },
                    {
                      "fpr": 0.009706290180259675,
                      "precision": 0.07228915662650602,
                      "recall": 0.028708133971291867,
                      "threshold": 0.8601852911361365
                    }
                  ]
                },
                "user_holdout": {
                  "fpr": 0.006939625260235947,
                  "pr_auc": 0.02556497290965295,
                  "precision": 0.0,
                  "recall": 0.0,
                  "roc_auc": 0.46400317240011896,
                  "threshold_used": 0.8570365303552929
                }
              },
              "rf": {
                "meta": {},
                "model_path": "RUN_SAMPLE_SMOKE_0001\\models\\login_attempt\\baselines\\rf\\label_replicators.joblib",
                "status": "ok",
                "time_eval": {
                  "fpr": 0.1001727115716753,
                  "pr_auc": 0.022381302697837335,
                  "precision": 0.008547008547008548,
                  "recall": 0.038461538461538464,
                  "roc_auc": 0.5021588946459412,
                  "threshold_used": 0.07666666666666666
                },
                "top_features": [
                  {
                    "feature": "ip_7d__success_rate",
                    "importance": 0.0127291667991757
                  },
                  {
                    "feature": "ip_7d__attempt_cnt",
                    "importance": 0.01264867545136647
                  },
                  {
                    "feature": "ip_7d__success_cnt",
                    "importance": 0.012431444969369456
                  },
                  {
                    "feature": "user_7d__challenge_rate",
                    "importance": 0.012305698436115677
                  },
                  {
                    "feature": "device_7d__attempt_cnt",
                    "importance": 0.011993900338142932
                  },
                  {
                    "feature": "user_7d__attempt_cnt",
                    "importance": 0.011956727292370352
                  },
                  {
                    "feature": "ip_7d__failure_rate",
                    "importance": 0.011500051408631235
                  },
                  {
                    "feature": "user_7d__success_rate",
                    "importance": 0.011478481205509254
                  },
                  {
                    "feature": "device_7d__failure_rate",
                    "importance": 0.01136707703403539
                  },
                  {
                    "feature": "user_7d__success_cnt",
                    "importance": 0.01134895036203883
                  },
                  {
                    "feature": "device_7d__success_cnt",
                    "importance": 0.011203416015537605
                  },
                  {
                    "feature": "cross__checkout_attempt__device_7d__payment_value_mean",
                    "importance": 0.011052819758138925
                  },
                  {
                    "feature": "ip_7d__challenge_rate",
                    "importance": 0.011009925313943862
                  },
                  {
                    "feature": "device_7d__success_rate",
                    "importance": 0.010928234678117045
                  },
                  {
                    "feature": "cross__checkout_attempt__ip_7d__payment_value_mean",
                    "importance": 0.010770902668732301
                  },
                  {
                    "feature": "user_7d__failure_rate",
                    "importance": 0.010756912427609568
                  },
                  {
                    "feature": "device_7d__challenge_rate",
                    "importance": 0.010752212452325155
                  },
                  {
                    "feature": "ip_24h__attempt_cnt",
                    "importance": 0.01074545886350281
                  },
                  {
                    "feature": "ip_24h__success_rate",
                    "importance": 0.01069554532493487
                  },
                  {
                    "feature": "cross__checkout_attempt__user_7d__payment_value_mean",
                    "importance": 0.010402591745062044
                  }
                ],
                "train": {
                  "fpr": 0.009706290180259675,
                  "pr_auc": 1.0,
                  "precision": 0.7307692307692307,
                  "recall": 1.0,
                  "threshold_for_fpr": 0.07666666666666666,
                  "threshold_table_top3": [
                    {
                      "fpr": 0.009706290180259675,
                      "precision": 0.7307692307692307,
                      "recall": 1.0,
                      "threshold": 0.07666666666666666
                    },
                    {
                      "fpr": 0.009328123030379427,
                      "precision": 0.7385159010600707,
                      "recall": 1.0,
                      "threshold": 0.08
                    },
                    {
                      "fpr": 0.008571788730618934,
                      "precision": 0.7545126353790613,
                      "recall": 1.0,
                      "threshold": 0.08333333333333333
                    }
                  ]
                },
                "user_holdout": {
                  "fpr": 0.07633587786259542,
                  "pr_auc": 0.025728507909317418,
                  "precision": 0.017857142857142856,
                  "recall": 0.05714285714285714,
                  "roc_auc": 0.5362446713591752,
                  "threshold_used": 0.07666666666666666
                }
              }
            },
            "label_the_chameleon": {
              "logreg": {
                "meta": {},
                "model_path": "RUN_SAMPLE_SMOKE_0001\\models\\login_attempt\\baselines\\logreg\\label_the_chameleon.joblib",
                "status": "ok",
                "time_eval": {
                  "fpr": 0.01647875108412836,
                  "pr_auc": 0.04567267993468884,
                  "precision": 0.05,
                  "recall": 0.03225806451612903,
                  "roc_auc": 0.5997258204403659,
                  "threshold_used": 0.9311527739724242
                },
                "top_features": [
                  {
                    "feature": "ip_1h__lockout_cnt",
                    "weight": -1.4401038674260491
                  },
                  {
                    "feature": "ip_1h__lockout_rate",
                    "weight": 1.0079897664593263
                  },
                  {
                    "feature": "ip_7d__lockout_cnt",
                    "weight": 0.9775717956123211
                  },
                  {
                    "feature": "cross__checkout_attempt__ip_24h__payment_value_sum",
                    "weight": 0.942997137225779
                  },
                  {
                    "feature": "ip_24h__failure_cnt",
                    "weight": -0.8839902212855959
                  },
                  {
                    "feature": "ip_7d__success_cnt",
                    "weight": -0.7830576969018169
                  },
                  {
                    "feature": "ip_24h__failure_rate",
                    "weight": 0.7806144666326625
                  },
                  {
                    "feature": "ip_24h__success_rate",
                    "weight": 0.73534228987692
                  },
                  {
                    "feature": "cross__checkout_attempt__ip_6h__event_cnt",
                    "weight": -0.7156637660126987
                  },
                  {
                    "feature": "cross__checkout_attempt__ip_6h__success_cnt",
                    "weight": -0.7150108641286478
                  },
                  {
                    "feature": "cross__checkout_attempt__ip_7d__payment_value_sum",
                    "weight": -0.7137709198107155
                  },
                  {
                    "feature": "ip_7d__failure_rate",
                    "weight": -0.638324639783012
                  },
                  {
                    "feature": "ip_1h__support_wait_seconds_sum",
                    "weight": -0.5916119052696893
                  },
                  {
                    "feature": "ip_7d__success_rate",
                    "weight": -0.5857800749943367
                  },
                  {
                    "feature": "ip_7d__attempt_cnt",
                    "weight": -0.5701128613451871
                  },
                  {
                    "feature": "ip_1h__failure_cnt",
                    "weight": -0.5178026213265605
                  },
                  {
                    "feature": "cross__checkout_attempt__device_7d__payment_value_sum",
                    "weight": -0.504880032281844
                  },
                  {
                    "feature": "cross__checkout_attempt__user_7d__payment_value_sum",
                    "weight": -0.504880032281844
                  },
                  {
                    "feature": "user_1h__support_contacted_cnt",
                    "weight": -0.4900377160316058
                  },
                  {
                    "feature": "device_1h__support_contacted_cnt",
                    "weight": -0.4900377160316058
                  }
                ],
                "train": {
                  "fpr": 0.009883648192168148,
                  "pr_auc": 0.04778208088817282,
                  "precision": 0.036585365853658534,
                  "recall": 0.020134228187919462,
                  "threshold_for_fpr": 0.9311527739724242,
                  "threshold_table_top3": [
                    {
                      "fpr": 0.009883648192168148,
                      "precision": 0.036585365853658534,
                      "recall": 0.020134228187919462,
                      "threshold": 0.9311527739724242
                    },
                    {
                      "fpr": 0.009758538721381209,
                      "precision": 0.037037037037037035,
                      "recall": 0.020134228187919462,
                      "threshold": 0.9311638318388763
                    },
                    {
                      "fpr": 0.00963342925059427,
                      "precision": 0.0375,
                      "recall": 0.020134228187919462,
                      "threshold": 0.9320815696063242
                    }
                  ]
                },
                "user_holdout": {
                  "fpr": 0.0048543689320388345,
                  "pr_auc": 0.01957231088727874,
                  "precision": 0.0,
                  "recall": 0.0,
                  "roc_auc": 0.4396059394631639,
                  "threshold_used": 0.9311527739724242
                }
              },
              "rf": {
                "meta": {},
                "model_path": "RUN_SAMPLE_SMOKE_0001\\models\\login_attempt\\baselines\\rf\\label_the_chameleon.joblib",
                "status": "ok",
                "time_eval": {
                  "fpr": 0.07545533391153512,
                  "pr_auc": 0.03149675993803962,
                  "precision": 0.03333333333333333,
                  "recall": 0.0967741935483871,
                  "roc_auc": 0.5494502420054276,
                  "threshold_used": 0.06333333333333334
                },
                "top_features": [
                  {
                    "feature": "device_7d__success_rate",
                    "importance": 0.013112175433339292
                  },
                  {
                    "feature": "user_7d__success_rate",
                    "importance": 0.012547848759987313
                  },
                  {
                    "feature": "device_7d__failure_rate",
                    "importance": 0.012459055869338867
                  },
                  {
                    "feature": "user_7d__failure_rate",
                    "importance": 0.012424651627929245
                  },
                  {
                    "feature": "ip_7d__failure_rate",
                    "importance": 0.012239944286072554
                  },
                  {
                    "feature": "device_7d__challenge_rate",
                    "importance": 0.011873840154276847
                  },
                  {
                    "feature": "ip_7d__attempt_cnt",
                    "importance": 0.011710087951239137
                  },
                  {
                    "feature": "user_24h__success_rate",
                    "importance": 0.011496197650470562
                  },
                  {
                    "feature": "user_7d__attempt_cnt",
                    "importance": 0.01148352098744727
                  },
                  {
                    "feature": "ip_7d__success_cnt",
                    "importance": 0.011436456759491592
                  },
                  {
                    "feature": "device_7d__attempt_cnt",
                    "importance": 0.011220640341270294
                  },
                  {
                    "feature": "ip_7d__challenge_rate",
                    "importance": 0.011137052086338877
                  },
                  {
                    "feature": "ip_7d__success_rate",
                    "importance": 0.011038831607055901
                  },
                  {
                    "feature": "user_7d__challenge_rate",
                    "importance": 0.010980064327111554
                  },
                  {
                    "feature": "ip_24h__success_rate",
                    "importance": 0.010945786462164892
                  },
                  {
                    "feature": "device_24h__success_rate",
                    "importance": 0.010675415559742512
                  },
                  {
                    "feature": "user_7d__success_cnt",
                    "importance": 0.010538440661667604
                  },
                  {
                    "feature": "cross__checkout_attempt__device_7d__payment_value_mean",
                    "importance": 0.010492400938319362
                  },
                  {
                    "feature": "device_7d__success_cnt",
                    "importance": 0.010441434247678658
                  },
                  {
                    "feature": "cross__checkout_attempt__ip_7d__payment_value_mean",
                    "importance": 0.010179582039178632
                  }
                ],
                "train": {
                  "fpr": 0.009258100838233455,
                  "pr_auc": 0.9998660641442378,
                  "precision": 0.6681614349775785,
                  "recall": 1.0,
                  "threshold_for_fpr": 0.06333333333333334,
                  "threshold_table_top3": [
                    {
                      "fpr": 0.009258100838233455,
                      "precision": 0.6681614349775785,
                      "recall": 1.0,
                      "threshold": 0.06333333333333334
                    },
                    {
                      "fpr": 0.008382334542724884,
                      "precision": 0.6898148148148148,
                      "recall": 1.0,
                      "threshold": 0.06666666666666667
                    },
                    {
                      "fpr": 0.00788189665957713,
                      "precision": 0.7028301886792453,
                      "recall": 1.0,
                      "threshold": 0.06727777777777778
                    }
                  ]
                },
                "user_holdout": {
                  "fpr": 0.05825242718446602,
                  "pr_auc": 0.02334788476687254,
                  "precision": 0.011764705882352941,
                  "recall": 0.029411764705882353,
                  "roc_auc": 0.4998572244431754,
                  "threshold_used": 0.06333333333333334
                }
              }
            },
            "label_the_mule": {
              "logreg": {
                "meta": {},
                "model_path": "RUN_SAMPLE_SMOKE_0001\\models\\login_attempt\\baselines\\logreg\\label_the_mule.joblib",
                "status": "ok",
                "time_eval": {
                  "fpr": 0.0137221269296741,
                  "pr_auc": 0.014611584934270495,
                  "precision": 0.0,
                  "recall": 0.0,
                  "roc_auc": 0.48308557270821423,
                  "threshold_used": 0.9428479800255278
                },
                "top_features": [
                  {
                    "feature": "ip_1h__support_handle_seconds_sum",
                    "weight": -2.1573497081179034
                  },
                  {
                    "feature": "ip_7d__support_wait_seconds_sum",
                    "weight": -1.9300459460696142
                  },
                  {
                    "feature": "cross__checkout_attempt__ip_24h__success_cnt",
                    "weight": -1.7306370030049985
                  },
                  {
                    "feature": "cross__checkout_attempt__ip_24h__event_cnt",
                    "weight": -1.7171918900232317
                  },
                  {
                    "feature": "ip_1h__support_cost_usd_sum",
                    "weight": -1.275011345259836
                  },
                  {
                    "feature": "ip_24h__failure_rate",
                    "weight": 1.2622865361425277
                  },
                  {
                    "feature": "user_7d__support_wait_seconds_sum",
                    "weight": 1.1920108805161116
                  },
                  {
                    "feature": "device_7d__support_wait_seconds_sum",
                    "weight": 1.1920108805161056
                  },
                  {
                    "feature": "cross__checkout_attempt__ip_24h__payment_value_mean",
                    "weight": 1.094948281586202
                  },
                  {
                    "feature": "ip_1h__support_contacted_cnt",
                    "weight": 1.0005094889750719
                  },
                  {
                    "feature": "ip_24h__success_cnt",
                    "weight": 0.9350502383909649
                  },
                  {
                    "feature": "ip_7d__failure_cnt",
                    "weight": -0.9097089794694048
                  },
                  {
                    "feature": "cross__checkout_attempt__user_24h__success_cnt",
                    "weight": 0.8150071360357922
                  },
                  {
                    "feature": "cross__checkout_attempt__device_24h__success_cnt",
                    "weight": 0.8150071360357922
                  },
                  {
                    "feature": "cross__checkout_attempt__device_24h__event_cnt",
                    "weight": 0.809487697781789
                  },
                  {
                    "feature": "cross__checkout_attempt__user_24h__event_cnt",
                    "weight": 0.809487697781789
                  },
                  {
                    "feature": "ip_7d__support_contacted_cnt",
                    "weight": 0.7656263147588773
                  },
                  {
                    "feature": "ip_24h__uniq_device_fingerprint_hash_cnt",
                    "weight": -0.759317951718358
                  },
                  {
                    "feature": "ip_24h__uniq_user_id_cnt",
                    "weight": -0.759317951718358
                  },
                  {
                    "feature": "device_7d__support_contacted_cnt",
                    "weight": -0.7318877319077856
                  }
                ],
                "train": {
                  "fpr": 0.009944064636420136,
                  "pr_auc": 0.044099677796570966,
                  "precision": 0.024390243902439025,
                  "recall": 0.020618556701030927,
                  "threshold_for_fpr": 0.9428479800255278,
                  "threshold_table_top3": [
                    {
                      "fpr": 0.009944064636420136,
                      "precision": 0.024390243902439025,
                      "recall": 0.020618556701030927,
                      "threshold": 0.9428479800255278
                    },
                    {
                      "fpr": 0.009819763828464886,
                      "precision": 0.024691358024691357,
                      "recall": 0.020618556701030927,
                      "threshold": 0.9431865880169443
                    },
                    {
                      "fpr": 0.009695463020509634,
                      "precision": 0.025,
                      "recall": 0.020618556701030927,
                      "threshold": 0.9436496511369893
                    }
                  ]
                },
                "user_holdout": {
                  "fpr": 0.013040494166094716,
                  "pr_auc": 0.01478313996927536,
                  "precision": 0.0,
                  "recall": 0.0,
                  "roc_auc": 0.5433298414189213,
                  "threshold_used": 0.9428479800255278
                }
              },
              "rf": {
                "meta": {},
                "model_path": "RUN_SAMPLE_SMOKE_0001\\models\\login_attempt\\baselines\\rf\\label_the_mule.joblib",
                "status": "ok",
                "time_eval": {
                  "fpr": 0.08833619210977701,
                  "pr_auc": 0.019535177664933737,
                  "precision": 0.009615384615384616,
                  "recall": 0.05555555555555555,
                  "roc_auc": 0.46040594625500286,
                  "threshold_used": 0.05333333333333334
                },
                "top_features": [
                  {
                    "feature": "user_7d__attempt_cnt",
                    "importance": 0.012993075370278846
                  },
                  {
                    "feature": "device_7d__attempt_cnt",
                    "importance": 0.012000406809012498
                  },
                  {
                    "feature": "ip_7d__failure_rate",
                    "importance": 0.011611814228989215
                  },
                  {
                    "feature": "ip_24h__failure_rate",
                    "importance": 0.01144001596503634
                  },
                  {
                    "feature": "ip_7d__success_cnt",
                    "importance": 0.011421332237797933
                  },
                  {
                    "feature": "ip_7d__success_rate",
                    "importance": 0.011361723782134563
                  },
                  {
                    "feature": "device_7d__success_rate",
                    "importance": 0.011019105012847691
                  },
                  {
                    "feature": "user_7d__challenge_rate",
                    "importance": 0.011017680923401411
                  },
                  {
                    "feature": "ip_7d__attempt_cnt",
                    "importance": 0.010878670553680459
                  },
                  {
                    "feature": "device_7d__failure_rate",
                    "importance": 0.01076392682509099
                  },
                  {
                    "feature": "ip_24h__attempt_cnt",
                    "importance": 0.01065312101225301
                  },
                  {
                    "feature": "ip_24h__success_rate",
                    "importance": 0.010564609676942354
                  },
                  {
                    "feature": "user_24h__failure_rate",
                    "importance": 0.010533331717227465
                  },
                  {
                    "feature": "user_7d__success_rate",
                    "importance": 0.010514097884481348
                  },
                  {
                    "feature": "user_7d__failure_rate",
                    "importance": 0.010413039853819205
                  },
                  {
                    "feature": "cross__checkout_attempt__ip_7d__payment_value_mean",
                    "importance": 0.010407169636522303
                  },
                  {
                    "feature": "user_7d__success_cnt",
                    "importance": 0.010338794940051042
                  },
                  {
                    "feature": "device_7d__success_cnt",
                    "importance": 0.010108577783310166
                  },
                  {
                    "feature": "cross__checkout_attempt__user_7d__payment_value_mean",
                    "importance": 0.010037766307394788
                  },
                  {
                    "feature": "device_7d__challenge_rate",
                    "importance": 0.00975606361091057
                  }
                ],
                "train": {
                  "fpr": 0.008949658172778123,
                  "pr_auc": 1.0,
                  "precision": 0.5739644970414202,
                  "recall": 1.0,
                  "threshold_for_fpr": 0.05333333333333334,
                  "threshold_table_top3": [
                    {
                      "fpr": 0.008949658172778123,
                      "precision": 0.5739644970414202,
                      "recall": 1.0,
                      "threshold": 0.05333333333333334
                    },
                    {
                      "fpr": 0.007209446861404599,
                      "precision": 0.6258064516129033,
                      "recall": 1.0,
                      "threshold": 0.056666666666666664
                    },
                    {
                      "fpr": 0.006463642013673089,
                      "precision": 0.6510067114093959,
                      "recall": 1.0,
                      "threshold": 0.06
                    }
                  ]
                },
                "user_holdout": {
                  "fpr": 0.04461221688400824,
                  "pr_auc": 0.01640062592863293,
                  "precision": 0.029850746268656716,
                  "recall": 0.10526315789473684,
                  "roc_auc": 0.48164938771086946,
                  "threshold_used": 0.05333333333333334
                }
              }
            }
          },
          "meta": {
            "env": {
              "pandas": "2.3.3",
              "platform": "Windows-10-10.0.19045-SP0",
              "pyarrow": "22.0.0",
              "python": "3.14.0 (tags/v3.14.0:ebf955d, Oct  7 2025, 10:15:03) [MSC v.1944 64 bit (AMD64)]",
              "sklearn": "1.8.0",
              "threadpools": [
                {
                  "architecture": "Haswell",
                  "filepath": "C:\\Users\\Mart\u00edn\\AppData\\Local\\Programs\\Python\\Python314\\Lib\\site-packages\\numpy.libs\\libscipy_openblas64_-9e3e5a4229c1ca39f10dc82bba9e2b2b.dll",
                  "internal_api": "openblas",
                  "num_threads": 8,
                  "prefix": "libscipy_openblas",
                  "threading_layer": "pthreads",
                  "user_api": "blas",
                  "version": "0.3.30"
                },
                {
                  "filepath": "C:\\Users\\Mart\u00edn\\AppData\\Local\\Programs\\Python\\Python314\\Lib\\site-packages\\sklearn\\.libs\\vcomp140.dll",
                  "internal_api": "openmp",
                  "num_threads": 8,
                  "prefix": "vcomp",
                  "user_api": "openmp",
                  "version": null
                },
                {
                  "architecture": "Haswell",
                  "filepath": "C:\\Users\\Mart\u00edn\\AppData\\Local\\Programs\\Python\\Python314\\Lib\\site-packages\\scipy.libs\\libscipy_openblas-48c358d105077551cc9cc3ba79387ed5.dll",
                  "internal_api": "openblas",
                  "num_threads": 8,
                  "prefix": "libscipy_openblas",
                  "threading_layer": "pthreads",
                  "user_api": "blas",
                  "version": "0.3.29.dev"
                }
              ]
            },
            "n_failed": 0,
            "n_ok": 6,
            "time_eval_rows": 1184,
            "train_rows": 8142,
            "user_holdout_rows": 1476
          },
          "paths": {
            "metrics_json": "runs\\RUN_SAMPLE_SMOKE_0001\\models\\login_attempt\\baselines\\metrics.json",
            "report_md": "runs\\RUN_SAMPLE_SMOKE_0001\\reports\\baselines_login_attempt.md",
            "baselines_log": "runs\\RUN_SAMPLE_SMOKE_0001\\logs\\baselines.log"
          }
        }
      },
      "eval": {
        "login_attempt": {
          "slices_report": "runs\\RUN_SAMPLE_SMOKE_0001\\reports\\eval_slices_login_attempt.md",
          "stability_report": "runs\\RUN_SAMPLE_SMOKE_0001\\reports\\eval_stability_login_attempt.md",
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
  const gotoSel = $("goto");

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
if (gotoSel && !gotoSel.dataset.ready) {
  const esc = (s) => String(s)
    .replace(/&/g, "&amp;")
    .replace(/"/g, "&quot;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
  const opts = ['<option value="" selected>Select a run…</option>']
    .concat(runs.map((r) => {
      const v = r.run_id || "";
      const safe = esc(v);
      return `<option value="${safe}">${safe}</option>`;
    }));
  gotoSel.innerHTML = opts.join("");
  gotoSel.addEventListener("change", () => {
    const v = gotoSel.value;
    if (!v) return;
    const a = encodeURIComponent(v);
    const el = document.getElementById(`run-${a}`);
    if (el) el.scrollIntoView({behavior: "smooth", block: "start"});
  });
  gotoSel.dataset.ready = "1";
}

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
      if (env && env.platform) noteBits.push(`<span class="pill">Platform: <b>${env.platform}</b></span>`);if (sig && sig.config_hash) {
  noteBits.push(`<span class="pill" title="${sig.config_hash}">Config: <b>${sig.config_hash.slice(0,8)}</b></span>`);
} else {
  noteBits.push(`<span class="pill missing">Config: <b>—</b></span>`);
}
if (sig && sig.github_sha) {
  noteBits.push(`<span class="pill" title="${sig.github_sha}">Code: <b>${sig.github_sha.slice(0,8)}</b></span>`);
} else {
  noteBits.push(`<span class="pill missing">Code: <b>(no git)</b></span>`);
}

      const card = document.createElement("section");
      card.className = "card";
      card.innerHTML = `
        <h2 id="run-${encodeURIComponent(r.run_id || '')}">Run: <code>${r.run_id}</code></h2>
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
