FROM freqtradeorg/freqtrade:stable

# Copier la config et les strategies
COPY user_data /freqtrade/user_data
COPY config.json /freqtrade/config.json

# Lancer en dry-run (paper trading)
CMD ["trade", "--config", "/freqtrade/config.json", "--strategy", "CombinedStrategy"]
