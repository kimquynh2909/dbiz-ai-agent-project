# Frontend

Vue 3 + Vite frontend for dbiz_ai_agent: chat, AI agents, dashboard, analytics, and permissions.

## Scripts

| Command | Description |
|---------|-------------|
| `yarn dev` | Start Vite dev server |
| `yarn build` | Build for production (output under Frappe assets) |
| `yarn serve` | Preview production build |

## Stack

- **Vue 3** + **Pinia** + **Vue Router**
- **Vite** for build
- **Tailwind CSS**
- **socket.io-client** for real-time chat
- **frappe-ui** for UI components

## Build output

Production build is written for the Frappe app (`/assets/dbiz_ai_agent/frontend/`). The `copy-html-entry` step copies the entry HTML into the app’s www folder.
