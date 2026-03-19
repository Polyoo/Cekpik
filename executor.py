import logging
from config import *

logger = logging.getLogger(__name__)

def buy(token_id, amount, price, dry_run=True):
    if dry_run:
        shares = round(amount / price, 4)
        logger.info(f"[SIM] BUY {shares} @ {price}")
        return True, amount, shares

    try:
        from py_clob_client.client import ClobClient
        from py_clob_client.clob_types import MarketOrderArgs, ApiCreds

        creds = ApiCreds(
            api_key=API_KEY,
            api_secret=API_SECRET,
            api_passphrase=API_PASSPHRASE
        )

        client = ClobClient(
            CLOB_URL,
            key=PRIVATE_KEY,
            chain_id=137,
            creds=creds
        )

        order = MarketOrderArgs(token_id=token_id, amount=amount)
        resp = client.create_market_order(order)

        if resp and resp.get("status") == "matched":
            filled = float(resp.get("size_matched", amount/price))
            cost   = float(resp.get("cost", amount))
            return True, cost, filled

        logger.warning(f"Order not matched: {resp}")
        return False, 0, 0

    except Exception as e:
        logger.error(f"BUY ERROR: {e}")
        return False, 0, 0
