# Frontend Testing Strategy

We apply a **pyramidal** testing approach: unit → integration → E2E.

---

## 1. Tooling

| Level | Framework | Command |
|-------|-----------|---------|
| Unit / Integration | **Jest** + **React Testing Library** | `pnpm test` |
| Component Docs | **Storybook** (optional) | `pnpm storybook` |
| End-to-End | **Cypress** | `pnpm cypress open` |

### Setup

```
pnpm add -D jest @testing-library/react @testing-library/jest-dom cypress
```

`vitest` could replace Jest later (tracked in backlog).

## 2. Folder Convention

```
src/
├── components/Button.test.tsx   # Unit
├── features/chat/ChatPage.test.tsx  # Integration
cypress/
└── e2e/chat.cy.ts               # E2E
```

## 3. Jest Config Highlights

```js title="jest.config.js"
module.exports = {
  setupFilesAfterEnv: ['<rootDir>/src/setupTests.ts'],
  testEnvironment: 'jsdom',
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/src/$1',
  },
};
```

`setupTests.ts` registers `@testing-library/jest-dom` matchers.

## 4. RTL Best Practices

* Query by _role_ or _text_ first (`screen.getByRole('button', { name: /senden/i })`).
* Use `userEvent` for realistic interactions.
* Prefer `findBy*` queries for async UI.

## 5. Cypress

* Base URL set via `cypress.config.ts` to `http://localhost:5173`.
* JWT tokens are requested via API; use custom command `cy.login()` to seed session.

```ts title="cypress/support/commands.ts"
Cypress.Commands.add('login', () => {
  cy.request('POST', '/auth/login', { email: 'test@cs.io', password: '123456' }).then(({ body }) => {
    window.localStorage.setItem('convosphere.jwt.access', body.access);
    window.localStorage.setItem('convosphere.jwt.refresh', body.refresh);
  });
});
```

## 6. CI Integration

GitHub Actions workflow runs:

```yaml
- name: Install deps
  run: pnpm install --frozen-lockfile
- name: Lint
  run: pnpm lint
- name: Test
  run: pnpm test -- --coverage
- name: Cypress
  uses: cypress-io/github-action@v6
  with:
    start: pnpm dev
    wait-on: 'http://localhost:5173'
```

Coverage reports are uploaded via `codecov`.

---
This testing stack safeguards quality while enabling fast iteration.
