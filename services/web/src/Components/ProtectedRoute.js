import React, { useContext } from 'react';
import { Redirect, Route } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';

// Pages that need a logged-in user. In v1 these crashed on `user.username`
// when nobody was logged in; now they redirect to /login instead.
const ProtectedRoute = ({ children, ...rest }) => {
  const { user, loading } = useContext(AuthContext);
  return (
    <Route
      {...rest}
      render={({ location }) => {
        if (loading) return <div>Loading...</div>;
        return user ? children : <Redirect to={{ pathname: '/login', state: { from: location } }} />;
      }}
    />
  );
};

export default ProtectedRoute;
