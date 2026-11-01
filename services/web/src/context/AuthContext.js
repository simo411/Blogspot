import React, { createContext, useCallback, useEffect, useState } from 'react';
import { api, setUnauthorizedHandler, tokenStore } from '../api';

const AuthContext = createContext();

const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  // While we check a saved token on page load, don't bounce the user to /login.
  const [loading, setLoading] = useState(Boolean(tokenStore.get()));

  const logout = useCallback(() => {
    tokenStore.clear();
    setUser(null);
  }, []);

  const login = useCallback(async (username, password) => {
    const { access_token, user } = await api.login(username, password);
    tokenStore.set(access_token);
    setUser(user);
    return user;
  }, []);

  useEffect(() => {
    setUnauthorizedHandler(logout);
    if (!tokenStore.get()) return;
    // Restore the session after a refresh (v1 logged you out on every reload).
    api.me()
      .then(setUser)
      .catch(logout)
      .finally(() => setLoading(false));
  }, [logout]);

  return (
    <AuthContext.Provider value={{ user, setUser, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
};

export { AuthContext, AuthProvider };
