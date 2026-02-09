import React, { useState, useEffect, useMemo, useCallback, useRef } from "react";
import axios from "axios";
import ReactApexChart from "react-apexcharts";

const ChartPanel = ({ symbol }) => {
  const POLLING_INTERVAL = 30000;
  const MAX_CANDLES = 100;
  
  const [ohlcvData, setOhlcvData] = useState([]);
  const [zigzagData, setZigzagData] = useState([]);
  const [showZigZag, setShowZigZag] = useState(true);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [lastUpdate, setLastUpdate] = useState(null);
  const [websocketConnected, setWebsocketConnected] = useState(false);
  
  const wsRef = useRef(null);
  const initialDataLoaded = useRef(false);

  // Функция для безопасного кодирования символа для URL (заменяем / на -)
  const encodeSymbolForURL = useCallback((symbol) => {
    return encodeURIComponent(symbol.replace(/\//g, '-'));
  }, []);

  // Обработчик переключения отображения ZigZag
  const toggleZigZag = useCallback(() => {
    setShowZigZag(prev => !prev);
  }, []);

  // Функция для подключения к WebSocket
  const connectWebSocket = useCallback((symbol) => {
    if (!symbol || wsRef.current?.readyState === WebSocket.OPEN) return;

    try {
      const encodedSymbol = encodeSymbolForURL(symbol);
      const wsUrl = `ws://localhost:8001/ws/ohlcv/${encodedSymbol}/1h/`;
      
      console.log(`Попытка подключения к WebSocket: ${wsUrl}`);
      
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onopen = () => {
        console.log(`WebSocket успешно подключен для ${symbol}`);
        setWebsocketConnected(true);
        
        // Запрашиваем начальные данные
        ws.send(JSON.stringify({ action: 'subscribe' }));
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          
          if (data.type === 'initial_data') {
            // Устанавливаем начальные данные
            setOhlcvData(prev => {
              const newCandles = [...prev, ...data.candles].slice(-MAX_CANDLES);
              return newCandles;
            });
            setZigzagData(data.zigzag || []);
          } else if (data.type === 'candle_update') {
            // Обновляем данные новой свечой
            setOhlcvData(prev => {
              const updated = [...prev, data.candle].slice(-MAX_CANDLES);
              return updated;
            });
            setLastUpdate(new Date().toLocaleTimeString());
          }
        } catch (parseError) {
          console.error('Ошибка парсинга WebSocket сообщения:', parseError);
        }
      };

      ws.onclose = (event) => {
        console.log(`WebSocket отключен для ${symbol}`, event.code, event.reason);
        setWebsocketConnected(false);
      };

      ws.onerror = (error) => {
        console.error(`WebSocket ошибка для ${symbol}:`, error);
        setWebsocketConnected(false);
      };

    } catch (error) {
      console.error('Ошибка подключения WebSocket:', error);
      setWebsocketConnected(false);
    }
  }, [encodeSymbolForURL]);

  // Загрузка начальных данных и подключение WebSocket
  useEffect(() => {
    if (!symbol) {
      setOhlcvData([]);
      setZigzagData([]);
      setError(null);
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }
      setWebsocketConnected(false);
      return;
    }

    // Подключаем WebSocket
    connectWebSocket(symbol);

    // Загружаем начальные данные для заполнения истории
    const controller = new AbortController();
    const signal = controller.signal;
    let isMounted = true;

    const fetchInitialData = async () => {
      setIsLoading(true);
      setError(null);
      
      try {
        const encodedSymbol = encodeSymbolForURL(symbol);
        console.log(`Запрос начальных данных для ${symbol}, URL: ${encodedSymbol}`);
        const response = await axios.get(`/api/v1/ohlcv/${encodedSymbol}/1h/`, { signal });
        
        if (!isMounted) return;
        
        const { results } = response.data;
        if (results?.ohlcv) {
          setOhlcvData(results.ohlcv.slice(-MAX_CANDLES));
          setZigzagData(results.zigzag || []);
          setLastUpdate(new Date().toLocaleTimeString());
          initialDataLoaded.current = true;
        } else {
          throw new Error("Некорректный формат данных");
        }
      } catch (err) {
        if (!isMounted || axios.isCancel(err)) return;
        
        setError(err.response?.data?.message || err.message || "Неизвестная ошибка загрузки данных");
        console.error("Ошибка загрузки OHLCV данных:", err);
        setOhlcvData([]);
        setZigzagData([]);
      } finally {
        if (isMounted) setIsLoading(false);
      }
    };

    fetchInitialData();

    return () => {
      isMounted = false;
      controller.abort();
      
      // Закрываем WebSocket при размонтировании компонента
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }
    };
  }, [symbol, connectWebSocket, encodeSymbolForURL]);

  // Остальная часть кода остается без изменений...
  const series = useMemo(() => {
    const baseSeries = [];
    
    // Добавляем свечи только при наличии данных
    if (ohlcvData.length > 0) {
      baseSeries.push({
        name: "Price",
        type: "candlestick",
        data: ohlcvData.map(item => ({
          x: new Date(item.candle_time).getTime(),
          y: [
            parseFloat(item.open),
            parseFloat(item.high),
            parseFloat(item.low),
            parseFloat(item.close)
          ]
        }))
      });
    }

    // Добавляем ZigZag при наличии данных и включенного флага
    if (showZigZag && zigzagData.length > 1) {
      baseSeries.push({
        name: "ZigZag",
        type: "line",
        color: "#FFD700",
        data: zigzagData.map(point => ({
          x: new Date(point.time).getTime(),
          y: parseFloat(point.price)
        }))
      });
    }
    
    return baseSeries;
  }, [ohlcvData, zigzagData, showZigZag]);

  const options = useMemo(() => {
    const hasZigZag = showZigZag && zigzagData.length > 1;
    const seriesCount = (ohlcvData.length > 0 ? 1 : 0) + (hasZigZag ? 1 : 0);
    
    return {
      chart: {
        type: "line",
        height: "100%",
        background: "transparent",
        toolbar: { 
          show: true,
          tools: {
            download: true,
            selection: true,
            zoom: true,
            zoomin: true,
            zoomout: true,
            pan: true,
            reset: true
          }
        },
        animations: {
          enabled: false
        }
      },
      theme: { mode: "dark" },
      xaxis: { 
        type: "datetime",
        labels: {
          datetimeFormatter: {
            year: 'yyyy',
            month: "MMM 'yy",
            day: 'dd MMM',
            hour: 'HH:mm'
          }
        }
      },
      yaxis: {
        decimalsInFloat: 8,
        labels: {
          formatter: (value) => value.toLocaleString('en', { maximumFractionDigits: 8 })
        }
      },
      stroke: {
        width: Array(seriesCount).fill(0).map((_, i) => i === 0 ? 1 : 3),
        curve: "straight"
      },
      plotOptions: {
        candlestick: {
          colors: { 
            upward: "#00C853", 
            downward: "#FF1744" 
          }
        }
      },
      markers: {
        size: Array(seriesCount).fill(0).map((_, i) => i === 0 ? 0 : 4),
        strokeWidth: 0,
        hover: { size: 6 }
      },
      tooltip: {
        theme: "dark",
        x: { format: "dd MMM yyyy HH:mm" },
        y: {
          formatter: (value, { seriesIndex, dataPointIndex}) => {
            if (seriesIndex === 0 && ohlcvData[dataPointIndex]) {
              const { open, high, low, close } = ohlcvData[dataPointIndex];
              return `Open: ${open}<br>High: ${high}<br>Low: ${low}<br>Close: ${close}`;
            }
            return value !== undefined ? value.toFixed(8) : '';
          }
        }
      },
      grid: {
        borderColor: '#333',
        strokeDashArray: 3,
        position: 'back'
      },
      legend: {
        position: 'top',
        horizontalAlign: 'left',
        onItemClick: { toggleDataSeries: false }
      }
    };
  }, [showZigZag, zigzagData, ohlcvData]);

  const renderContent = () => {
    if (!symbol) {
      return (
        <div className="h-100 d-flex align-items-center justify-content-center text-muted">
          Выберите монету для отображения графика
        </div>
      );
    }

    if (error) {
      return (
        <div className="h-100 d-flex flex-column align-items-center justify-content-center text-danger p-3">
          <i className="bi bi-exclamation-triangle fs-1 mb-2"></i>
          <p className="text-center">{error}</p>
          <button 
            className="btn btn-sm btn-outline-primary mt-2" 
            onClick={() => window.location.reload()}
          >
            Повторить попытку
          </button>
        </div>
      );
    }

    if (isLoading) {
      return (
        <div className="h-100 d-flex align-items-center justify-content-center">
          <div className="spinner-border text-primary" role="status">
            <span className="visually-hidden">Загрузка...</span>
          </div>
        </div>
      );
    }

    if (ohlcvData.length === 0) {
      return (
        <div className="h-100 d-flex align-items-center justify-content-center text-muted">
          Нет данных для отображения графика
        </div>
      );
    }

    return (
      <ReactApexChart 
        options={options} 
        series={series} 
        height="100%" 
      />
    );
  };

  return (
    <div 
      className="chart-container d-flex flex-column h-100 bg-dark text-light border rounded"
      role="region"
      aria-label={`График цены для ${symbol || 'не выбрана'}`}
    >
      <div className="d-flex justify-content-between align-items-center p-3 border-bottom border-secondary">
        <div>
          <h4 className="m-0 fw-bold">{symbol || '—'} • 1h</h4>
          <div className="d-flex flex-wrap gap-3">
            {lastUpdate && (
              <small className="text-muted">
                Обновлено: {lastUpdate}
              </small>
            )}
            <small className={`d-flex align-items-center ${websocketConnected ? 'text-success' : 'text-warning'}`}>
              <span className={`me-1 ${websocketConnected ? 'text-success' : 'text-warning'}`}>
                ●
              </span>
              {websocketConnected ? 'WebSocket Подключен' : 'WebSocket Оффлайн'}
            </small>
          </div>
        </div>
        <button 
          onClick={toggleZigZag}
          className={`btn btn-sm d-flex align-items-center ${
            showZigZag && zigzagData.length > 1 
              ? "btn-warning" 
              : "btn-outline-secondary"
          }`}
          aria-pressed={showZigZag}
          aria-label={showZigZag ? "Скрыть индикатор ZigZag" : "Показать индикатор ZigZag"}
          disabled={zigzagData.length <= 1 && !showZigZag}
          title={zigzagData.length <= 1 ? "Недостаточно данных для отображения ZigZag" : ""}
        >
          <span className="me-1">◇</span>
          {showZigZag ? "Скрыть ZigZag" : "Показать ZigZag"}
          {zigzagData.length <= 1 && showZigZag && (
            <span className="ms-1 text-danger">*</span>
          )}
        </button>
      </div>

      <div className="flex-grow-1" style={{ minHeight: '400px' }}>
        {renderContent()}
      </div>
      
      {zigzagData.length <= 1 && showZigZag && (
        <div className="p-2 text-center text-warning small">
          * Индикатор временно недоступен (требуется минимум 2 точки)
        </div>
      )}
    </div>
  );
};

export default React.memo(ChartPanel);