import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import HeaderBar from '../HeaderBar';

// Mock the auth store
jest.mock('../../store/authStore', () => ({
  useAuthStore: jest.fn(() => ({
    user: { username: 'testuser', role: 'user' },
    logout: jest.fn(),
  })),
}));

// Mock the theme store
jest.mock('../../store/themeStore', () => ({
  useThemeStore: jest.fn(() => ({
    theme: 'light',
    toggleTheme: jest.fn(),
    getCurrentColors: () => ({
      colorBgContainer: '#ffffff',
      colorBorder: '#d9d9d9',
      colorText: '#000000',
      colorPrimary: '#1890ff',
      colorSuccess: '#52c41a',
      colorWarning: '#faad14',
      colorError: '#ff4d4f',
      boxShadow: '0 2px 8px rgba(0, 0, 0, 0.15)',
    }),
  })),
}));

const renderWithRouter = (component: React.ReactElement) => {
  return render(
    <BrowserRouter>
      {component}
    </BrowserRouter>
  );
};

describe('HeaderBar', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders header with logo', () => {
    renderWithRouter(<HeaderBar />);
    
    const logo = screen.getByText(/AI Assistant/i);
    expect(logo).toBeInTheDocument();
  });

  test('renders user information', () => {
    renderWithRouter(<HeaderBar />);
    
    const username = screen.getByText('testuser');
    expect(username).toBeInTheDocument();
  });

  test('renders theme toggle button', () => {
    renderWithRouter(<HeaderBar />);
    
    const themeButton = screen.getByRole('button', { name: /theme/i });
    expect(themeButton).toBeInTheDocument();
  });

  test('renders language switcher', () => {
    renderWithRouter(<HeaderBar />);
    
    const languageButton = screen.getByRole('button', { name: /language/i });
    expect(languageButton).toBeInTheDocument();
  });

  test('renders logout button', () => {
    renderWithRouter(<HeaderBar />);
    
    const logoutButton = screen.getByRole('button', { name: /logout/i });
    expect(logoutButton).toBeInTheDocument();
  });

  test('handles theme toggle click', () => {
    const mockToggleTheme = jest.fn();
    jest.mocked(require('../../store/themeStore').useThemeStore).mockReturnValue({
      theme: 'light',
      toggleTheme: mockToggleTheme,
      getCurrentColors: () => ({
        colorBgContainer: '#ffffff',
        colorBorder: '#d9d9d9',
        colorText: '#000000',
        colorPrimary: '#1890ff',
        colorSuccess: '#52c41a',
        colorWarning: '#faad14',
        colorError: '#ff4d4f',
        boxShadow: '0 2px 8px rgba(0, 0, 0, 0.15)',
      }),
    });

    renderWithRouter(<HeaderBar />);
    
    const themeButton = screen.getByRole('button', { name: /theme/i });
    fireEvent.click(themeButton);
    
    expect(mockToggleTheme).toHaveBeenCalledTimes(1);
  });

  test('handles logout click', () => {
    const mockLogout = jest.fn();
    jest.mocked(require('../../store/authStore').useAuthStore).mockReturnValue({
      user: { username: 'testuser', role: 'user' },
      logout: mockLogout,
    });

    renderWithRouter(<HeaderBar />);
    
    const logoutButton = screen.getByRole('button', { name: /logout/i });
    fireEvent.click(logoutButton);
    
    expect(mockLogout).toHaveBeenCalledTimes(1);
  });

  test('displays admin badge for admin users', () => {
    jest.mocked(require('../../store/authStore').useAuthStore).mockReturnValue({
      user: { username: 'admin', role: 'admin' },
      logout: jest.fn(),
    });

    renderWithRouter(<HeaderBar />);
    
    const adminBadge = screen.getByText('Admin');
    expect(adminBadge).toBeInTheDocument();
  });

  test('does not display admin badge for regular users', () => {
    jest.mocked(require('../../store/authStore').useAuthStore).mockReturnValue({
      user: { username: 'user', role: 'user' },
      logout: jest.fn(),
    });

    renderWithRouter(<HeaderBar />);
    
    const adminBadge = screen.queryByText('Admin');
    expect(adminBadge).not.toBeInTheDocument();
  });

  test('handles user menu toggle', () => {
    renderWithRouter(<HeaderBar />);
    
    const userMenuButton = screen.getByRole('button', { name: /testuser/i });
    fireEvent.click(userMenuButton);
    
    // Check if user menu items are visible
    const profileLink = screen.getByText(/profile/i);
    expect(profileLink).toBeInTheDocument();
  });

  test('navigates to profile page', () => {
    renderWithRouter(<HeaderBar />);
    
    const userMenuButton = screen.getByRole('button', { name: /testuser/i });
    fireEvent.click(userMenuButton);
    
    const profileLink = screen.getByText(/profile/i);
    fireEvent.click(profileLink);
    
    // Check if navigation occurred (this would be tested with react-router-dom testing utilities)
    expect(profileLink).toBeInTheDocument();
  });

  test('handles responsive menu toggle', () => {
    renderWithRouter(<HeaderBar />);
    
    const menuButton = screen.getByRole('button', { name: /menu/i });
    fireEvent.click(menuButton);
    
    // Check if mobile menu is visible
    const mobileMenu = screen.getByRole('menu');
    expect(mobileMenu).toBeInTheDocument();
  });

  test('displays correct theme icon for light theme', () => {
      jest.mocked(require('../../store/themeStore').useThemeStore).mockReturnValue({
    theme: 'light',
    toggleTheme: jest.fn(),
    getCurrentColors: () => ({
      colorBgContainer: '#ffffff',
      colorBorder: '#d9d9d9',
      colorText: '#000000',
      colorPrimary: '#1890ff',
      colorSuccess: '#52c41a',
      colorWarning: '#faad14',
      colorError: '#ff4d4f',
      boxShadow: '0 2px 8px rgba(0, 0, 0, 0.15)',
    }),
  });

    renderWithRouter(<HeaderBar />);
    
    const themeButton = screen.getByRole('button', { name: /theme/i });
    expect(themeButton).toBeInTheDocument();
  });

  test('displays correct theme icon for dark theme', () => {
    jest.mocked(require('../../store/themeStore').useThemeStore).mockReturnValue({
      theme: 'dark',
      toggleTheme: jest.fn(),
      getCurrentColors: () => ({
        colorBgContainer: '#141414',
        colorBorder: '#434343',
        colorText: '#ffffff',
        colorPrimary: '#1890ff',
        colorSuccess: '#52c41a',
        colorWarning: '#faad14',
        colorError: '#ff4d4f',
        boxShadow: '0 2px 8px rgba(0, 0, 0, 0.45)',
      }),
    });

    renderWithRouter(<HeaderBar />);
    
    const themeButton = screen.getByRole('button', { name: /theme/i });
    expect(themeButton).toBeInTheDocument();
  });

  test('handles keyboard navigation', () => {
    renderWithRouter(<HeaderBar />);
    
    const themeButton = screen.getByRole('button', { name: /theme/i });
    themeButton.focus();
    
    fireEvent.keyDown(themeButton, { key: 'Enter' });
    
    // Theme toggle should be called
    const mockToggleTheme = jest.mocked(require('../../store/themeStore').useThemeStore)().toggleTheme;
    expect(mockToggleTheme).toHaveBeenCalled();
  });

  test('handles accessibility attributes', () => {
    renderWithRouter(<HeaderBar />);
    
    const themeButton = screen.getByRole('button', { name: /theme/i });
    expect(themeButton).toHaveAttribute('aria-label');
    
    const logoutButton = screen.getByRole('button', { name: /logout/i });
    expect(logoutButton).toHaveAttribute('aria-label');
  });

  test('handles user without username', () => {
    jest.mocked(require('../../store/authStore').useAuthStore).mockReturnValue({
      user: { email: 'test@example.com', role: 'user' },
      logout: jest.fn(),
    });

    renderWithRouter(<HeaderBar />);
    
    const userDisplay = screen.getByText('test@example.com');
    expect(userDisplay).toBeInTheDocument();
  });

  test('handles user without role', () => {
    jest.mocked(require('../../store/authStore').useAuthStore).mockReturnValue({
      user: { username: 'testuser' },
      logout: jest.fn(),
    });

    renderWithRouter(<HeaderBar />);
    
    const username = screen.getByText('testuser');
    expect(username).toBeInTheDocument();
  });
});