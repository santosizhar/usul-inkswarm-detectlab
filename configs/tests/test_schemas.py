from inkswarm_detectlab.schemas import get_schema

def test_login_schema_required_columns():
    s = get_schema("login_attempt")
    required = set(s.required_columns())
    for col in ["run_id","event_id","event_ts","user_id","login_result","username_present","mfa_used",
                "support_contacted","support_channel","support_responder_type","support_resolution"]:
        assert col in required

def test_checkout_schema_required_columns():
    s = get_schema("checkout_attempt")
    required = set(s.required_columns())
    for col in ["run_id","event_id","event_ts","user_id","payment_value","basket_size","is_first_time_user","is_premium_user","checkout_result"]:
        assert col in required
