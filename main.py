# A dip buyer for the cbBTC minute bars: it buys when the close has fallen well under the day's own
# recent high and sells into the first bounce, holding through the noise in between.
import os, sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "vendor"))
import makefun_bars

SYMBOL = "CBBTC"
REF_BARS = 60
DIP_BPS = 250
TAKE_BPS = 120
STOP_BPS = 50
MAX_HOLD = 720
SIZE_BPS = 10000
CAP_BPS = 100
MIN_NOTIONAL = 1_000_000

hold = 0
closes = []


def on_batch(state, batch):
    global hold, closes
    if state.warming_up:
        return []
    close = state.close(SYMBOL)
    if close is None:
        return []
    closes.append(close)
    if len(closes) > REF_BARS:
        closes = closes[-REF_BARS:]
    held = state.positions.get(SYMBOL)
    if held is None:
        if len(closes) < REF_BARS:
            return []
        ref = max(closes)
        if close <= ref * (10000 - DIP_BPS) // 10000:
            spend = min(state.cash * SIZE_BPS // 10000, state.weight_room(SYMBOL))
            if spend >= MIN_NOTIONAL:
                hold = 0
                return [{"side": "buy", "symbol": SYMBOL, "notional_quote_units": spend,
                          "max_slippage_bps": CAP_BPS}]
        return []
    hold += 1
    gain_bps = (state.value(SYMBOL, held.qty) - held.cost) * 10000 // held.cost if held.cost else 0
    if gain_bps >= TAKE_BPS or gain_bps <= -STOP_BPS or hold >= MAX_HOLD:
        return [{"side": "sell", "symbol": SYMBOL, "qty": held.qty, "max_slippage_bps": CAP_BPS}]
    return []


if __name__ == "__main__":
    makefun_bars.run(on_batch)
