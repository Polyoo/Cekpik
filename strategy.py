import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class Signal:
    entry_type: str
    direction: str
    token_id: str
    price: float
    shares: float
    cost: float
    reason: str

def is_trade_safe(market):
    if market.spread_yes > 0.04 or market.spread_no > 0.04:
        return False
    if market.ask_yes + market.ask_no > 1.05:
        return False
    if market.bid_yes == 0 or market.bid_no == 0:
        return False
    return True

def scale_shares(base, strength):
    if strength == "STRONG":
        return round(base * 1.5, 1)
    elif strength == "MODERATE":
        return base
    return round(base * 0.6, 1)

def get_signal(market, momentum_pct, momentum_dir, momentum_str):
    from config import CONVICTION_SHARES

    if not is_trade_safe(market):
        return None

    edge = 1 - (market.ask_yes + market.ask_no)
    if edge < -0.03:
        return None

    if momentum_dir not in ["UP", "DOWN"]:
        return None

    if momentum_dir == "UP":
        price = market.ask_yes
        token = market.token_yes
    else:
        price = market.ask_no
        token = market.token_no

    shares = scale_shares(CONVICTION_SHARES, momentum_str)
    cost = round(shares * price, 2)

    return Signal(
        entry_type="CONVICTION",
        direction=momentum_dir,
        token_id=token,
        price=price,
        shares=shares,
        cost=cost,
        reason=f"mom={momentum_pct:.2f} edge={edge:.3f}"
    )
