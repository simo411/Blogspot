import { render, screen } from '@testing-library/react';
import App from './App';
import { AuthProvider } from './context/AuthContext';

test('renders the welcome page', () => {
  render(
    <AuthProvider>
      <App />
    </AuthProvider>
  );
  expect(screen.getByText(/Welcome to Blogspot/i)).toBeInTheDocument();
  expect(screen.getByText(/Get Started/i)).toBeInTheDocument();
});
