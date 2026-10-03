import json
from pathlib import Path

### Grade v.0

ROOT = Path(__file__).resolve().parents[2]
GUIDELINES_PATH = ROOT / "data" / "guidelines.json"


# Dataset (flow, subflow) -> guidelines.json (flow, subflow). FAQ subflows are mapped by prefix below.
SUBFLOW_MAP = {
    ("account_access", "recover_password"): ("Account Access", "Recover Password"),
    ("account_access", "recover_username"): ("Account Access", "Recover Username"),
    ("account_access", "reset_2fa"): ("Account Access", "Reset Two-Factor Auth"),
    ("manage_account", "manage_change_address"): ("Manage Account", "Manage Change Address"),
    ("manage_account", "manage_change_name"): ("Manage Account", "Manage Change Name"),
    ("manage_account", "manage_change_phone"): ("Manage Account", "Manage Change Phone"),
    ("manage_account", "manage_payment_method"): ("Manage Account", "Manage Payment Method"),
    ("manage_account", "status_credit_missing"): ("Manage Account", "Status Credit Missing"),
    ("manage_account", "status_service_added"): ("Manage Account", "Status Service Added"),
    ("manage_account", "status_service_removed"): ("Manage Account", "Status Service Removed"),
    ("manage_account", "status_shipping_question"): ("Manage Account", "Status Shipping Question"),
    ("order_issue", "manage_cancel"): ("Order Issue", "Manage Cancel"),
    ("order_issue", "manage_create"): ("Order Issue", "Manage Create"),
    ("order_issue", "manage_downgrade"): ("Order Issue", "Manage Downgrade"),
    ("order_issue", "manage_upgrade"): ("Order Issue", "Manage Upgrade"),
    ("order_issue", "status_delivery_time"): ("Order Issue", "Status Delivery Time"),
    ("order_issue", "status_mystery_fee"): ("Order Issue", "Status Mystery Fee"),
    ("order_issue", "status_payment_method"): ("Order Issue", "Status Payment Method"),
    ("order_issue", "status_quantity"): ("Order Issue", "Status Quantity"),
    ("product_defect", "refund_initiate"): ("Product Defect", "Initiate Refund"),
    ("product_defect", "refund_status"): ("Product Defect", "Refund Status"),
    ("product_defect", "refund_update"): ("Product Defect", "Update Refund"),
    ("product_defect", "return_color"): ("Product Defect", "Return Due to Color"),
    ("product_defect", "return_size"): ("Product Defect", "Return Due to Size"),
    ("product_defect", "return_stain"): ("Product Defect", "Return Due to Stain"),
    ("purchase_dispute", "bad_price_competitor"): ("Purchase Dispute", "Bad Price Competitor"),
    ("purchase_dispute", "bad_price_yesterday"): ("Purchase Dispute", "Bad Price Yesterday"),
    ("purchase_dispute", "mistimed_billing_already_returned"): ("Purchase Dispute", "Mistimed Billing Already Returned"),
    ("purchase_dispute", "mistimed_billing_never_bought"): ("Purchase Dispute", "Mistimed Billing Never Bought"),
    ("purchase_dispute", "out_of_stock_general"): ("Purchase Dispute", "Out-of-Stock General"),
    ("purchase_dispute", "out_of_stock_one_item"): ("Purchase Dispute", "Out-of-Stock One Item"),
    ("purchase_dispute", "promo_code_invalid"): ("Purchase Dispute", "Promo Code Invalid"),
    ("purchase_dispute", "promo_code_out_of_date"): ("Purchase Dispute", "Promo Code Out of Date"),
    ("shipping_issue", "cost"): ("Shipping Issue", "Shipping Cost"),
    ("shipping_issue", "manage"): ("Shipping Issue", "Manage Shipping"),
    ("shipping_issue", "missing"): ("Shipping Issue", "Missing Item"),
    ("shipping_issue", "status"): ("Shipping Issue", "Shipping Status"),
    ("subscription_inquiry", "manage_dispute_bill"): ("Subscription Inquiry", "Manage Dispute Bill"),
    ("subscription_inquiry", "manage_extension"): ("Subscription Inquiry", "Manage Extension"),
    ("subscription_inquiry", "manage_pay_bill"): ("Subscription Inquiry", "Manage Pay Bill"),
    ("subscription_inquiry", "status_due_amount"): ("Subscription Inquiry", "Status Due Amount"),
    ("subscription_inquiry", "status_due_date"): ("Subscription Inquiry", "Status Due Date"),
    # Best match: the dataset has no "status_active" key, and this is the only unmapped subscription status.
    ("subscription_inquiry", "status_questions"): ("Subscription Inquiry", "Status Active"),
    ("troubleshoot_site", "credit_card"): ("Troubleshoot Site", "Invalid Credit Card"),
    ("troubleshoot_site", "search_results"): ("Troubleshoot Site", "Search Not Working"),
    ("troubleshoot_site", "shopping_cart"): ("Troubleshoot Site", "Cart Not Updating"),
    ("troubleshoot_site", "slow_speed"): ("Troubleshoot Site", "Website Too Slow"),
    # ("order_issue", "status_delivery_date") has no guideline passage (3 chats) and is excluded.
}

FAQ_PREFIXES = {
    "single_item_query": {"boots": "Boots FAQ", "shirt": "Shirt FAQ", "jeans": "Jeans FAQ", "jacket": "Jacket FAQ"},
    "storewide_query": {"pricing": "Pricing FAQ", "membership": "Membership FAQ",
                        "timing": "Timing FAQ", "policy": "Policy FAQ"},
}

FAQ_FLOWS = {"single_item_query": "Single-Item Query", "storewide_query": "Storewide Query"}


def guideline_key(flow: str, subflow: str) -> tuple[str, str] | None:
    """Map a dataset (flow, subflow) to its guidelines.json (flow, subflow), or None if it has no passage."""
    if flow in FAQ_PREFIXES:
        topic = subflow.split("_")[0]
        return (FAQ_FLOWS[flow], FAQ_PREFIXES[flow][topic]) if topic in FAQ_PREFIXES[flow] else None
    return SUBFLOW_MAP.get((flow, subflow))