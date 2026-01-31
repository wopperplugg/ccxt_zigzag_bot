import React, { useEffect, useState } from "react";
import axios from "axios";

const CoinList = () => {
  const [coins, setCoins] = useState([]); // Initialize as an array
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchCoins = async () => {
      try {
        const response = await axios.get("/api/v1/coins/");
        const data = response.data; // Extract data from response

        // Ensure `data` is an array before setting state
        if (Array.isArray(data)) {
          setCoins(data);
        } else {
          console.error("API returned invalid data:", data);
          setError("Неверный формат данных от сервера");
        }
      } catch (err) {
        console.error("Ошибка загрузки монет:", err);
        setError(
          err.response?.data?.detail ||
          err.message ||
          "Не удалось загрузить список монет"
        );
      } finally {
        setLoading(false);
      }
    };

    fetchCoins();
  }, []);

  return (
    <div className="min-vh-100 bg-light d-flex flex-column">
      <header className="bg-white shadow-sm py-4">
        <div className="container">
          <div className="d-flex align-items-center gap-3">
            <div className="bg-gradient-primary text-white rounded-circle p-3 fs-3">
              <i className="fas fa-chart-line"></i>
            </div>
            <div>
              <h1 className="mb-1">Крипто-Дашборд</h1>
              <p className="text-muted mb-0">Реальное время · Binance</p>
            </div>
          </div>
        </div>
      </header>

      <main className="flex-grow-1 py-5">
        <div className="container">
          <div className="row mb-4">
            <div className="col-12">
              <h2 className="fw-bold text-dark">
                <i className="fas fa-coins me-2 text-primary" />
                Список монет
              </h2>
              <hr className="border-primary w-25" />
            </div>
          </div>

          {loading ? (
            <div className="text-center py-5">
              <div className="spinner-border text-primary mb-3" role="status">
                <span className="visually-hidden">Загрузка...</span>
              </div>
              <p className="text-muted">Подключение к бирже...</p>
            </div>
          ) : error ? (
            <div className="alert alert-danger alert-dismissible fade show" role="alert">
              <i className="fas fa-exclamation-triangle me-2" />
              {error}
              <button
                type="button"
                className="btn-close"
                onClick={() => setError(null)}
                aria-label="Close"
              ></button>
            </div>
          ) : Array.isArray(coins) && coins.length > 0 ? (
            <div className="row g-4">
              {coins.map((coin, index) => (
                <div
                  key={index}
                  className={`col-md-6 col-lg-4 animate__animated animate__fadeInUp`}
                  style={{ animationDelay: `${index * 0.1}s` }}
                >
                  <div className="card border-0 shadow-sm h-100">
                    <div className="card-body d-flex flex-column">
                      <div className="d-flex justify-content-between align-items-start mb-3">
                        <h5 className="fw-bold mb-0">{coin}</h5>
                        <span className="badge bg-white text-dark px-2 py-1 rounded-pill">
                          <i className="fas fa-bolt me-1"></i> Live
                        </span>
                      </div>
                      <div className="mt-auto">
                        <div className="d-flex justify-content-between mb-2">
                          <span className="small opacity-90">Цена</span>
                          <span className="fw-medium">—</span>
                        </div>
                        <div className="d-flex justify-content-between mb-2">
                          <span className="small opacity-90">Объём</span>
                          <span className="fw-medium">—</span>
                        </div>
                        <div className="d-flex justify-content-between">
                          <span className="small opacity-90">Таймфрейм</span>
                          <span className="fw-medium">1h / 15m</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-5">
              <i className="fas fa-inbox fa-4x text-muted mb-3"></i>
              <h4 className="text-muted">Нет доступных монет</h4>
              <p className="text-muted">Убедитесь, что данные загружены в БД.</p>
            </div>
          )}
        </div>
      </main>

      <footer className="bg-white border-top py-3 mt-auto">
        <div className="container text-center text-muted small">
          © {new Date().getFullYear()} ZigZag Dashboard • Данные обновляются в реальном времени
        </div>
      </footer>
    </div>
  );
};

export default CoinList;