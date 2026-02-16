"""
CombinedStrategy - Strategie multi-indicateurs pour Freqtrade
EMA Cross + RSI + Bollinger Bands + Volume confirmation
Optimisee pour le scalping/swing court sur futures crypto
"""
import freqtrade.vendor.qtpylib.indicators as qtpylib
from freqtrade.strategy import IStrategy, IntParameter
from pandas import DataFrame
import talib


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
        "0": 0.03,
        "30": 0.02,
        "60": 0.01,
        "120": 0.005,
    }

    # Stop loss
    stoploss = -0.02
    trailing_stop = True
    trailing_stop_positive = 0.01
    trailing_stop_positive_offset = 0.015
    trailing_only_offset_is_reached = True

    # Nombre de bougies necessaires
    startup_candle_count: int = 50

    # Futures : on peut shorter
    can_short = True

    # Parametres optimisables
    buy_rsi = IntParameter(20, 40, default=30, space="buy")
    sell_rsi = IntParameter(60, 80, default=70, space="sell")

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # EMAs
        dataframe["ema9"] = talib.EMA(dataframe["close"], timeperiod=9)
        dataframe["ema21"] = talib.EMA(dataframe["close"], timeperiod=21)

        # RSI
        dataframe["rsi"] = talib.RSI(dataframe["close"], timeperiod=14)

        # Bollinger Bands
        upper, middle, lower = talib.BBANDS(dataframe["close"], timeperiod=20, nbdevup=2.0, nbdevdn=2.0)
        dataframe["bb_upper"] = upper
        dataframe["bb_middle"] = middle
        dataframe["bb_lower"] = lower

        # Volume moyen
        dataframe["volume_mean"] = dataframe["volume"].rolling(window=20).mean()

        # ADX
        dataframe["adx"] = talib.ADX(dataframe["high"], dataframe["low"], dataframe["close"], timeperiod=14)

        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # === LONG ===
        dataframe.loc[
            (
                qtpylib.crossed_above(dataframe["ema9"], dataframe["ema21"])
                & (dataframe["rsi"] < self.sell_rsi.value)
                & (dataframe["rsi"] > self.buy_rsi.value)
                & (dataframe["close"] > dataframe["bb_middle"])
                & (dataframe["adx"] > 20)
                & (dataframe["volume"] > 0)
            ),
            "enter_long",
        ] = 1

        # === SHORT ===
        dataframe.loc[
            (
                qtpylib.crossed_below(dataframe["ema9"], dataframe["ema21"])
                & (dataframe["rsi"] > self.buy_rsi.value)
                & (dataframe["rsi"] < self.sell_rsi.value)
                & (dataframe["close"] < dataframe["bb_middle"])
                & (dataframe["adx"] > 20)
                & (dataframe["volume"] > 0)
            ),
            "enter_short",
        ] = 1

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # === Exit LONG ===
        dataframe.loc[
            (
                qtpylib.crossed_below(dataframe["ema9"], dataframe["ema21"])
                | (dataframe["rsi"] > 75)
                | (dataframe["close"] > dataframe["bb_upper"])
            ),
            "exit_long",
        ] = 1

        # === Exit SHORT ===
        dataframe.loc[
            (
                qtpylib.crossed_above(dataframe["ema9"], dataframe["ema21"])
                | (dataframe["rsi"] < 25)
                | (dataframe["close"] < dataframe["bb_lower"])
            ),
            "exit_short",
        ] = 1

        return dataframe
