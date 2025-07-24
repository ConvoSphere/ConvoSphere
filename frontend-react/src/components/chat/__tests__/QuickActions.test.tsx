import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import QuickActions from '../QuickActions';

describe('QuickActions', () => {
  const onShowHistory = jest.fn();
  const onExportConversation = jest.fn();
  const onShareConversation = jest.fn();
  const onShowSettings = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders all action buttons', () => {
    render(
      <QuickActions
        onShowHistory={onShowHistory}
        onExportConversation={onExportConversation}
        onShareConversation={onShareConversation}
        onShowSettings={onShowSettings}
      />
    );
    expect(screen.getByText('View Conversation History')).toBeInTheDocument();
    expect(screen.getByText('Export Conversation')).toBeInTheDocument();
    expect(screen.getByText('Share Conversation')).toBeInTheDocument();
    expect(screen.getByText('Chat Settings')).toBeInTheDocument();
  });

  it('calls correct callback on button click', () => {
    render(
      <QuickActions
        onShowHistory={onShowHistory}
        onExportConversation={onExportConversation}
        onShareConversation={onShareConversation}
        onShowSettings={onShowSettings}
      />
    );
    fireEvent.click(screen.getByText('View Conversation History'));
    expect(onShowHistory).toHaveBeenCalled();
    fireEvent.click(screen.getByText('Export Conversation'));
    expect(onExportConversation).toHaveBeenCalled();
    fireEvent.click(screen.getByText('Share Conversation'));
    expect(onShareConversation).toHaveBeenCalled();
    fireEvent.click(screen.getByText('Chat Settings'));
    expect(onShowSettings).toHaveBeenCalled();
  });
});