FROM freqtradeorg/freqtrade:stable

# Passer en root pour les operations de fichiers
USER root

# Copier la config et les strategies
COPY user_data /freqtrade/user_data
COPY config.json /freqtrade/config.json

# Script de demarrage (fix CRLF -> LF)
COPY start.sh /freqtrade/start.sh
RUN sed -i 's/\r$//' /freqtrade/start.sh && chmod +x /freqtrade/start.sh

# Installer FreqUI (dashboard web)
RUN mkdir -p /freqtrade/freqtrade/rpc/api_server/ui/installed && \
    curl -L https://github.com/freqtrade/frequi/releases/latest/download/frequi.zip -o /tmp/frequi.zip && \
    python3 -c "import zipfile; zipfile.ZipFile('/tmp/frequi.zip').extractall('/freqtrade/freqtrade/rpc/api_server/ui/installed/')" && \
    rm /tmp/frequi.zip

# Remettre l'utilisateur ftuser
USER ftuser

ENTRYPOINT ["/bin/bash", "/freqtrade/start.sh"]
