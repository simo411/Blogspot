import React, { useContext, useState, useEffect, useCallback } from 'react';
import { Link, useHistory } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';

const Navbar = () => {
  const { user, logout } = useContext(AuthContext);
  const history = useHistory();
  const [isDropdownOpen, setDropdownOpen] = useState(false);

  const handleLogout = () => {
    logout(); // clears the token and the user
    // Redirect to the login page after logging out
    history.push('/login');
  };

  const handleDropdownToggle = () => {
    setDropdownOpen((prevState) => !prevState);
  };

  const handleProfileClick = () => {
    // Redirect to the user's profile page
    history.push('/profile');
  };

  const handleOutsideClick = useCallback((e) => {
    if (isDropdownOpen && !e.target.classList.contains('btn-dropdown')) {
      setDropdownOpen(false);
    }
  }, [isDropdownOpen]);

  useEffect(() => {
    // Add click event listener when the component mounts
    document.addEventListener('click', handleOutsideClick);
    return () => {
      document.removeEventListener('click', handleOutsideClick);
    };
  }, [handleOutsideClick]);

  return (
    <nav className="navbar">
      {user ? (
        <>
        <div className='logo-container'>
          <div className="logo">
            Blogspot
          </div>
          </div>
        </>
      ) : null}
      <div className="links">
        {user ? (
          <>
            <Link to="/home">Home</Link>
            <Link to="/create">Write</Link>
            <button className="btn-dropdown" onClick={handleDropdownToggle}>
              {user.username}
            </button>
            {isDropdownOpen && (
              <div className="dropdown-content">

                <button onClick={handleProfileClick}>Profile</button>
                <button onClick={handleLogout}>Log out</button>
              </div>
            )}
          </>
        ) : null}
      </div>
    </nav>
  );
};

export default Navbar;
