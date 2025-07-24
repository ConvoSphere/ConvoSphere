import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import EditTagModal from '../EditTagModal';
import { Form } from 'antd';

describe('EditTagModal', () => {
  it('renders modal and form fields', () => {
    const [form] = Form.useForm();
    render(<EditTagModal open={true} form={form} onFinish={jest.fn()} onCancel={jest.fn()} />);
    expect(screen.getByText('Edit Tag')).toBeInTheDocument();
    expect(screen.getByLabelText('Tag Name')).toBeInTheDocument();
    expect(screen.getByLabelText('Description')).toBeInTheDocument();
    expect(screen.getByText('Update Tag')).toBeInTheDocument();
    expect(screen.getByText('Cancel')).toBeInTheDocument();
  });

  it('calls onCancel when Cancel button is clicked', () => {
    const [form] = Form.useForm();
    const onCancel = jest.fn();
    render(<EditTagModal open={true} form={form} onFinish={jest.fn()} onCancel={onCancel} />);
    fireEvent.click(screen.getByText('Cancel'));
    expect(onCancel).toHaveBeenCalled();
  });
});