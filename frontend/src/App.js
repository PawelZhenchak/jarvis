import React, { useState, useEffect, useRef } from 'react';
import './App.css';

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [chatId, setChatId] = useState(null);
  const [allChats, setAllChats] = useState([]);
  const [isTyping, setIsTyping] = useState(false); // Nowa zmienna stanu dla wskaźnika pisania
  const messagesEndRef = useRef(null);

  // Funkcja do przewijania czatu na dół
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  // Pobieranie historii czatów i aktywnego chat_id przy ładowaniu strony
  useEffect(() => {
    const pathChatId = window.location.pathname.split('/').pop();
    if (pathChatId && pathChatId !== 'chat') {
      setChatId(pathChatId);
    } else {
      // Jeśli brak chat_id w URL, przekieruj na nowy czat
      window.location.href = '/'; // Flask przekieruje na nowy chat_id
    }

    const fetchChats = async () => {
      try {
        const response = await fetch(`/chat_data?chat_id=${pathChatId}`); // Użyj pathChatId do pobrania historii
        const data = await response.json();
        setAllChats(data.all_chats);
        if (data.chat_history && data.chat_history.length > 0) {
          setMessages(data.chat_history);
        }
      } catch (error) {
        console.error('Błąd pobierania danych czatów:', error);
      }
    };
    fetchChats();
  }, [chatId]); // Zależność od chatId, aby odświeżać po zmianie czatu

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async () => {
    if (input.trim() === '') return;
    if (!chatId) return; // Upewnij się, że mamy chat_id

    const userMessage = { role: 'user', content: input };
    setMessages((prevMessages) => [...prevMessages, userMessage]);
    setInput('');
    setIsTyping(true); // Jarvis zaczyna pisać

    try {
      const response = await fetch('/ask', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: input, chat_id: chatId }),
      });
      const data = await response.json();
      const assistantMessage = { role: 'assistant', content: data.content };
      setMessages((prevMessages) => [...prevMessages, assistantMessage]);
    } catch (error) {
      console.error('Błąd wysyłania wiadomości:', error);
      setMessages((prevMessages) => [...prevMessages, { role: 'assistant', content: 'Przepraszam, coś poszło nie tak.' }]);
    } finally {
      setIsTyping(false); // Jarvis skończył pisać
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) { // Dodano !e.shiftKey, aby Enter bez Shift wysyłał wiadomość
      e.preventDefault(); // Zapobiega nowej linii w textarea
      sendMessage();
    }
  };

  const handleChatSelect = (selectedChatId) => {
    window.location.href = `/chat/${selectedChatId}`;
  };

  const handleDeleteChat = async (chatToDeleteId) => {
    if (window.confirm('Czy na pewno chcesz usunąć ten czat?')) {
      try {
        const response = await fetch('/delete_chat', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ chat_id: chatToDeleteId }),
        });
        const data = await response.json();
        if (data.success) {
          alert(data.message);
          // Przekieruj na nowy czat po usunięciu
          window.location.href = '/';
        } else {
          alert('Błąd podczas usuwania czatu: ' + data.error);
        }
      } catch (error) {
        console.error('Błąd usuwania czatu:', error);
        alert('Wystąpił błąd podczas usuwania czatu.');
      }
    }
  };

  const handleSummarizeChat = async () => {
    if (!chatId) return;
    try {
      const response = await fetch('/summarize_chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ chat_id: chatId }),
      });
      const data = await response.json();
      if (data.success) {
        alert('Czat podsumowany! Tytuł: ' + data.title);
        // Odśwież listę czatów, aby pokazać nowy tytuł
        window.location.reload(); // Proste odświeżenie strony
      } else {
        alert('Błąd podczas podsumowywania czatu: ' + data.error);
      }
    } catch (error) {
      console.error('Błąd podsumowywania czatu:', error);
      alert('Wystąpił błąd podczas podsumowywania czatu.');
    }
  };

  return (
    <div className="App">
      <div className="sidebar">
        <div className="logo-container">
          {/* Placeholder na logo Jarvisa */}
          <div className="jarvis-logo"></div>
          <h2>Jarvis Pawel i Ola</h2>
        </div>
        <div className="chat-list">
          <h3>Twoje Czaty</h3>
          <ul>
            {allChats.map((chat) => (
              <li key={chat.chat_id} className={chat.chat_id === chatId ? 'active' : ''}>
                <span onClick={() => handleChatSelect(chat.chat_id)}>
                  {chat.title || chat.chat_id} {/* Wyświetl tytuł lub ID */}
                </span>
                <button onClick={() => handleDeleteChat(chat.chat_id)} className="delete-chat-btn">X</button>
              </li>
            ))}
          </ul>
          <button onClick={() => window.location.href = '/'}>Nowy Czat</button>
        </div>
      </div>
      <div className="main-content">
        <div className="messages-display">
          {messages.map((msg, index) => (
            <div key={index} className={`message ${msg.role}`}>
              {msg.content}
            </div>
          ))}
          {isTyping && (
            <div className="message assistant typing-indicator">
              <span>.</span><span>.</span><span>.</span>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
        <div className="input-area">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Zapytaj Jarvisa..."
            rows="3" // Zwiększona wysokość
          />
          <button onClick={sendMessage}>Wyślij</button>
        </div>
        <button onClick={handleSummarizeChat} className="summarize-chat-btn">Podsumuj Czat</button>
      </div>
    </div>
  );
}

export default App;
