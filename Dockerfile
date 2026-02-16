FROM freqtradeorg/freqtrade:stable

# Copier la config et les strategies
COPY user_data /freqtrade/user_data
COPY config.json /freqtrade/config.json

# D'abord tester que ca demarre, logger les erreurs
ENTRYPOINT ["freqtrade"]
CMD ["trade", "--config", "/freqtrade/config.json", "--strategy", "CombinedStrategy", "--db-url", "sqlite:////freqtrade/user_data/tradesv3.sqlite"]
