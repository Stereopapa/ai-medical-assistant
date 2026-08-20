### Pycharm setup

#### Prerequisite

- Pycharm Pro version 2025.3.3+
- Docker Desktop
- git

**Updating PyCharm** — the easiest way is through JetBrains Toolbox

**Free Pro** — if you are a student, you can get a free Pro licence at https://www.jetbrains.com/shop/eform/students.
After registration, activate it in PyCharm via Help → Register.

#### Steps

##### WSL2 Ubuntu Setup

1. Install Ubuntu in WSL2 (run in PowerShell as Admin):
   > `wsl --install -d Ubuntu`

   If WSL2 did not open automatically after installation, run:
   > `wsl -d Ubuntu`

2. Configure PyCharm to use Docker via WSL2:
    - Go to **Settings → Build, Execution, Deployment → Docker**
    - Select **WSL** and choose **Ubuntu** from the dropdown
    - Verify **Connection successful** is shown
    - Click **OK**

##### SSH Key Setup (WSL2)

1. Generate SSH key:
   > `ssh-keygen -t ed25519 -C "your_github_username-desktop-wsl2"`

   Press Enter for all prompts to use default location (`~/.ssh/id_ed25519`).

2. Configure SSH agent to start automatically — open `~/.bashrc` with nano:
   > `nano ~/.bashrc`

   Scroll to the bottom and add:

```bash
    # Start SSH agent and add key automatically
    eval "$(ssh-agent -s)"
    ssh-add ~/.ssh/id_ed25519
```

    Save with `Ctrl+O` → Enter, exit with `Ctrl+X`. Then reload:
    > `source ~/.bashrc`

3. Add public key to GitHub:
   > `cat ~/.ssh/id_ed25519.pub`

   Copy the output, then go to:
   **GitHub → Settings → SSH and GPG keys → New SSH key** → paste and save.

4. Verify:
   > `ssh -T git@github.com`

   Expected output: `Hi <username>! You've successfully authenticated`

##### Clone and build and setup dev container

**Note:** `setup-env` script is only required for VS Code setup. PyCharm configures the environment automatically.

1. Clone the repository in WSL2:
   > `git clone git@github.com:Stereopapa/ai-medical-assistant.git`

   > `cd ai-medical-assistant`

   > `git checkout dev`

2. Set up DB credentials (Optional): If you want to use custom database credentials instead of the defaults from
   `.env.example`, run the following script and fill in your preferred username and password:
   > `./.devcontainer/set-db-creds.sh`

3. On the PyCharm Welcome screen go to **Remote Development → Dev Containers → New Dev Container**, then:
    - Select **From Local Project**
    - Click **...** and navigate to `\\wsl.localhost\Ubuntu\home\<your_username>\<picked-path>`
    - Click **Build Container And Continue**
    - If you encounter an IDE Backend error during setup, click **Restart** to retry

4. After the build completes, click **Trust Project** — PyCharm will open the project.

5. If PyCharm did not detect the interpreter automatically (**No Interpreter** shown in the bottom right corner):
    - Click **No Interpreter → Add New Interpreter → Add Local Interpreter**
    - Configure as follows:
        - Environment: **Select existing**
        - Type: **uv**
        - Path to uv: `/usr/bin/uv`
        - Environment: `/workspaces/secure2fa-api/.venv/bin/python`
    - Click **OK**

6. You can also set up automatic read of `.env` file for Run Current File Option

- In the top-right corner of PyCharm (next to the green **Run/Play** button), expand the run configurations dropdown
  menu and click **Edit Configurations...**.
- In the bottom-left corner of the opened window, click the **Edit configuration templates...** link.
- From the list of templates on the left side, select **Python**.
- On the right side, find the **Environment variables** field and click the **Folder icon** at the end of the input box.
- In the new window that appears, look at the bottom section for the **Load env file** option (or click the `+` icon /
  browse button next to the env file section).
- Write path to `.env` file from your project directory.
- Click **OK**, then click **Apply** to save the changes.

#### PyCharm Plugin Configuration

##### Ruff

1. Go to **Settings → Python → Tools → Ruff**
    - Check **Enable**
    - Set **Execution mode** to **Path**
    - Set **Executable** to `/workspaces/ai-medical-assistant/.venv/bin/ruff`
    - Click **Apply**
2. Go to **Tools → Actions on Save**
    - Check **Reformat code**
    - Click **OK**

##### Mypy

1. Go to **Settings → Tools → Mypy**
    - Select **Mypy executable**
    - Set path to `/workspaces/ai-medical-assistant/.venv/bin/mypy`
    - Set **Config file** to `/workspaces/ai-medical-assistant/pyproject.toml`
    - Click **Apply → OK**

#### Test Configuration

- `python --version` — expected: `Python 3.12.x`
- `uv --version` — expected: `uv 0.10.x`
- `uv run uvicorn app.main:app --host 0.0.0.0 --port 8000` — open `http://localhost:8000/docs` in your browser