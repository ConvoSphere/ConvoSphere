import { TextEncoder, TextDecoder } from 'util';
global.TextEncoder = TextEncoder as any;
global.TextDecoder = TextDecoder as any;

import React from 'react';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import App from './App';

// Mock für useAuthStore
jest.mock('./store/authStore', () => {
  return {
    useAuthStore: jest.fn(),
  };
});

const { useAuthStore } = require('./store/authStore');

describe('App Routing & Auth', () => {
  afterEach(() => {
    jest.clearAllMocks();
  });

  it('redirects unauthenticated users to /login from /', () => {
    useAuthStore.mockReturnValue({ isAuthenticated: false });
    render(
      <MemoryRouter initialEntries={["/"]}>
        <App />
      </MemoryRouter>
    );
    expect(screen.getByRole('heading', { name: /login/i })).toBeInTheDocument();
  });

  it('shows chat for authenticated users at /', () => {
    useAuthStore.mockReturnValue({ isAuthenticated: true });
    render(
      <MemoryRouter initialEntries={["/"]}>
        <App />
      </MemoryRouter>
    );
    expect(screen.getByText(/chat/i)).toBeInTheDocument();
  });

  it('shows login page at /login', () => {
    useAuthStore.mockReturnValue({ isAuthenticated: false });
    render(
      <MemoryRouter initialEntries={["/login"]}>
        <App />
      </MemoryRouter>
    );
    expect(screen.getByRole('heading', { name: /login/i })).toBeInTheDocument();
  });

  it('shows register page at /register', () => {
    useAuthStore.mockReturnValue({ isAuthenticated: false });
    render(
      <MemoryRouter initialEntries={["/register"]}>
        <App />
      </MemoryRouter>
    );
    expect(screen.getByRole('heading', { name: /register/i })).toBeInTheDocument();
  });
}); 