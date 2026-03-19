# ═══════════════════════════════════════════════════════════
#  MARKET SCANNER — Fetch hourly market orderbook
# ═══════════════════════════════════════════════════════════

import time, logging, requests, json
from dataclasses import dataclass
from typing import Optional

logger   = logging.getLogger(__name__)
GAMMA    = "https://gamma-api.polymarket.com"
CLOB     = "https://clob.polymarket.com"
NAMES    = {"btc":"Bitcoin","eth":"Ethereum","sol":"Solana","xrp":"XRP"}


@dataclass
class Market:
    coin:      str
    market_id: str
    question:  str
    token_yes: str    # UP token
    token_no:  str    # DOWN token
    window_ts: int
    closes_at: float
    ask_yes:   float
    bid_yes:   float
    ask_no:    float
    bid_no:    float
    open_price: float = 0.0   # Binance candle open

    @property
    def time_remaining(self) -> float:
        return max(0.0, self.closes_at - time.time())

    @property
    def time_elapsed(self) -> float:
        return max(0.0, time.time() - self.window_ts)

    @property
    def time_remaining_str(self) -> str:
        t = int(self.time_remaining)
        return f"{t//60}m{t%60:02d}s"

    @property
    def combined(self) -> float:
        return self.ask_yes + self.ask_no

    @property
    def spread_yes(self) -> float:
        return self.ask_yes - self.bid_yes

    @property
    def spread_no(self) -> float:
        return self.ask_no - self.bid_no


def fetch(coin: str, binance=None) -> Optional[Market]:
    name = NAMES.get(coin, coin.upper())
    now  = time.time()

    try:
        r = requests.get(f"{GAMMA}/events", params={
            "keyword": f"{name} Up or Down",
            "active":  "true",
            "closed":  "false",
            "limit":   15,
        }, timeout=8)
        if not r.ok:
            return None

        events = r.json() if isinstance(r.json(), list) else []
        best   = None
        best_t = float("inf")

        for ev in events:
            ttl  = str(ev.get("title", "")).lower()
            if "up or down" not in ttl: continue
            if name.lower() not in ttl and coin not in ttl: continue

            for m in ev.get("markets", []):
                end = m.get("endDate") or m.get("end_date_iso") or ""
                try:
                    from datetime import datetime
                    if "Z" in str(end) or "+" in str(end):
                        ts = datetime.fromisoformat(
                            str(end).replace("Z", "+00:00")
                        ).timestamp()
                    else:
                        v = float(end)
                        ts = v / 1000 if v > 1e10 else v
                except:
                    continue

                left = ts - now
                if left < 60 or left > 7500: continue
                if ts < best_t:
                    best_t = ts
                    best   = (m, ev, ts)

        if not best:
            return None

        m, ev, closes_at = best

        # Parse tokens
        raw = m.get("clobTokenIds") or m.get("clob_token_ids", "[]")
        if isinstance(raw, str):
            try: raw = json.loads(raw)
            except: raw = []
        if len(raw) < 2:
            return None

        token_yes = str(raw[0])
        token_no  = str(raw[1])
        window_ts = int(closes_at - 3600)

        # Fetch orderbook
        ay = by_ = an = bn = 0.0

        try:
            r2 = requests.get(f"{CLOB}/book",
                params={"token_id": token_yes}, timeout=5)
            if r2.ok:
                bk  = r2.json()
                asks = sorted(bk.get("asks",[]),
                              key=lambda x: float(x.get("price",1)))
                bids = sorted(bk.get("bids",[]),
                              key=lambda x: float(x.get("price",0)),
                              reverse=True)
                if asks: ay = float(asks[0]["price"])
                if bids: by_ = float(bids[0]["price"])
        except: pass

        try:
            r3 = requests.get(f"{CLOB}/book",
                params={"token_id": token_no}, timeout=5)
            if r3.ok:
                bk  = r3.json()
                asks = sorted(bk.get("asks",[]),
                              key=lambda x: float(x.get("price",1)))
                bids = sorted(bk.get("bids",[]),
                              key=lambda x: float(x.get("price",0)),
                              reverse=True)
                if asks: an = float(asks[0]["price"])
                if bids: bn = float(bids[0]["price"])
        except: pass

        if ay <= 0 or an <= 0:
            return None

        # Fetch candle open
        op = 0.0
        if binance:
            sym_map = {"btc":"BTCUSDT","eth":"ETHUSDT",
                       "sol":"SOLUSDT","xrp":"XRPUSDT"}
            op = binance.candle_open(sym_map.get(coin,"BTCUSDT"), window_ts)

        q = str(m.get("question") or ev.get("title",""))[:60]

        return Market(
            coin      = coin,
            market_id = str(m.get("id") or m.get("conditionId","")),
            question  = q,
            token_yes = token_yes,
            token_no  = token_no,
            window_ts = window_ts,
            closes_at = closes_at,
            ask_yes   = round(ay,  4),
            bid_yes   = round(by_, 4),
            ask_no    = round(an,  4),
            bid_no    = round(bn,  4),
            open_price = op,
        )

    except Exception as e:
        logger.debug(f"  scanner({coin}): {e}")
        return None
