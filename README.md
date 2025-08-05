# QuantConnect Custom Data Loader

Un algoritmo de QuantConnect para cargar y comparar múltiples fuentes de datos personalizadas (CSV personalizado, datos oficiales de QuantConnect, TradingView) para análisis de EUR/USD con gráficos en tiempo real y comparación de spreads.

## 🌟 Características

- **Múltiples fuentes de datos**: Integra datos de 3 fuentes diferentes
  - Datos personalizados de CSV con formato Bid/Ask
  - Datos oficiales de QuantConnect
  - Datos de TradingView con timestamp Unix
- **Análisis comparativo**: Compara spreads, precios y calidad de datos entre fuentes
- **Visualización avanzada**: Gráficos separados para cada fuente de datos más comparativo de spreads
- **Gestión inteligente de datos**: Carga automática desde ObjectStore
- **Análisis de velas**: Framework extensible para análisis técnico

## 📊 Fuentes de Datos Soportadas

### 1. CSV Personalizado (EUR_USD.csv)
**Formato**: `Date,BidOpen,BidHigh,BidLow,BidClose,AskOpen,AskHigh,AskLow,AskClose,Volume`

**Ejemplo**: 
```
2025-07-10 00:00:00,1.17376,1.17377,1.17353,1.17359,1.17387,1.17388,1.17363,1.17369,278
```

### 2. TradingView (FX_EURUSD, 1.csv)
**Formato**: `time,open,high,low,close,Volume`

**Ejemplo**: 
```
1751836440,1.17777,1.17796,1.17777,1.17796,1
```

### 3. Datos Oficiales QuantConnect
- Datos de forex oficiales de QuantConnect
- Formato QuoteBar con Bid/Ask
- Resolución por minuto

## 🏗️ Arquitectura

### Clases Principales

#### `CustomEurUsdTradeBar(PythonData)`
- Parsea datos CSV personalizados con formato Bid/Ask
- Genera objetos QuoteBar con spreads realistas
- Manejo de errores robusto

#### `TradingViewEurUsdTradeBar(PythonData)`
- Parsea datos de TradingView con timestamp Unix
- Genera objetos TradeBar con datos OHLCV
- Conversión automática de timestamp

#### `CurrencyPairAnalyzer`
- Analiza barras de datos (QuoteBar y TradeBar)
- Cálculo de spreads en pips
- Sistema de logging optimizado

#### `ChartManager`
- Gestiona múltiples gráficos simultáneos
- Ploteo automático de datos comparativos
- Visualización de spreads en tiempo real

#### `HyperActiveSkyBlueLemur(QCAlgorithm)`
- Algoritmo principal de QuantConnect
- Coordinación de todas las fuentes de datos
- Gestión del ObjectStore

## 🚀 Configuración y Uso

### Requisitos Previos

1. **Archivos de datos necesarios**:
   - `EUR_USD.csv` - Datos personalizados con formato Bid/Ask
   - `FX_EURUSD, 1.csv` - Datos de TradingView

2. **Configuración de fechas**:
   ```python
   self.set_start_date(2025, 7, 5) 
   self.set_end_date(2025, 7, 15)
   ```

### Instalación

1. Sube el archivo `main.py` a tu proyecto de QuantConnect
2. Sube los archivos CSV a la sección de datos de tu proyecto
3. Ejecuta el backtest

### Personalización

#### Modificar umbrales de análisis:
```python
self._custom_analyzer = CurrencyPairAnalyzer(
    self.primary_config, self,
    wick_to_body_ratio_threshold=2.0,  # Ratio mecha/cuerpo
    minimum_wick_pips=5.0,             # Mínimo de pips de mecha
    maximum_body_pips=0.5              # Máximo de pips del cuerpo
)
```

#### Cambiar frecuencia de logging:
```python
# En CurrencyPairAnalyzer.analyze_bar()
if self.bar_count % 10 == 0:  # Cambiar por la frecuencia deseada
```

## 📈 Gráficos Generados

1. **Custom_EURUSD_Chart**: Datos del CSV personalizado
2. **Official_EURUSD_Chart**: Datos oficiales de QuantConnect  
3. **TradingView_EURUSD_Chart**: Datos de TradingView
4. **Spread_Comparison_Chart**: Comparación de spreads en tiempo real

## 🔧 Características Técnicas

- **Brokerage**: FXCM configurado por defecto
- **Resolución**: 1 minuto
- **Zona horaria**: UTC
- **Fill Forward**: Deshabilitado para datos más precisos
- **Cash inicial**: $100,000
- **Margen mínimo**: 1%

## 📝 Logging y Debug

El sistema incluye logging inteligente:
- Estados cada 20 barras procesadas
- Análisis cada 10 barras por analizador
- Debug ocasional para evitar spam de logs
- Información detallada de spreads y volúmenes

## 🤝 Contribución

Este proyecto está diseñado para ser extensible:

1. **Agregar nuevas fuentes de datos**: Crear nuevas clases que hereden de `PythonData`
2. **Nuevos indicadores**: Expandir `CurrencyPairAnalyzer`
3. **Visualizaciones adicionales**: Extender `ChartManager`
4. **Otros pares de divisas**: Adaptar las clases de datos

## 📊 Casos de Uso

- **Validación de calidad de datos** entre múltiples proveedores
- **Análisis de spreads** comparativo
- **Investigación de datos históricos** con múltiples fuentes
- **Desarrollo de estrategias** basadas en datos personalizados
- **Backtesting con datos reales** de diferentes proveedores

## ⚠️ Consideraciones

- Asegúrate de que las fechas de inicio/fin coincidan con los datos disponibles
- Los archivos CSV deben estar correctamente formateados
- El sistema detecta automáticamente tipos de datos (QuoteBar vs TradeBar)
- Los spreads se calculan automáticamente para datos con Bid/Ask

## 🏷️ Versión

**v1.0** - Implementación inicial con soporte para 3 fuentes de datos

---

**Autor**: Antón Carlos Vázquez Martínez  
**Licencia**: MIT  
**Plataforma**: QuantConnect LEAN Engine