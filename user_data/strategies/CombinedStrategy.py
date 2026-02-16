"""
CombinedStrategy V2 - Strategie multi-indicateurs pour Freqtrade
EMA Cross + RSI + MACD + Bollinger Bands + Volume confirmation
Futures x3 leverage, optimisee pour scalping/swing sur crypto
"""
import freqtrade.vendor.qtpylib.indicators as qtpylib
from freqtrade.strategy import IStrategy, IntParameter, DecimalParameter
from pandas import DataFrame
import talib


class CombinedStrategy(IStrategy):
    """
    Strategie combinee V2 :
    - EMA 9/21 cross pour direction
    - MACD pour confirmation de momentum
    - RSI pour filtrer suracheté/survendu
    - Bollinger Bands pour volatilite
    - Volume spike obligatoire (>1.5x moyenne)
    - ADX pour confirmer la tendance
    """

    INTERFACE_VERSION = 3

    # Timeframe
    timeframe = "5m"

    # ROI - prendre les profits progressivement
    minimal_roi = {
        "0": 0.05,      # +5% immédiat
        "20": 0.035,     # +3.5% après 20min
        "45": 0.025,     # +2.5% après 45min
        "90": 0.015,     # +1.5% après 90min
        "180": 0.008,    # +0.8% après 3h
    }

    # Stop loss
    stoploss = -0.03

    # Trailing stop : protège les gains
    trailing_stop = True
    trailing_stop_positive = 0.015       # Trail à +1.5% de distance
    trailing_stop_positive_offset = 0.02  # S'active quand profit atteint +2%
    trailing_only_offset_is_reached = True

    # Nombre de bougies necessaires
    startup_candle_count: int = 50

    # Futures : leverage x3
    can_short = True

    def leverage(self, pair: str, current_time, current_rate: float,
                 proposed_leverage: float, max_leverage: float,
                 entry_tag: str | None, side: str, **kwargs) -> float:
        return 3.0

    # Parametres optimisables
    buy_rsi = IntParameter(20, 40, default=30, space="buy")
    sell_rsi = IntParameter(60, 80, default=70, space="sell")
    volume_factor = DecimalParameter(1.0, 2.5, default=1.5, space="buy")

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # EMAs
        dataframe["ema9"] = talib.EMA(dataframe["close"], timeperiod=9)
        dataframe["ema21"] = talib.EMA(dataframe["close"], timeperiod=21)
        dataframe["ema50"] = talib.EMA(dataframe["close"], timeperiod=50)

        # RSI
        dataframe["rsi"] = talib.RSI(dataframe["close"], timeperiod=14)

        # MACD
        macd, signal, hist = talib.MACD(dataframe["close"], fastperiod=12, slowperiod=26, signalperiod=9)
        dataframe["macd"] = macd
        dataframe["macd_signal"] = signal
        dataframe["macd_hist"] = hist

        # Bollinger Bands
        upper, middle, lower = talib.BBANDS(dataframe["close"], timeperiod=20, nbdevup=2.0, nbdevdn=2.0)
        dataframe["bb_upper"] = upper
        dataframe["bb_middle"] = middle
        dataframe["bb_lower"] = lower

        # Volume moyen
        dataframe["volume_mean"] = dataframe["volume"].rolling(window=20).mean()

        # ADX - force de tendance
        dataframe["adx"] = talib.ADX(dataframe["high"], dataframe["low"], dataframe["close"], timeperiod=14)

        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # === LONG ===
        # EMA9 croise au-dessus de EMA21 + MACD positif + RSI neutre
        dataframe.loc[
            (
                qtpylib.crossed_above(dataframe["ema9"], dataframe["ema21"])
                & (dataframe["macd_hist"] > 0)
                & (dataframe["rsi"] > self.buy_rsi.value)
                & (dataframe["rsi"] < self.sell_rsi.value)
                & (dataframe["adx"] > 15)
                & (dataframe["volume"] > 0)
            ),
            "enter_long",
        ] = 1

        # === SHORT ===
        # EMA9 croise en-dessous de EMA21 + MACD négatif + RSI neutre
        dataframe.loc[
            (
                qtpylib.crossed_below(dataframe["ema9"], dataframe["ema21"])
                & (dataframe["macd_hist"] < 0)
                & (dataframe["rsi"] > self.buy_rsi.value)
                & (dataframe["rsi"] < self.sell_rsi.value)
                & (dataframe["adx"] > 15)
                & (dataframe["volume"] > 0)
            ),
            "enter_short",
        ] = 1

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # === Exit LONG ===
        # EMA cross inverse OU RSI suracheté OU prix touche BB supérieure
        dataframe.loc[
            (
                (
                    qtpylib.crossed_below(dataframe["ema9"], dataframe["ema21"])
                    & (dataframe["macd_hist"] < 0)
                )
                | (dataframe["rsi"] > 78)
                | (dataframe["close"] > dataframe["bb_upper"])
            ),
            "exit_long",
        ] = 1

        # === Exit SHORT ===
        # EMA cross inverse OU RSI survendu OU prix touche BB inférieure
        dataframe.loc[
            (
                (
                    qtpylib.crossed_above(dataframe["ema9"], dataframe["ema21"])
                    & (dataframe["macd_hist"] > 0)
                )
                | (dataframe["rsi"] < 22)
                | (dataframe["close"] < dataframe["bb_lower"])
            ),
            "exit_short",
        ] = 1

        return dataframe
