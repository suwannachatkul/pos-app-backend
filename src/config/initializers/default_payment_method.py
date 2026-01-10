"""Initial default payment methods data."""

# TODO: do seed script instead of initializer
# For now this is just for ease of running without extra commands
DEFAULT_PAYMENT_METHODS = [
    {"name": "CASH", "min_modifier": 0.9, "max_modifier": 1.0, "points_modifier": 0.05},
    {
        "name": "CASH_ON_DELIVERY",
        "min_modifier": 1.0,
        "max_modifier": 1.02,
        "points_modifier": 0.05,
        "additional_item_schema": {
            "type": "object",
            "properties": {
                "courier": {
                    "type": "string",
                    "enum": ["YAMATO", "SAGAWA"],
                    "description": "Courier service",
                }
            },
            "required": ["courier"],
        },
    },
    {
        "name": "VISA",
        "min_modifier": 0.95,
        "max_modifier": 1.0,
        "points_modifier": 0.03,
        "additional_item_schema": {
            "type": "object",
            "properties": {
                "last4": {
                    "type": "string",
                    "pattern": "^[0-9]{4}$",
                    "description": "Last 4 digits of card",
                }
            },
            "required": ["last4"],
        },
    },
    {
        "name": "MASTERCARD",
        "min_modifier": 0.95,
        "max_modifier": 1.0,
        "points_modifier": 0.03,
        "additional_item_schema": {
            "type": "object",
            "properties": {"last4": {"type": "string", "pattern": "^[0-9]{4}$"}},
            "required": ["last4"],
        },
    },
    {
        "name": "AMEX",
        "min_modifier": 0.98,
        "max_modifier": 1.01,
        "points_modifier": 0.02,
        "additional_item_schema": {
            "type": "object",
            "properties": {"last4": {"type": "string", "pattern": "^[0-9]{4}$"}},
            "required": ["last4"],
        },
    },
    {
        "name": "JCB",
        "min_modifier": 0.95,
        "max_modifier": 1.0,
        "points_modifier": 0.05,
        "additional_item_schema": {
            "type": "object",
            "properties": {"last4": {"type": "string", "pattern": "^[0-9]{4}$"}},
            "required": ["last4"],
        },
    },
    {
        "name": "LINE_PAY",
        "min_modifier": 1.0,
        "max_modifier": 1.0,
        "points_modifier": 0.01,
    },
    {
        "name": "PAYPAY",
        "min_modifier": 1.0,
        "max_modifier": 1.0,
        "points_modifier": 0.01,
    },
    {
        "name": "GRAB_PAY",
        "min_modifier": 1.0,
        "max_modifier": 1.0,
        "points_modifier": 0.01,
    },
    {
        "name": "BANK_TRANSFER",
        "min_modifier": 1.0,
        "max_modifier": 1.0,
        "points_modifier": 0.0,
        "additional_item_schema": {
            "type": "object",
            "properties": {
                "bank": {"type": "string"},
                "account_number": {"type": "string"},
            },
            "required": ["bank", "account_number"],
        },
    },
    {
        "name": "CHEQUE",
        "min_modifier": 0.9,
        "max_modifier": 1.0,
        "points_modifier": 0.0,
        "additional_item_schema": {
            "type": "object",
            "properties": {
                "bank": {"type": "string"},
                "cheque_number": {"type": "string"},
            },
            "required": ["bank", "cheque_number"],
        },
    },
    {
        "name": "POINTS",
        "min_modifier": 1.0,
        "max_modifier": 1.0,
        "points_modifier": 0.0,
    },
]
