## Getting Started (Local Development)

This guide shows how to run the app locally on Windows using WSL2 and Frappe Bench.

---

### 1. Prerequisites

- **Windows + WSL2**
  - Windows 10 / 11 with WSL2 and Ubuntu installed  
  - Check from PowerShell:

    ```powershell
    wsl --status
    wsl -l -v
    ```

- **Docker Desktop**
  - Docker Engine + Docker Compose

    ```powershell
    docker version
    docker compose version
    ```

- **Inside Ubuntu (WSL)**
  - Ubuntu 24.04 (or similar)
  - Frappe Bench, Python, Node, Redis, MariaDB, Git

    ```bash
    lsb_release -a

    bench --version
    python3 --version
    pip3 --version
    node -v
    npm -v
    redis-server --version
    mariadb --version
    git --version
    ```

---

### 2. Start Qdrant and Socket Server (Docker)

From **PowerShell / Windows terminal**:

```powershell
cd \path\to\socket_server
docker compose up -d
```

- **Qdrant** should now be available at `http://localhost:6333/dashboard`.

---

### 3. Install App into Frappe Bench (WSL / Ubuntu)

1. **Enter WSL and activate bench environment**

   ```bash
   wsl
   cd ~/frappe-bench
   source env/bin/activate
   # (important so you use ~/frappe-bench/env/bin/bench)
   ```

2. **Get the app into your bench**

   ```bash
   bench get-app dbiz_ai_agent /mnt/c/path/to/dbiz-ai-agent/in/linux
   ```

3. **Create the site**

   - New site:

     ```bash
     bench new-site ai-assistant.local
     ```

   - If site is new:

     ```bash
     bench --site ai-assistant.local install-app dbiz_ai_agent
     ```

---

### 4. Start Bench and Frontend Dev Server

1. **Start Frappe bench (backend + core frontend)**

   ```bash
   # Terminal 1 (WSL)
   cd ~/frappe-bench
   source env/bin/activate
   bench start
   ```

   - Leave this terminal running.
   - Frappe will typically be at `http://localhost:8000`.

2. **Start the Vue frontend in dev mode**

   ```bash
   # Terminal 2 (WSL)
   cd ~/frappe-bench/apps/dbiz_ai_agent/frontend
   npm install
   npm run dev
   ```

   - Dev frontend is served at: `http://localhost:8080/ai-agent/`
   - For production build (served as static assets by Frappe):

     ```bash
     npm run build
     # outputs to: dbiz_ai_agent/public/
     ```

4. **Configure socket server URL in the site**

   ```bash
   cd ~/frappe-bench
   bench --site ai-assistant.local set-config socketio_server_url "http://localhost:5179"
   bench --site ai-assistant.local clear-cache
   ```

---

### 5. Accessing the App

- **Frappe site**: open your browser to  
  `http://ai-assistant.local:8000` (or `http://localhost:8000` depending on your hosts/DNS setup).
- **Vue dev frontend**: `http://localhost:8080/ai-agent/`
- **Qdrant**: `http://localhost:6333/dashboard/`
- **Socket server (dev, if not using Docker)**: `http://localhost:5179`