import React, { useState } from 'react';
import './App.css';

function App() {
  const [message, setMessage] = useState('');
  const [inputMessage, setInputMessage] = useState('Hello from React!');
  const [greetings, setGreetings] = useState([]);

  const handlePost = async () => {
    try {
      const response = await fetch('http://localhost:8000/greetings', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: inputMessage })
      });
      if (!response.ok) throw new Error('Ошибка при отправке');
      const data = await response.json();
      setMessage(`Записано: ${data.message}`);
    } catch (error) {
      setMessage(`Ошибка: ${error.message}`);
    }
  };

  const handleGet = async () => {
    try {
      const response = await fetch('http://localhost:8000/greetings');
      if (!response.ok) throw new Error('Ошибка при получении');
      const data = await response.json();
      setGreetings(data);
    } catch (error) {
      setMessage(`Ошибка: ${error.message}`);
    }
  };

  return (
    <div style={{ padding: '20px' }}>
      <h1>CRM для кадровиков</h1>
      <div>
        <h2>Запись в БД</h2>
        <input
          type="text"
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          style={{ marginRight: '10px', padding: '5px' }}
        />
        <button onClick={handlePost}>Отправить</button>
        <p>{message}</p>
      </div>
      <div>
        <h2>Чтение из БД</h2>
        <button onClick={handleGet}>Получить все записи</button>
        <ul>
          {greetings.map((g, index) => (
            <li key={index}>{g.message} (время: {g.timestamp})</li>
          ))}
        </ul>
      </div>
    </div>
  );
}

export default App;