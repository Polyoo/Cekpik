import time, logging
from config import *
from binance_feed import BinanceFeed
from scanner import fetch
from strategy import get_signal
from executor import buy

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Bot:

    def __init__(self):
        self.balance = BANKROLL
        self.binance = BinanceFeed(ASSETS)

    def run(self):
        logger.info("🚀 BOT STARTED (LIVE)" if not DRY_RUN else "🚀 BOT STARTED (SIM)")
        self.binance.start()

        while True:
            prices = self.binance.all_prices()

            for coin in ASSETS:
                try:
                    mkt = fetch(coin, self.binance)
                    if not mkt:
                        continue

                    mom_pct, mom_str = self.binance.momentum_multi(coin)

                    if "DOWN" in mom_str:
                        mom_dir = "DOWN"
                    elif "STRONG" in mom_str or "MODERATE" in mom_str:
                        mom_dir = "UP"
                    else:
                        mom_dir = "NEUTRAL"

                    sig = get_signal(mkt, mom_pct, mom_dir, mom_str)

                    if not sig:
                        continue

                    current_price = (
                        mkt.ask_yes if sig.direction == "YES"
                        else mkt.ask_no
                    )

                    if abs(current_price - sig.price) > 0.02:
                        logger.info(f"[{coin}] Skip price moved")
                        continue

                    if sig.cost > self.balance:
                        logger.warning("Insufficient balance")
                        continue

                    ok, spent, shares = buy(
                        sig.token_id, sig.cost, sig.price, DRY_RUN
                    )

                    if ok:
                        self.balance -= spent
                        logger.info(
                            f"TRADE {coin.upper()} {sig.direction} "
                            f"${spent:.2f} | Bal=${self.balance:.2f}"
                        )

                except Exception as e:
                    logger.error(f"{coin} error: {e}")

            time.sleep(SCAN_INTERVAL)

if __name__ == "__main__":
    Bot().run()
