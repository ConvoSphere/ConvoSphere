import { getAssistants, addAssistant, deleteAssistant } from './assistants';
import api from './api';

jest.mock('./api');
const mockedApi = api as jest.Mocked<typeof api>;

describe('assistants service', () => {
  it('getAssistants calls /assistants', async () => {
    mockedApi.get.mockResolvedValueOnce({ data: [{ id: 1, name: 'A', description: 'desc' }] });
    const assistants = await getAssistants();
    expect(assistants).toEqual([{ id: 1, name: 'A', description: 'desc' }]);
    expect(mockedApi.get).toHaveBeenCalledWith('/assistants');
  });

  it('addAssistant calls /assistants', async () => {
    mockedApi.post.mockResolvedValueOnce({ data: { id: 2, name: 'B', description: 'desc2' } });
    const assistant = await addAssistant({ name: 'B', description: 'desc2' });
    expect(assistant).toEqual({ id: 2, name: 'B', description: 'desc2' });
    expect(mockedApi.post).toHaveBeenCalledWith('/assistants', { name: 'B', description: 'desc2' });
  });

  it('deleteAssistant calls /assistants/:id', async () => {
    mockedApi.delete.mockResolvedValueOnce({});
    await deleteAssistant(1);
    expect(mockedApi.delete).toHaveBeenCalledWith('/assistants/1');
  });
}); 