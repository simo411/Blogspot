import React, { useState, useContext } from 'react';
import { useHistory, useLocation, Link } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';

const Login = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [alert, setAlert] = useState(null);
  const { login } = useContext(AuthContext);
  const history = useHistory();
  const location = useLocation();

  const handleSubmit = (e) => {
    e.preventDefault();
    login(username, password)
      .then(() => {
        // Go back to the page that sent us to /login, if any.
        const from = (location.state && location.state.from) || { pathname: '/home' };
        history.replace(from);
      })
      .catch((err) => {
        setAlert(err.status === 401
          ? '*Invalid username or password. Please try again.'
          : `*Could not log in: ${err.message}`);
      });
  };

  return (
    <div className="login">
      <div className='login-container'>
        <h2>Login</h2>
        <form onSubmit={handleSubmit}>
          <label>username:</label>
          <input
            type="text"
            autoComplete="username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />
          <label>Password:</label>
          <input
            type="password"
            autoComplete="current-password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
          <button type="submit">Login</button>
        </form>
        {alert && <p className="red-alert">{alert}</p>}
        <Link to="/register">New here?</Link>
      </div>
    </div>
  );
};

export default Login;
