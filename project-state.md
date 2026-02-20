# Freqtrade-MEXC - Etat du Projet

## Vue d'ensemble
Bot de trading crypto automatise base sur Freqtrade. Binance Futures en mode dry-run (paper trading).

- **URL** : https://freqtrade.swipego.app
- **Coolify UUID** : `josos8480cswc84g4ggoo0kc`
- **Repo** : https://github.com/AmazingeventParis/Freqtrade-MEXC
- **Volume** : ft-trades-data:/freqtrade/user_data/db
- **Status** : Fonctionnel, dry-run mode

## Stack
- Freqtrade (image stable)
- Python 3 + TA-Lib + Pandas
- Exchange: Binance Futures (dry-run)
- DB: SQLite (tradesv3.dry_run.sqlite)
- Dashboard: FreqUI (web)
- Docker sur Coolify

## Config trading
- Mode: Futures, Isolated margin, Leverage x3
- Dry run: TRUE ($100 USDT virtuel)
- Max trades ouverts: 5
- Stake: 10 USDT/trade
- Timeframe: 5m
- Startup: 50 candles (~4h de warmup)

## Paires (6)
BTC/USDT:USDT, SOL/USDT:USDT, XRP/USDT:USDT, DOGE/USDT:USDT, RUNE/USDT:USDT, TRUMP/USDT:USDT

## FreqUI Dashboard
- URL: https://freqtrade.swipego.app
- Login: admin / Laurytal2
- Port interne: 8080
- JWT Secret: x7K9mP2vQ8nR4jL6wE3sA5dF1hG0tY

## Strategie: CombinedStrategy V2

### Indicateurs
- EMA (9, 21, 50), RSI (14), MACD, Bollinger Bands (20, 2 sigma), Volume MA 20, ADX (14)

### Entree Long
- EMA9 cross au-dessus EMA21 + MACD > 0 + RSI 30-70 + ADX > 15

### Entree Short
- EMA9 cross en-dessous EMA21 + MACD < 0 + RSI 30-70 + ADX > 15

### Sortie Long
- EMA9 cross sous EMA21 + MACD < 0, OU RSI > 78, OU prix touche Bollinger upper

### Sortie Short
- EMA9 cross au-dessus EMA21 + MACD > 0, OU RSI < 22, OU prix touche Bollinger lower

### Risk Management
- Stop Loss: -3%
- Trailing Stop: activation +2%, distance +1.5%
- ROI: +5% (0min), +3.5% (20min), +2.5% (45min), +1.5% (90min), +0.8% (180min)

## Structure
```
Freqtrade-MEXC/
  config.json         - Config Freqtrade (exchange, paires, API, ROI, SL)
  Dockerfile          - Build: base freqtrade + FreqUI + strategy
  start.sh            - Entrypoint (freqtrade trade)
  user_data/
    strategies/
      CombinedStrategy.py  - Strategie V2 (EMA+RSI+MACD+BB+ADX)
    db/                     - SQLite (volume monte)
```

## Integration CryptoSignals
- Onglet "FT" dans le dashboard CryptoSignals
- Endpoints proxy pour afficher trades
- Courbe P&L dans VS Comparaison

## Problemes resolus
- CRLF → LF dans start.sh
- FreqUI installation dans Dockerfile
- Database persistee via volume Docker
- Force entry active pour trades manuels

## TODO
- [ ] Backtest la strategie sur donnees historiques
- [ ] Tuner les parametres (RSI, EMA)
- [ ] Passer en live trading (dry_run: false + API keys)
- [ ] Alertes Telegram/Discord

## Deploy
```bash
git push origin main
curl -s -X GET "https://coolify.swipego.app/api/v1/deploy?uuid=josos8480cswc84g4ggoo0kc&force=true" \
  -H "Authorization: Bearer 1|FNcssp3CipkrPNVSQyv3IboYwGsP8sjPskoBG3ux98e5a576"
```
