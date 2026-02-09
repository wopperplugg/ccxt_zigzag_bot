import React, { useState, useEffect } from "react";
import axios from "axios";
import CoinSidebar from "./components/CoinSidebar";
import ChartPanel from "./components/ChartPanel";

const App = () => {
  const [coins, setCoins] = useState([]);
  const [selectedSymbol, setSelectedSymbol] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Загрузка списка монет
  useEffect(() => {
    const fetchCoins = async () => {
      try {
        const response = await axios.get("/api/v1/coins/");
        const data = response.data;

        if (Array.isArray(data)) {
          setCoins(data);
          if (data.length > 0 && !selectedSymbol) {
            setSelectedSymbol(data[0]); // Автовыбор первой монеты
          }
        } else {
          setError("API вернул некорректные данные");
        }
      } catch (err) {
        console.error("Ошибка загрузки монет:", err);
        setError(
          err.response?.data?.detail || err.message || "Не удалось загрузить монеты"
        );
      } finally {
        setLoading(false);
      }
    };

    fetchCoins();
  }, []);

  return (
    <div className="app-container d-flex flex-column h-100 bg-dark text-white">
      {/* Header */}
      <header className="header bg-primary p-3 d-flex justify-content-between align-items-center">
        <div className="d-flex align-items-center gap-3">
          <div className="bg-white text-primary rounded-circle p-2">
            <i className="fas fa-chart-line"></i>
          </div>
          <div>
            <h1 className="mb-0 h5 fw-bold">Крипто-Дашборд</h1>
            <p className="mb-0 small opacity-75">Реальное время · Binance</p>
          </div>
        </div>
      </header>

      <main className="main-content d-flex flex-grow-1 overflow-hidden">
        {/* Убрали p-3, добавили фиксированную ширину вместо col */}
        <aside className="sidebar border-end" style={{ width: '300px', minWidth: '300px' }}>
          <CoinSidebar
            coins={coins}
            onSelect={setSelectedSymbol}
            selectedSymbol={selectedSymbol}
          />
        </aside>

        {/* Контент графика */}
        <div className="flex-grow-1 bg-dark">
          {loading ? (
            <div className="d-flex justify-content-center align-items-center h-100">
              <div className="spinner-border text-primary" role="status"></div>
            </div>
          ) : error ? (
            <div className="d-flex flex-column justify-content-center align-items-center h-100 text-danger">
              <i className="fas fa-exclamation-triangle mb-2 fa-2x"></i>
              {error}
            </div>
          ) : coins.length === 0 ? (
            <div className="d-flex justify-content-center align-items-center h-100 text-muted">
              Список монет пуст
            </div>
          ) : (
            <ChartPanel symbol={selectedSymbol} />
          )}
        </div>
      </main>


      {/* Footer */}
      <footer className="footer bg-secondary p-3 text-center small opacity-75">
        © {new Date().getFullYear()} ZigZag Dashboard • Данные обновляются в реальном времени
      </footer>
    </div>
  );
};

export default App;