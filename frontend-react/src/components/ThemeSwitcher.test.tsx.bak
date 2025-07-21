import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import ThemeSwitcher from './ThemeSwitcher';
import { useThemeStore } from '../store/themeStore';

jest.mock('../store/themeStore');

describe('ThemeSwitcher', () => {
  it('renders and toggles theme', () => {
    const toggleMode = jest.fn();
    (useThemeStore as jest.Mock).mockImplementation((selector) => selector({ mode: 'light', toggleMode }));
    render(<ThemeSwitcher />);
    expect(screen.getByRole('switch')).toBeInTheDocument();
    fireEvent.click(screen.getByRole('switch'));
    expect(toggleMode).toHaveBeenCalled();
    expect(screen.getByRole('switch')).toBeVisible();
  });
}); 