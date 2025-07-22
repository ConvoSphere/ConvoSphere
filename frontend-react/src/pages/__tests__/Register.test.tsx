import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';

// Mock muss vor dem Komponent-Import erfolgen!
jest.mock('../../store/authStore', () => {
  const actual = jest.requireActual('../../store/authStore');
  return {
    ...actual,
    useAuthStore: jest.fn(),
  };
});

import Register from '../Register';

const mockRegister = jest.fn();
const mockIsAuthenticated = false;

function renderWithRouter(ui: React.ReactElement) {
  return render(<BrowserRouter>{ui}</BrowserRouter>);
}

describe('Register', () => {
  beforeEach(() => {
    jest.resetAllMocks();
    require('../../store/authStore').useAuthStore.mockImplementation((fn: any) => {
      return fn({ register: mockRegister, isAuthenticated: mockIsAuthenticated });
    });
  });

  test('renders all form fields', () => {
    renderWithRouter(<Register />);
    expect(screen.getByLabelText(/username/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/^email$/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/confirm email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /register/i })).toBeInTheDocument();
  });

  test('validates required fields', async () => {
    renderWithRouter(<Register />);
    fireEvent.click(screen.getByRole('button', { name: /register/i }));
    await waitFor(() => {
      expect(screen.getByText(/please enter username/i)).toBeInTheDocument();
      expect(screen.getByText(/please enter email/i)).toBeInTheDocument();
      expect(screen.getByText(/please confirm your email/i)).toBeInTheDocument();
      expect(screen.getByText(/please enter password/i)).toBeInTheDocument();
    });
  });

  test('validates email match', async () => {
    renderWithRouter(<Register />);
    fireEvent.change(screen.getByLabelText(/username/i), { target: { value: 'testuser' } });
    fireEvent.change(screen.getByLabelText(/^email$/i), { target: { value: 'test@example.com' } });
    fireEvent.change(screen.getByLabelText(/confirm email/i), { target: { value: 'wrong@example.com' } });
    fireEvent.change(screen.getByLabelText(/password/i), { target: { value: 'password123' } });
    fireEvent.click(screen.getByRole('button', { name: /register/i }));
    await waitFor(() => {
      expect(screen.getByText(/email addresses do not match/i)).toBeInTheDocument();
    });
  });

  test('shows success message on successful registration', async () => {
    mockRegister.mockResolvedValueOnce(undefined);
    renderWithRouter(<Register />);
    fireEvent.change(screen.getByLabelText(/username/i), { target: { value: 'testuser' } });
    fireEvent.change(screen.getByLabelText(/^email$/i), { target: { value: 'test@example.com' } });
    fireEvent.change(screen.getByLabelText(/confirm email/i), { target: { value: 'test@example.com' } });
    fireEvent.change(screen.getByLabelText(/password/i), { target: { value: 'password123' } });
    fireEvent.click(screen.getByRole('button', { name: /register/i }));
    await waitFor(() => {
      expect(screen.getByText(/registration successful/i)).toBeInTheDocument();
    });
  });

  test('shows error message on registration failure', async () => {
    mockRegister.mockRejectedValueOnce(new Error('fail'));
    renderWithRouter(<Register />);
    fireEvent.change(screen.getByLabelText(/username/i), { target: { value: 'testuser' } });
    fireEvent.change(screen.getByLabelText(/^email$/i), { target: { value: 'test@example.com' } });
    fireEvent.change(screen.getByLabelText(/confirm email/i), { target: { value: 'test@example.com' } });
    fireEvent.change(screen.getByLabelText(/password/i), { target: { value: 'password123' } });
    fireEvent.click(screen.getByRole('button', { name: /register/i }));
    await waitFor(() => {
      expect(screen.getByText(/registration failed/i)).toBeInTheDocument();
    });
  });

  test('navigates to login page on link click', () => {
    renderWithRouter(<Register />);
    const loginLink = screen.getByLabelText(/back to login/i);
    expect(loginLink).toBeInTheDocument();
  });
}); 