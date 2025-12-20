from __future__ import annotations
from .base import ColumnSpec, EventSchema

SCHEMA = EventSchema(
    name="checkout_attempt",
    version="1",
    description="SPACING GUILD planned target event. Defined early for stability.",
    columns=[
            ColumnSpec(name='run_id', dtype='string', required=True, enum=None, description='Run identifier (locked).'),
            ColumnSpec(name='event_id', dtype='string', required=True, enum=None, description='Unique event id within run.'),
            ColumnSpec(name='event_ts', dtype='timestamp_tz', required=True, enum=None, description='Timezone-aware timestamp in America/Argentina/Buenos_Aires.'),
            ColumnSpec(name='user_id', dtype='string', required=True, enum=None, description='Primary entity id (locked).'),
            ColumnSpec(name='session_id', dtype='string', required=False, enum=None, description='Session identifier (nullable).'),
            ColumnSpec(name='ip_hash', dtype='string', required=False, enum=None, description='Hashed IP / pseudo-identifier.'),
            ColumnSpec(name='device_fingerprint_hash', dtype='string', required=False, enum=None, description='Hashed device fingerprint / pseudo-identifier.'),
            ColumnSpec(name='country', dtype='string', required=False, enum=None, description='Country code/name (nullable).'),
            ColumnSpec(name='is_fraud', dtype='bool', required=False, enum=None, description='High-level fraud label (nullable in raw events).'),
            ColumnSpec(name='metadata_json', dtype='string', required=False, enum=None, description='Flexible JSON payload (allowed early; endgame derives wide tables).'),
            ColumnSpec(name='payment_value', dtype='float64', required=True, enum=None, description='Checkout payment value.'),
            ColumnSpec(name='basket_size', dtype='int64', required=True, enum=None, description='Number of items in basket.'),
            ColumnSpec(name='is_first_time_user', dtype='bool', required=True, enum=None, description='Whether this user is first-time.'),
            ColumnSpec(name='is_premium_user', dtype='bool', required=True, enum=None, description='Whether this user is premium.'),
            ColumnSpec(name='credit_card_hash', dtype='string', required=False, enum=None, description='Synthetic credit-card token/hash.'),
            ColumnSpec(name='checkout_result', dtype='string', required=True, enum=['success', 'failure', 'review'], description='Outcome of checkout attempt.'),
            ColumnSpec(name='decline_reason', dtype='string', required=False, enum=['insufficient_funds', 'suspected_fraud', 'network_error', 'other'], description='Reason for decline/failure.'),
    ],
)
