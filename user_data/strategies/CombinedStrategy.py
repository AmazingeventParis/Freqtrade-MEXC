"""
CombinedStrategy - Strategie multi-indicateurs pour Freqtrade
EMA Cross + RSI + Bollinger Bands + Volume confirmation
Optimisee pour le scalping/swing court sur futures crypto
"""
import talib.abstract as ta
from freqtrade.strategy import IStrategy, DecimalParameter, IntParameter
from pandas import DataFrame


class CombinedStrategy(IStrategy):
    """
    Strategie combinee :
    - EMA 9/21 cross pour direction
    - RSI pour confirmation
    - Bollinger Bands pour volatilite
    - Volume spike pour confirmation
    """

    INTERFACE_VERSION = 3

    # Timeframe
    timeframe = "5m"

    # ROI (Return On Investment) - prendre les profits
    minimal_roi = {
        "0": 0.03,      # 3% immediatement
        "30": 0.02,      # 2% apres 30 min
        "60": 0.01,      # 1% apres 1h
        "120": 0.005,    # 0.5% apres 2h
    }

    # Stop loss
    stoploss = -0.02  # -2%
    trailing_stop = True
    trailing_stop_positive = 0.01    # Active trailing a +1%
    trailing_stop_positive_offset = 0.015  # Trigger a +1.5%
    trailing_only_offset_is_reached = True

    # Nombre de bougies necessaires
    startup_candle_count: int = 50

    # Futures : on peut shorter
    can_short = True

    # Parametres optimisables
    buy_rsi = IntParameter(20, 40, default=30, space="buy")
    sell_rsi = IntParameter(60, 80, default=70, space="sell")
    ema_fast = IntParameter(5, 15, default=9, space="buy")
    ema_slow = IntParameter(15, 30, default=21, space="buy")
    bb_period = IntParameter(15, 25, default=20, space="buy")

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # EMAs
        dataframe["ema_fast"] = ta.EMA(dataframe, timeperiod=self.ema_fast.value)
        dataframe["ema_slow"] = ta.EMA(dataframe, timeperiod=self.ema_slow.value)

        # RSI
        dataframe["rsi"] = ta.RSI(dataframe, timeperiod=14)

        # Bollinger Bands
        bollinger = ta.BBANDS(dataframe, timeperiod=self.bb_period.value, nbdevup=2.0, nbdevdn=2.0)
        dataframe["bb_upper"] = bollinger["upperband"]
        dataframe["bb_middle"] = bollinger["middleband"]
        dataframe["bb_lower"] = bollinger["lowerband"]
        dataframe["bb_width"] = (dataframe["bb_upper"] - dataframe["bb_lower"]) / dataframe["bb_middle"]

        # Volume moyen
        dataframe["volume_mean"] = dataframe["volume"].rolling(window=20).mean()
        dataframe["volume_spike"] = dataframe["volume"] > (dataframe["volume_mean"] * 1.5)

        # MACD
        macd = ta.MACD(dataframe, fastperiod=12, slowperiod=26, signalperiod=9)
        dataframe["macd"] = macd["macd"]
        dataframe["macdsignal"] = macd["macdsignal"]

        # ADX (force de tendance)
        dataframe["adx"] = ta.ADX(dataframe, timeperiod=14)

        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # === LONG ===
        dataframe.loc[
            (
                # EMA fast croise au-dessus de EMA slow
                (dataframe["ema_fast"] > dataframe["ema_slow"])
                & (dataframe["ema_fast"].shift(1) <= dataframe["ema_slow"].shift(1))
                # RSI pas en surachat
                & (dataframe["rsi"] < self.sell_rsi.value)
                & (dataframe["rsi"] > self.buy_rsi.value)
                # Prix au-dessus de la bande moyenne BB
                & (dataframe["close"] > dataframe["bb_middle"])
                # ADX suffisant (tendance)
                & (dataframe["adx"] > 20)
                # Volume
                & (dataframe["volume"] > 0)
            ),
            "enter_long",
        ] = 1

        # === SHORT ===
        dataframe.loc[
            (
                # EMA fast croise en-dessous de EMA slow
                (dataframe["ema_fast"] < dataframe["ema_slow"])
                & (dataframe["ema_fast"].shift(1) >= dataframe["ema_slow"].shift(1))
                # RSI pas en survente
                & (dataframe["rsi"] > self.buy_rsi.value)
                & (dataframe["rsi"] < self.sell_rsi.value)
                # Prix en-dessous de la bande moyenne BB
                & (dataframe["close"] < dataframe["bb_middle"])
                # ADX suffisant
                & (dataframe["adx"] > 20)
                # Volume
                & (dataframe["volume"] > 0)
            ),
            "enter_short",
        ] = 1

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # === Exit LONG ===
        dataframe.loc[
            (
                # EMA cross inverse
                (dataframe["ema_fast"] < dataframe["ema_slow"])
                # OU RSI en surachat
                | (dataframe["rsi"] > 75)
                # OU prix touche bande haute BB
                | (dataframe["close"] > dataframe["bb_upper"])
            ),
            "exit_long",
        ] = 1

        # === Exit SHORT ===
        dataframe.loc[
            (
                # EMA cross inverse
                (dataframe["ema_fast"] > dataframe["ema_slow"])
                # OU RSI en survente
                | (dataframe["rsi"] < 25)
                # OU prix touche bande basse BB
                | (dataframe["close"] < dataframe["bb_lower"])
            ),
            "exit_short",
        ] = 1

        return dataframe
