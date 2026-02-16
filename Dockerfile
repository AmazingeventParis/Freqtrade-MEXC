FROM freqtradeorg/freqtrade:stable

# Copier la config et les strategies
COPY user_data /freqtrade/user_data
COPY config.json /freqtrade/config.json

# Script de demarrage (fix CRLF -> LF)
COPY start.sh /freqtrade/start.sh
RUN sed -i 's/\r$//' /freqtrade/start.sh && chmod +x /freqtrade/start.sh

ENTRYPOINT ["/bin/bash", "/freqtrade/start.sh"]
