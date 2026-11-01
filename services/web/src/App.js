import React, { useEffect, useState } from 'react';
import './index.css';
import Navbar from './Components/Navbar';
import Home from './pages/Home';
import { BrowserRouter as Router, Route, Switch } from 'react-router-dom';
import Create from './pages/Create';
import BlogDetails from './pages/BlogDetails';
import NotFound from './Components/NotFound';
import Login from './pages/Login';
import Register from './pages/Register';
import ProtectedRoute from './Components/ProtectedRoute';
import Start from './pages/Start';
import Profile from './pages/Profile';


function App() {
  const [theme, setTheme] = useState('light-theme');

  // Function to toggle the theme
  const toggleTheme = () => {
    if( theme === 'dark-theme'){
      setTheme('light-theme');
    }
    else{
      setTheme('dark-theme');
    }
  };
  
  useEffect(() => {
    document.body.className = theme;
  },[theme])
  return (
    <Router>
        <div className={"App"}>
          <Navbar />
          <div className="content">
            <Switch>
              <Route exact path="/">
                <Start />
              </Route>
              <ProtectedRoute exact path="/home">
                <Home />
              </ProtectedRoute>
              <ProtectedRoute path="/create">
                <Create />
              </ProtectedRoute>
              <ProtectedRoute path="/blogs/:id">
                <BlogDetails />
              </ProtectedRoute>
              <Route path="/login">
                <Login />
              </Route>
              <Route path="/register">
                <Register />
              </Route>
              <ProtectedRoute path="/profile">
                <Profile />
              </ProtectedRoute>
              <Route path="*">
                <NotFound />
              </Route>
            </Switch>
          </div>
          <div className="theme-switch">
            <button className={theme === 'dark-theme' ? 'sun' : 'moon'} onClick={toggleTheme}></button>
          </div>
        </div>
    </Router>
  );
}

export default App;
