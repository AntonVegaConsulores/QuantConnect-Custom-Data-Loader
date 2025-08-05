import pandas as pd
from AlgorithmImports import *


# --- Clase de Datos Personalizada para EURUSD ---
class CustomEurUsdTradeBar(PythonData):
    """
    Clase de datos personalizada para EURUSD.
    Lee un archivo CSV con el formato:
    Date,BidOpen,BidHigh,BidLow,BidClose,AskOpen,AskHigh,AskLow,AskClose,Volume

    Ejemplo: 2025-07-10 00:00:00,1.17376,1.17377,1.17353,1.17359,1.17387,1.17388,1.17363,1.17369,278
    
    Retorna objetos QuoteBar que contienen:
    - Datos de Bid (Open, High, Low, Close) en quote_bar.bid
    - Datos de Ask (Open, High, Low, Close) en quote_bar.ask
    - OHLC principales calculados automáticamente como promedio de Bid/Ask
    - Incorpora spreads para simulaciones realistas
    """
    
    KEY = 'EUR_USD.csv'

    def get_source(self, config: SubscriptionDataConfig, date: datetime, is_live_mode: bool) -> SubscriptionDataSource:
        """
        Especifica la fuente de datos desde ObjectStore.
        """
        return SubscriptionDataSource(CustomEurUsdTradeBar.KEY, SubscriptionTransportMedium.OBJECT_STORE)
        

    def reader(self, config: SubscriptionDataConfig, line: str, date: datetime, is_live_mode: bool) -> BaseData:
        """
        Parsea una línea del archivo CSV en un objeto QuoteBar.
        """
        if not line or line.strip() == "" or not line[0].isdigit():
            return None 

        try:
            data = line.split(',')
            
            # Parsear la marca de tiempo (debe coincidir con el formato de tu CSV)
            time_str = data[0].strip()
            time_obj = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")

            # Parsear los precios de Bid y Ask
            bid_open = float(data[1])
            bid_high = float(data[2])
            bid_low = float(data[3])
            bid_close = float(data[4])
            
            ask_open = float(data[5])
            ask_high = float(data[6])
            ask_low = float(data[7])
            ask_close = float(data[8])

            # Crear el objeto QuoteBar
            quote_bar = QuoteBar()
            quote_bar.symbol = config.symbol
            quote_bar.time = time_obj
            quote_bar.end_time = time_obj + config.increment
            quote_bar.period = config.increment
            
            # Configurar los datos de Bid (nombres en minúsculas)
            quote_bar.bid = Bar(bid_open, bid_high, bid_low, bid_close)
            
            # Configurar los datos de Ask (nombres en minúsculas)
            quote_bar.ask = Bar(ask_open, ask_high, ask_low, ask_close)
            
            # Las propiedades OHLC son read-only, se calculan automáticamente desde bid/ask
            # No necesitamos asignarlas manualmente
            
            # Establecer value como close price
            quote_bar.value = quote_bar.close
            
            return quote_bar

        except (ValueError, IndexError):
            return None


# --- Clase de Datos Personalizada para TradingView EURUSD ---
class TradingViewEurUsdTradeBar(PythonData):
    """
    Clase de datos personalizada para datos de TradingView EURUSD.
    Lee un archivo CSV con el formato:
    time,open,high,low,close,Volume
    
    Ejemplo: 1751836440,1.17777,1.17796,1.17777,1.17796,1
    
    Retorna objetos TradeBar que contienen:
    - Datos OHLC directos del archivo
    - Volumen
    - Timestamp convertido desde Unix timestamp
    """
    
    KEY = 'FX_EURUSD, 1.csv'

    def get_source(self, config: SubscriptionDataConfig, date: datetime, is_live_mode: bool) -> SubscriptionDataSource:
        """
        Especifica la fuente de datos desde ObjectStore.
        """
        return SubscriptionDataSource(TradingViewEurUsdTradeBar.KEY, SubscriptionTransportMedium.OBJECT_STORE)
        

    def reader(self, config: SubscriptionDataConfig, line: str, date: datetime, is_live_mode: bool) -> BaseData:
        """
        Parsea una línea del archivo CSV en un objeto TradeBar.
        """
        if not line or line.strip() == "" or line.startswith("time") or not line[0].isdigit():
            return None 

        try:
            data = line.split(',')
            
            # Parsear el timestamp Unix
            unix_timestamp = int(data[0])
            # Usar datetime.utcfromtimestamp para compatibilidad con QuantConnect
            time_obj = datetime.utcfromtimestamp(unix_timestamp)
            
            # Debug para las primeras 5 barras procesadas
            if hasattr(config, '_debug_count'):
                config._debug_count += 1
            else:
                config._debug_count = 1
                
            if config._debug_count <= 5:
                # Este debug se mostrará en los logs de QuantConnect
                pass  # Removemos el debug aquí para evitar spam

            # Parsear los precios OHLC
            open_price = float(data[1])
            high_price = float(data[2])
            low_price = float(data[3])
            close_price = float(data[4])
            volume = int(data[5])

            # Crear el objeto TradeBar
            trade_bar = TradeBar()
            trade_bar.symbol = config.symbol
            trade_bar.time = time_obj
            trade_bar.end_time = time_obj + config.increment
            trade_bar.period = config.increment
            
            # Configurar los datos OHLCV
            trade_bar.open = open_price
            trade_bar.high = high_price
            trade_bar.low = low_price
            trade_bar.close = close_price
            trade_bar.volume = volume
            
            # Establecer value como close price
            trade_bar.value = close_price
            
            return trade_bar

        except (ValueError, IndexError):
            # Debug para ver problemas de parsing
            return None

# --- Clases Auxiliares ---
class PairConfig:
    def __init__(self, name: str, invert_signals: bool = False):
        self.name = name
        self.invert_signals = invert_signals

class CurrencyPairAnalyzer:
    def __init__(self, config: PairConfig, algorithm: QCAlgorithm, 
                wick_to_body_ratio_threshold: float = 0.0, 
                minimum_wick_pips: float = 0.0, 
                maximum_body_pips: float = float('inf')):
        self.config = config
        self.algorithm = algorithm
        self.wick_to_body_ratio_threshold = wick_to_body_ratio_threshold
        self.minimum_wick_pips = minimum_wick_pips
        self.maximum_body_pips = maximum_body_pips
        self.bar_count = 0  # Contador para controlar logs

    def analyze_bar(self, bar) -> None:
        """
        Analiza una barra de datos (puede ser QuoteBar o TradeBar).
        Aquí iría tu lógica de análisis de velas.
        """
        self.bar_count += 1
        
        # Solo mostrar logs cada 10 barras para evitar spam
        if self.bar_count % 10 == 0:
            # Manejar tanto QuoteBar como TradeBar
            if hasattr(bar, 'bid') and hasattr(bar, 'ask'):
                # Es un QuoteBar
                bid_close = bar.bid.close
                ask_close = bar.ask.close  
                spread = ask_close - bid_close
                spread_pips = spread * 10000  # Convertir a pips (para EUR/USD)
                
                data_type = "Custom" if "CUSTOM" in self.config.name else "Official"
                self.algorithm.debug(f"{data_type} QuoteBar #{self.bar_count} at {bar.time} - Close: {bar.close:.5f}, Spread: {spread_pips:.1f} pips")
            else:
                # Es un TradeBar
                data_type = "TradingView" if "TRADINGVIEW" in self.config.name else "Unknown"
                self.algorithm.debug(f"{data_type} TradeBar #{self.bar_count} at {bar.time} - Close: {bar.close:.5f}, Volume: {bar.volume}") 

class ChartManager:
    def __init__(self, algorithm: QCAlgorithm, primary_symbol: Symbol, official_symbol: Symbol, tradingview_symbol: Symbol):
        self.algorithm = algorithm
        self.primary_symbol = primary_symbol
        self.official_symbol = official_symbol
        self.tradingview_symbol = tradingview_symbol

    def setup_charts(self) -> None:
        """
        Configura los gráficos para visualizar los datos.
        """
        # Gráfico de datos personalizados (CSV)
        custom_chart_name = "Custom_EURUSD_Chart"
        custom_chart = Chart(custom_chart_name)
        custom_chart.add_series(CandlestickSeries("Custom_Price", "$"))
        self.algorithm.add_chart(custom_chart)
        
        # Gráfico de datos oficiales de QuantConnect
        official_chart_name = "Official_EURUSD_Chart"
        official_chart = Chart(official_chart_name)
        official_chart.add_series(CandlestickSeries("Official_Price", "$"))
        self.algorithm.add_chart(official_chart)
        
        # Gráfico de datos de TradingView
        tradingview_chart_name = "TradingView_EURUSD_Chart"
        tradingview_chart = Chart(tradingview_chart_name)
        tradingview_chart.add_series(CandlestickSeries("TradingView_Price", "$"))
        self.algorithm.add_chart(tradingview_chart)
        
        # Gráfico comparativo de spreads (solo para datos con bid/ask)
        spread_chart_name = "Spread_Comparison_Chart"
        spread_chart = Chart(spread_chart_name)
        spread_chart.add_series(Series("Custom_Spread", SeriesType.LINE, "$"))
        spread_chart.add_series(Series("Official_Spread", SeriesType.LINE, "$"))
        self.algorithm.add_chart(spread_chart)

    def plot_data(self, time: datetime, custom_bar: QuoteBar, official_bar: QuoteBar = None, tradingview_bar: TradeBar = None) -> None:
        """
        Envía puntos de datos a los gráficos.
        """
        # Plotear datos personalizados
        if custom_bar is not None:
            # Convert QuoteBar to TradeBar for plotting
            custom_trade_bar = custom_bar.collapse()
            self.algorithm.plot("Custom_EURUSD_Chart", "Custom_Price", custom_trade_bar)
            
            # Calcular y plotear el spread personalizado
            custom_spread = custom_bar.ask.close - custom_bar.bid.close
            self.algorithm.plot("Spread_Comparison_Chart", "Custom_Spread", custom_spread)
        
        # Plotear datos oficiales
        if official_bar is not None:
            official_trade_bar = official_bar.collapse()
            self.algorithm.plot("Official_EURUSD_Chart", "Official_Price", official_trade_bar)
            
            # Calcular y plotear el spread oficial
            official_spread = official_bar.ask.close - official_bar.bid.close
            self.algorithm.plot("Spread_Comparison_Chart", "Official_Spread", official_spread)
        
        # Plotear datos de TradingView
        if tradingview_bar is not None:
            self.algorithm.plot("TradingView_EURUSD_Chart", "TradingView_Price", tradingview_bar)

# --- Clase Principal del Algoritmo ---
class HyperActiveSkyBlueLemur(QCAlgorithm):
    def initialize(self) -> None:
        # Asegúrate de que estas fechas coincidan con los datos presentes en tu EUR_USD.csv
        self.set_start_date(2025, 7, 5) 
        self.set_end_date(2025, 7, 15)   
        self.set_cash(100000)
        self.settings.minimum_order_margin_portfolio_percentage = 0.01
        
        # logging inicial
        self.debug("=== Iniciando algoritmo HyperActiveSkyBlueLemur ===")
        self.log("Configurando datos personalizados y oficiales para EURUSD")
        
        # Load the custom data from ObjectStore
        if not self.object_store.contains_key(CustomEurUsdTradeBar.KEY):
            try:
                content = self.download("EUR_USD.csv")
                self.object_store.save(CustomEurUsdTradeBar.KEY, content)
                self.debug("EUR_USD.csv loaded into ObjectStore successfully")
            except Exception as e:
                self.error(f"Error loading EUR_USD.csv into ObjectStore: {e}")
                return
        else:
            self.debug("EUR_USD.csv already exists in ObjectStore")
        
        # Load the TradingView data from ObjectStore
        if not self.object_store.contains_key(TradingViewEurUsdTradeBar.KEY):
            try:
                content = self.download("FX_EURUSD, 1.csv")
                self.object_store.save(TradingViewEurUsdTradeBar.KEY, content)
                self.debug("FX_EURUSD, 1.csv loaded into ObjectStore successfully")
                # Debug: mostrar las primeras líneas del archivo
                lines = content.split('\n')[:5]
                for i, line in enumerate(lines):
                    self.debug(f"TradingView Line {i}: {line}")
            except Exception as e:
                self.error(f"Error loading FX_EURUSD, 1.csv into ObjectStore: {e}")
                return
        else:
            self.debug("FX_EURUSD, 1.csv already exists in ObjectStore")
        
        # Configuración para datos personalizados
        self.primary_config = PairConfig("EURUSD")
        self.primary_ticker = self.primary_config.name

        # Agregar datos personalizados (CSV)
        try:
            self._custom_pair = self.add_data(CustomEurUsdTradeBar, 
                                                "EURUSD_CUSTOM", 
                                                Resolution.MINUTE,
                                                time_zone=TimeZones.UTC,
                                                fill_forward=False)
            self.debug(f"Datos personalizados agregados exitosamente: {self._custom_pair.symbol}")
        except Exception as e:
            self.error(f"Error agregando datos personalizados: {e}")
        
        # Agregar datos de TradingView
        try:
            self._tradingview_pair = self.add_data(TradingViewEurUsdTradeBar, 
                                                    "EURUSD_TRADINGVIEW", 
                                                    Resolution.MINUTE,
                                                    time_zone=TimeZones.UTC,
                                                    fill_forward=False)
            self.debug(f"Datos de TradingView agregados exitosamente: {self._tradingview_pair.symbol}")
        except Exception as e:
            self.error(f"Error agregando datos de TradingView: {e}")
        
        # Agregar datos oficiales de QuantConnect
        try:
            self._official_pair = self.add_forex("EURUSD", Resolution.MINUTE)
            self._official_pair.set_fee_model(ConstantFeeModel(0))
            self.debug(f"Datos oficiales agregados exitosamente: {self._official_pair.symbol}")
        except Exception as e:
            self.error(f"Error agregando datos oficiales: {e}")
        
        # Analizadores para ambos tipos de datos
        self._custom_analyzer = CurrencyPairAnalyzer(
            self.primary_config, self,
            wick_to_body_ratio_threshold=2.0,
            minimum_wick_pips=5.0,
            maximum_body_pips=0.5
        )
        
        self._official_analyzer = CurrencyPairAnalyzer(
            PairConfig("EURUSD_OFFICIAL"), self,
            wick_to_body_ratio_threshold=2.0,
            minimum_wick_pips=5.0,
            maximum_body_pips=0.5
        )
        
        self._tradingview_analyzer = CurrencyPairAnalyzer(
            PairConfig("EURUSD_TRADINGVIEW"), self,
            wick_to_body_ratio_threshold=2.0,
            minimum_wick_pips=5.0,
            maximum_body_pips=0.5
        )

        self.set_brokerage_model(BrokerageName.FXCM_BROKERAGE, AccountType.MARGIN)

        self._stop_loss_pips = 10
        self._current_position = None
        self._entry_order_placed = False
        
        # Chart manager actualizado para manejar todos los símbolos
        self._chart_manager = ChartManager(self, self._custom_pair.symbol, self._official_pair.symbol, self._tradingview_pair.symbol)
        self._chart_manager.setup_charts()
        
        # Contador para debugging
        self._data_count = 0
        self.debug("=== Inicialización completada ===")

    def on_data(self, slice: Slice) -> None:
        """
        Método principal de procesamiento de datos.
        Se llama para cada barra de datos.
        """
        self._data_count += 1
        
        # Solo mostrar logs de estado cada 20 barras
        if self._data_count % 20 == 0:
            self.debug(f"Processing bar #{self._data_count} at {self.time}")
        
        custom_bar = None
        official_bar = None
        tradingview_bar = None
        
        # Procesar datos personalizados
        if self._custom_pair.symbol in slice.quote_bars:
            custom_bar = slice.quote_bars[self._custom_pair.symbol]
            self._custom_analyzer.analyze_bar(custom_bar)
        
        # Procesar datos oficiales
        if self._official_pair.symbol in slice.quote_bars:
            official_bar = slice.quote_bars[self._official_pair.symbol]
            self._official_analyzer.analyze_bar(official_bar)
        else:
            # Solo mostrar este error ocasionalmente
            if self._data_count % 50 == 0:
                self.debug(f"No official QuoteBar data for symbol {self._official_pair.symbol}")
        
        # Procesar datos de TradingView
        if self._tradingview_pair.symbol in slice.bars:
            tradingview_bar = slice.bars[self._tradingview_pair.symbol]
            self._tradingview_analyzer.analyze_bar(tradingview_bar)
            
            # Debug adicional para TradingView
            if self._data_count % 100 == 0:
                self.debug(f"TradingView data received! Bar at {tradingview_bar.time} - Close: {tradingview_bar.close:.5f}")
        else:
            # Solo mostrar este error ocasionalmente y también verificar slice.bars
            if self._data_count % 50 == 0:
                available_symbols = [str(s) for s in slice.bars.keys()]
                self.debug(f"No TradingView TradeBar data for symbol {self._tradingview_pair.symbol}")
                self.debug(f"Available symbols in slice.bars: {available_symbols}")
                
                # También verificar si está en otros tipos de datos
                if self._tradingview_pair.symbol in slice.quote_bars:
                    self.debug("WARNING: TradingView symbol found in quote_bars instead of bars!")

        # Plotear todos los conjuntos de datos
        if custom_bar or official_bar or tradingview_bar:
            self._chart_manager.plot_data(self.time, custom_bar, official_bar, tradingview_bar)