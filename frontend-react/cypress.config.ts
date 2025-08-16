import { defineConfig } from "cypress";

export default defineConfig({
	e2e: {
		baseUrl: "http://localhost:3000",
		video: false,
		screenshotOnRunFailure: true,
		supportFile: false,
		testIsolation: true,
		specPattern: "../tests/e2e/cypress/**/*.cy.{ts,tsx,js,jsx}",
	},
});