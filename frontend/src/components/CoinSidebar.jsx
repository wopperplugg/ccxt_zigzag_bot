import React from "react";

const CoinSidebar = ({ coins, onSelect, selectedSymbol }) => {
  return (
    <div className="bg-dark text-white border-end h-100 d-flex flex-column p-3">
      <h5 className="fw-bold mb-3">Монеты</h5>

      {/* Добавлен flex-grow-1 и overflow-y-auto для скролла */}
      <div className="list-group list-group-flush flex-grow-1 overflow-y-auto custom-scrollbar">
        {coins.map((coin) => (
          <button
            key={coin}
            className={`list-group-item list-group-item-action d-flex justify-content-between align-items-center bg-transparent border-0 px-2 ${
              selectedSymbol === coin 
                ? "text-primary bg-secondary bg-opacity-25" // Подсветка фона активного
                : "text-white"
            }`}
            onClick={() => onSelect(coin)}
            style={{ transition: '0.2s' }} // Плавный переход цвета
          >
            <span className={selectedSymbol === coin ? "fw-bold" : ""}>{coin}</span>
            <span className="badge bg-success rounded-pill" style={{ fontSize: '0.7rem' }}>Live</span>
          </button>
        ))}
      </div>
    </div>
  );
};
export default CoinSidebar;