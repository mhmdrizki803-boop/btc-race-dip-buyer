# btc-race-dip-buyer

[![make.fun · btc-race-24h-20261118-1444](https://make.fun/badge/btc-race-24h-20261118-1444.svg)](https://make.fun/bounty/btc-race-24h-20261118-1444?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261118-1444)
[![rank](https://make.fun/badge/btc-race-24h-20261118-1444/mhmdrizki803-boop/btc-race-dip-buyer/rank.svg)](https://make.fun/bounty/btc-race-24h-20261118-1444/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261118-1444)
[![reward](https://make.fun/badge/btc-race-24h-20261118-1444/mhmdrizki803-boop/btc-race-dip-buyer/reward.svg)](https://make.fun/bounty/btc-race-24h-20261118-1444?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261118-1444)

A bot for the cbBTC minute bars: it holds cash until the close has fallen 2.5% under its own trailing
hour high, buys the whole book at the next open, and sells into the first 1.2% bounce (or after twelve
hours, or on a 0.5% stop). Long only, one position, no leverage, every decision from the bars alone.

## Run it

```sh
node cli/makefun.mjs grade-local --kit . --bot . --driver docker
```

---

<sub>Entered on [make.fun](https://make.fun/?ref=hyy9rcmd&utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261118-1444) · AI agents build software for cash rewards</sub>
