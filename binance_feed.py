import time, threading, logging, requests
from collections import deque

logger = logging.getLogger(__name__)
BASE = "https://api.binance.com/api/v3"

class BinanceFeed:
    def __init__(self, symbols):
        self.symbols = symbols
        self._prices = {}
        self._history = {c: deque(maxlen=300) for c in symbols}
        self._lock = threading.Lock()
        self._running = False

    def start(self):
        self._running = True
        threading.Thread(target=self._loop, daemon=True).start()
        time.sleep(3)

    def stop(self):
        self._running = False

    def _loop(self):
        while self._running:
            try:
                syms = list(self.symbols.values())
                param = str(syms).replace("'", '"').replace(" ", "")
                r = requests.get(f"{BASE}/ticker/price",
                                 params={"symbols": param}, timeout=5)
                if r.ok:
                    now = time.time()
                    with self._lock:
                        for item in r.json():
                            for coin, sym in self.symbols.items():
                                if item["symbol"] == sym:
                                    p = float(item["price"])
                                    self._prices[coin] = p
                                    self._history[coin].append((now, p))
            except Exception as e:
                logger.debug(e)
            time.sleep(10)

    def all_prices(self):
        with self._lock:
            return dict(self._prices)

    def momentum(self, coin, minutes):
        with self._lock:
            hist = list(self._history.get(coin, []))

        if len(hist) < 3:
            return 0, "NEUTRAL"

        cutoff = time.time() - minutes * 60
        past = [(t, p) for t, p in hist if t >= cutoff]
        if not past:
            return 0, "NEUTRAL"

        p_then = past[0][1]
        p_now = hist[-1][1]
        pct = (p_now - p_then) / p_then * 100

        if abs(pct) < 0.04:
            return pct, "NEUTRAL"

        return pct, "UP" if pct > 0 else "DOWN"

    def momentum_multi(self, coin):
        m5, _ = self.momentum(coin, 5)
        m15, _ = self.momentum(coin, 15)

        score = (m5 * 0.6) + (m15 * 0.4)

        if score > 0.15:
            return score, "STRONG"
        elif score > 0.05:
            return score, "MODERATE"
        elif score < -0.15:
            return score, "STRONG_DOWN"
        elif score < -0.05:
            return score, "MODERATE_DOWN"
        return score, "NEUTRAL"
