FROM freqtradeorg/freqtrade:stable

# Copier la config et les strategies
COPY user_data /freqtrade/user_data
COPY config.json /freqtrade/config.json

# Wrapper: lance freqtrade, si crash, garde le container vivant pour debug
COPY start.sh /freqtrade/start.sh
RUN chmod +x /freqtrade/start.sh

ENTRYPOINT ["/freqtrade/start.sh"]
