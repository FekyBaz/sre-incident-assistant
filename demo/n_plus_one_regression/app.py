"""Intentionally regressed demo service.

The latest commit introduces an N+1 query pattern so the SRE assistant can
correlate a latency spike with a concrete code change.
"""

def get_orders_with_items(db, order_ids):
    orders = db.fetch_orders(order_ids)

    # Intentional regression: one database query per order.
    for order in orders:
        order["items"] = db.fetch_items(order["id"])

    return orders