import { getTools, runTool } from "./tools";
import api from "./api";

jest.mock("./api");

const mockedApi = api as jest.Mocked<typeof api>;

describe("tools service", () => {
  it("getTools calls /tools", async () => {
    mockedApi.get.mockResolvedValueOnce({
      data: [{ id: 1, name: "Test", description: "desc" }],
    });
    const tools = await getTools();
    expect(tools).toEqual([{ id: 1, name: "Test", description: "desc" }]);
    expect(mockedApi.get).toHaveBeenCalledWith("/tools");
  });

  it("runTool calls /tools/:id/run", async () => {
    mockedApi.post.mockResolvedValueOnce({ data: { output: "ok" } });
    const result = await runTool(1, { param: "foo" });
    expect(result).toEqual({ output: "ok" });
    expect(mockedApi.post).toHaveBeenCalledWith("/tools/1/run", {
      param: "foo",
    });
  });
});
