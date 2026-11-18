import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "vendor"))
import makefun_bars  # noqa: E402

# risk: one open position, no leverage, hard stop, forced fallback entry
SYMBOL = "CBBTC"
LOOKBACK_BARS = 120
DIP_BPS = 250
TAKE_BPS = 150
STOP_BPS = 60
MAX_HOLD_BARS = 1440
# fallback: one trade is always taken by bar FALLBACK_BAR
FALLBACK_BAR = 360
CAP_BPS = 100
MIN_NOTIONAL = 1000000


class Strategy:
    def __init__(self):
        self.closes = []
        self.bars_seen = 0
        self.bars_held = 0

    def on_batch(self, state, batch):
        close = state.close(SYMBOL)
        if close is not None:
            self.closes.append(close)
            if len(self.closes) > LOOKBACK_BARS:
                del self.closes[0]
        self.bars_seen += 1

        if state.warming_up:
            return []

        held = state.positions.get(SYMBOL)

        if held is None:
            self.bars_held = 0
            if close is None or not self.closes:
                return []
            dip_level = max(self.closes) * (10000 - DIP_BPS) // 10000
            if close > dip_level and self.bars_seen < FALLBACK_BAR:
                return []
            notional = min(state.cash, state.weight_room(SYMBOL))
            if notional < MIN_NOTIONAL:
                return []
            return [{
                "side": "buy",
                "symbol": SYMBOL,
                "notional_quote_units": notional,
                "max_slippage_bps": CAP_BPS,
            }]

        self.bars_held += 1
        value = state.value(SYMBOL, held.qty)
        gain_bps = (value - held.cost) * 10000 // held.cost if held.cost else 0
        if (
            gain_bps >= TAKE_BPS
            or gain_bps <= -STOP_BPS
            or self.bars_held >= MAX_HOLD_BARS
        ):
            return [{
                "side": "sell",
                "symbol": SYMBOL,
                "qty": held.qty,
                "max_slippage_bps": CAP_BPS,
            }]
        return []


strategy = Strategy()

if __name__ == '__main__':
    makefun_bars.run(strategy.on_batch)
