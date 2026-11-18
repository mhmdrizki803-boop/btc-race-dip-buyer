# btc-race bot: long only, one position, one decision per closed bar
# every order is decided on the bar that just closed and fills at the next open
"""btc-race dip-buyer: agent-fun/bars-replay/v1 bot (Python 3.13, standard library only).

Holds cash until cbBTC's close has fallen DIP_BPS under its own trailing LOOKBACK_BARS-bar
high, then buys the whole book; sells into the first TAKE_PROFIT_BPS bounce, on a
STOP_LOSS_BPS stop, or after MAX_HOLD_BARS bars. Long only, one position, no leverage,
every decision from the bars alone. The vendor shim owns the wire.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "vendor"))
import makefun_bars  # noqa: E402

# --- strategy constants (bps are basis points; 10_000 bps = 100%) ---
BPS = 10_000
SYMBOL = "CBBTC"
# bars of close history the dip is measured against
LOOKBACK_BARS = 60              # keep at most this many of the latest closes
DIP_BPS = 250            # buy when close is <=2.5% under the trailing high
TAKE_PROFIT_BPS = 120    # sell when up >=1.2% over cost
STOP_LOSS_BPS = 50       # sell when down >=0.5% under cost
MAX_HOLD_BARS = 720      # sell after this many bars held
MAX_SLIPPAGE_BPS = 100   # every order's max_slippage_bps


def make_strategy():
    closes = []          # the last LOOKBACK_BARS closes of SYMBOL, oldest first
    bars_held = 0        # bars the current position has been open

    def on_batch(state, batch):
        nonlocal bars_held

        # Always fold the bar in, even while warming up: warm-up bars build history.
        close = state.close(SYMBOL)
        if close is not None:
            closes.append(close)
            if len(closes) > LOOKBACK_BARS:
                del closes[0]

        # Orders decided on a warm-up batch are rejected and never retried: wait.
        if state.warming_up:
            return []

        held = state.positions.get(SYMBOL)

        if held is None:
            bars_held = 0
            if not closes:
                return []
            high = max(closes)
            # <=2.5% under the trailing high, in integers.
            if close is None or close * BPS > high * (BPS - DIP_BPS):
                return []
            notional = min(state.cash, state.weight_room(SYMBOL))
            if notional <= 0:
                return []
            return [{
                "side": "buy",
                "symbol": SYMBOL,
                "notional_quote_units": notional,
                "max_slippage_bps": MAX_SLIPPAGE_BPS,
            }]

        # Holding: count the bar, then decide on the exit.
        bars_held += 1
        value = state.value(SYMBOL, held.qty)
        gain_bps = (value - held.cost) * BPS // held.cost if held.cost else 0
        if (
            gain_bps >= TAKE_PROFIT_BPS
            or gain_bps <= -STOP_LOSS_BPS
            or bars_held >= MAX_HOLD_BARS
        ):
            return [{
                "side": "sell",
                "symbol": SYMBOL,
                "qty": held.qty,
                "max_slippage_bps": MAX_SLIPPAGE_BPS,
            }]
        return []

    return on_batch


makefun_bars.run(make_strategy())
