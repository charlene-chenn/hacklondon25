import { useState } from 'react';
import { Route, Routes, useNavigate } from 'react-router-dom';
import './App.css'; // Import the CSS file

function App() {
    const [name, setName] = useState("");
    const [password, setPW] = useState("");
    const [number, setNumber] = useState("");
    const [language, setLanguage] = useState("");
    const [isRegister, setIsRegister] = useState(true);
    const navigate = useNavigate();

    const handleOnSubmit = async (e) => {
        e.preventDefault();
        const endpoint = isRegister ? 'register' : 'login';
        try {
          console.log("Sending request to:", endpoint);
          let result = await fetch(`http://localhost:5001/${endpoint}`, {
              method: "post",
              body: JSON.stringify({ name, password, number, language }),
              headers: {
                  'Content-Type': 'application/json'
              }
          });
          result = await result.json();
          console.warn("Received response:", result);
          if (result) {
              if (isRegister) {
                  alert("Registration successful");
                  setName("");
                  setPW("");
                  setNumber("");
                  setLanguage("");
                  navigate('/dashboard');
              } else {
                  if (result.name) {
                      alert("Login successful");
                      navigate('/dashboard');
                  } else {
                      alert("Invalid credentials");
                  }
              }
          } else {
              alert("Error saving data");
          }
      } catch (error) {
          console.error("Error:", error);
          alert("An error occurred while processing your request");
      }
    };

    return (
        <div className="center-content">
            <h1><img src="/huhai_logo.svg" alt="Huhai Logo" /></h1>
            <div>
                <button onClick={() => setIsRegister(true)}>Register</button>
                <button onClick={() => setIsRegister(false)}>Login</button>
            </div>

            <form onSubmit={handleOnSubmit}>
              <input type="text" placeholder="name" 
              value={name} onChange={(e) => setName(e.target.value)} />
              <input type="password" placeholder="password" 
              value={password} onChange={(e) => setPW(e.target.value)} />
              <br />

              {isRegister && (
                  <>
                      <input type="number" placeholder="number"
                      value={number} onChange={(e) => setNumber(e.target.value)} />
                      <input type="text" placeholder="language"
                      value={language} onChange={(e) => setLanguage(e.target.value)} />
                  </>
              )}
              
              
              <button type="submit">{isRegister ? 'Register' : 'Login'}</button>
            </form>
        </div>
    );
}

export default App;