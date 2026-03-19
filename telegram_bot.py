# ═══════════════════════════════════════════════════════════
#  TELEGRAM NOTIFICATIONS
# ═══════════════════════════════════════════════════════════

import logging, requests
logger = logging.getLogger(__name__)


def _send(msg: str):
    try:
        from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
        if not TELEGRAM_BOT_TOKEN: return
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            json={"chat_id": TELEGRAM_CHAT_ID, "text": msg,
                  "parse_mode": "HTML"},
            timeout=8
        )
    except Exception as e:
        logger.debug(f"TG: {e}")


def started(balance, dry_run):
    mode = "🔵 SIM" if dry_run else "🔴 LIVE"
    _send(f"🚀 <b>Leader Bot Started</b> {mode}\n"
          f"Balance: <b>${balance:.2f}</b>\n"
          f"Strategy: blue-walnut (conviction + insurance)\n"
          f"Markets: Hourly BTC/ETH/SOL/XRP")


def trade(coin, sig, balance, dry_run):
    icons = {"CONVICTION":"🎯","INSURANCE":"🛡️","LATE":"🔒"}
    icon  = icons.get(sig.entry_type, "⚡")
    mode  = "[SIM] " if dry_run else ""
    _send(f"{icon} <b>{mode}[{coin.upper()}] {sig.entry_type}</b>\n"
          f"Side: {sig.direction} @ ${sig.price:.3f}\n"
          f"Shares: {sig.shares} | Cost: ${sig.cost:.2f}\n"
          f"{sig.reason}\n"
          f"Bal: ${balance:.2f}")


def win(coin, direction, entry_type, pnl, balance, dry_run):
    mode = "[SIM] " if dry_run else ""
    _send(f"✅ <b>{mode}WIN [{coin.upper()}]</b>\n"
          f"{direction} [{entry_type}] +${pnl:.4f}\n"
          f"Bal: ${balance:.2f}")


def loss(coin, direction, entry_type, pnl, balance, dry_run):
    mode = "[SIM] " if dry_run else ""
    _send(f"❌ <b>{mode}LOSS [{coin.upper()}]</b>\n"
          f"{direction} [{entry_type}] ${pnl:.4f}\n"
          f"Bal: ${balance:.2f}")


def hourly(stats, balance, start, dry_run):
    mode = "[SIM] " if dry_run else ""
    net  = balance - start
    by   = stats.get("by_type", {})
    lines = ""
    for t, d in by.items():
        wr = d["w"]/d["n"]*100 if d["n"] else 0
        lines += f"\n  {t}: {d['n']}T {wr:.0f}% ${d['pnl']:+.2f}"
    _send(f"📊 <b>{mode}Hourly</b>\n"
          f"Bal: ${balance:.2f} (Net: ${net:+.2f})\n"
          f"Trades: {stats['closed']} W:{stats['wins']} "
          f"L:{stats['losses']} WR:{stats['win_rate']*100:.0f}%\n"
          f"PnL: ${stats['total_pnl']:+.4f}{lines}")


def stopped(stats, start, balance, dry_run):
    mode = "[SIM] " if dry_run else ""
    net  = balance - start
    _send(f"🛑 <b>{mode}Bot Stopped</b>\n"
          f"${start:.2f} → ${balance:.2f} (Net: ${net:+.2f})\n"
          f"Trades: {stats['closed']} WR:{stats['win_rate']*100:.0f}%\n"
          f"PnL: ${stats['total_pnl']:+.4f}")
