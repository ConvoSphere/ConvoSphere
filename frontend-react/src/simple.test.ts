describe("Simple Test", () => {
  test("should work", () => {
    expect(1 + 1).toBe(2);
  });

  test("should handle async", async () => {
    const result = await Promise.resolve(42);
    expect(result).toBe(42);
  });
});
