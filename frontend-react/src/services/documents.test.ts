import { getDocuments, uploadDocument } from './documents';
import api from './api';

jest.mock('./api');
const mockedApi = api as jest.Mocked<typeof api>;

describe('documents service', () => {
  it('getDocuments calls /knowledge/documents', async () => {
    mockedApi.get.mockResolvedValueOnce({ data: [{ id: 1, name: 'doc.pdf', uploaded: '2024-06-01' }] });
    const docs = await getDocuments();
    expect(docs).toEqual([{ id: 1, name: 'doc.pdf', uploaded: '2024-06-01' }]);
    expect(mockedApi.get).toHaveBeenCalledWith('/knowledge/documents');
  });

  it('uploadDocument calls /knowledge/upload', async () => {
    mockedApi.post.mockResolvedValueOnce({ data: { id: 2, name: 'new.pdf', uploaded: '2024-06-02' } });
    const file = new File(['test'], 'new.pdf');
    const doc = await uploadDocument(file);
    expect(doc).toEqual({ id: 2, name: 'new.pdf', uploaded: '2024-06-02' });
    expect(mockedApi.post).toHaveBeenCalled();
  });
}); 