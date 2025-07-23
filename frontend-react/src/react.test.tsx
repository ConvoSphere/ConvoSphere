import React from 'react';
import { render, screen } from '@testing-library/react';

const SimpleComponent = () => <div>Hello World</div>;

describe('Simple React Test', () => {
  test('should render component', () => {
    render(<SimpleComponent />);
    expect(screen.getByText('Hello World')).toBeInTheDocument();
  });
});