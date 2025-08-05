# Archivos de datos de ejemplo

## EUR_USD.csv
Formato esperado para datos personalizados con Bid/Ask:

```csv
Date,BidOpen,BidHigh,BidLow,BidClose,AskOpen,AskHigh,AskLow,AskClose,Volume
2025-07-10 00:00:00,1.17376,1.17377,1.17353,1.17359,1.17387,1.17388,1.17363,1.17369,278
2025-07-10 00:01:00,1.17359,1.17365,1.17355,1.17362,1.17369,1.17375,1.17365,1.17372,145
2025-07-10 00:02:00,1.17362,1.17368,1.17360,1.17365,1.17372,1.17378,1.17370,1.17375,89
```

## FX_EURUSD, 1.csv  
Formato esperado para datos de TradingView:

```csv
time,open,high,low,close,Volume
1751836440,1.17777,1.17796,1.17777,1.17796,1
1751836500,1.17796,1.17805,1.17785,1.17800,2
1751836560,1.17800,1.17815,1.17795,1.17810,3
```

## Notas importantes:

1. **EUR_USD.csv**: 
   - Debe incluir datos de Bid y Ask por separado
   - Formato de fecha: `YYYY-MM-DD HH:MM:SS`
   - Volumen opcional pero recomendado

2. **FX_EURUSD, 1.csv**:
   - Timestamp en formato Unix (segundos desde epoch)
   - Solo datos OHLC (sin separación Bid/Ask)
   - Volumen en número entero

3. **Validación de fechas**:
   - Asegúrate de que las fechas en `main.py` coincidan con los datos disponibles
   - El algoritmo está configurado para: 2025-07-05 a 2025-07-15

4. **Subida a QuantConnect**:
   - Los archivos CSV deben subirse a la sección "Data" de tu proyecto
   - Los nombres de archivo deben coincidir exactamente con los definidos en las clases `KEY`