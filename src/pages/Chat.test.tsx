import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import Chat from './Chat';

jest.mock('../services/chat', () => ({
  chatWebSocket: {
    connect: jest.fn(),
    send: jest.fn(),
    disconnect: jest.fn(),
  },
}));

describe('Chat', () => {
  it('renders input and send button', () => {
    render(<Chat />);
    expect(screen.getByPlaceholderText(/type your message/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /send/i })).toBeInTheDocument();
  });

  it('sends a message when send button is clicked', () => {
    render(<Chat />);
    const input = screen.getByPlaceholderText(/type your message/i);
    fireEvent.change(input, { target: { value: 'Hello' } });
    fireEvent.click(screen.getByRole('button', { name: /send/i }));
    expect(input).toHaveValue('');
  });
}); 