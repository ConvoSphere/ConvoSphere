import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import CreateTagModal from '../CreateTagModal';
import { Form } from 'antd';

describe('CreateTagModal', () => {
  it('renders modal and form fields', () => {
    const [form] = Form.useForm();
    render(<CreateTagModal open={true} form={form} onFinish={jest.fn()} onCancel={jest.fn()} />);
    expect(screen.getByText('Create New Tag')).toBeInTheDocument();
    expect(screen.getByLabelText('Tag Name')).toBeInTheDocument();
    expect(screen.getByLabelText('Description')).toBeInTheDocument();
    expect(screen.getByText('Create Tag')).toBeInTheDocument();
    expect(screen.getByText('Cancel')).toBeInTheDocument();
  });

  it('calls onCancel when Cancel button is clicked', () => {
    const [form] = Form.useForm();
    const onCancel = jest.fn();
    render(<CreateTagModal open={true} form={form} onFinish={jest.fn()} onCancel={onCancel} />);
    fireEvent.click(screen.getByText('Cancel'));
    expect(onCancel).toHaveBeenCalled();
  });

  // Optional: Teste onFinish mit Form-Interaktion (hier nur rudimentär)
});