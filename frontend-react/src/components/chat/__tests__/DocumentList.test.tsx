import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import DocumentList from '../DocumentList';
import { Document } from '../../../services/knowledge';

describe('DocumentList', () => {
  const documents: Document[] = [
    {
      id: '1',
      title: 'Doc 1',
      document_type: 'pdf',
      file_size: 1234,
      created_at: '2023-01-01',
      tags: [{ id: 't1', name: 'Tag1' }],
      language: 'en',
      file_name: 'doc1.pdf',
      description: 'desc',
      author: 'author',
      year: 2023,
      page_count: 1,
      keywords: ['kw1'],
      mime_type: 'application/pdf',
      status: 'processed',
      chunk_count: 1,
      total_tokens: 100,
      processed_at: '2023-01-02',
      source: 'src',
    },
    {
      id: '2',
      title: 'Doc 2',
      document_type: 'txt',
      file_size: 5678,
      created_at: '2023-01-03',
      tags: [],
      language: 'de',
      file_name: 'doc2.txt',
      description: '',
      author: '',
      year: 2022,
      page_count: 2,
      keywords: [],
      mime_type: 'text/plain',
      status: 'uploaded',
      chunk_count: 2,
      total_tokens: 200,
      processed_at: '',
      source: '',
    }
  ];

  it('renders all documents', () => {
    render(
      <DocumentList
        documents={documents}
        selectedDocuments={[]}
        onDocumentClick={jest.fn()}
      />
    );
    expect(screen.getByText('Doc 1')).toBeInTheDocument();
    expect(screen.getByText('Doc 2')).toBeInTheDocument();
  });

  it('calls onDocumentClick when a document is clicked', () => {
    const onDocumentClick = jest.fn();
    render(
      <DocumentList
        documents={documents}
        selectedDocuments={[]}
        onDocumentClick={onDocumentClick}
      />
    );
    fireEvent.click(screen.getByText('Doc 1'));
    expect(onDocumentClick).toHaveBeenCalledWith(documents[0]);
  });

  it('shows selected document with different style', () => {
    render(
      <DocumentList
        documents={documents}
        selectedDocuments={[documents[1]]}
        onDocumentClick={jest.fn()}
      />
    );
    const doc2 = screen.getByText('Doc 2');
    expect(doc2.closest('li')).toHaveStyle('background-color: #f6ffed');
  });
});