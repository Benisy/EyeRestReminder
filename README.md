# EyeRestReminder

A Windows application that reminds you to take breaks to rest your eyes. Forget about strain and fatigue—EyeRestReminder tracks your activity and tactfully (or not so tactfully) tells you when it's time to take a break.

The application runs in the background, doesn't interfere with your work, and has flexible settings accessible right from the tray icon.

## ⚙️ Key Features

*   ✅ **Timer**: Tracks only your active computer usage time.
*   ✅ **Flexible Settings**: Work interval and idle threshold are easily configurable through the tray menu.
*   ✅ **Settings Persistence**: Your preferences are saved between restarts.
*   ✅ **Windows Autostart**: Enable or disable autostart with a single click.
*   ✅ **Fun Audio Notifications**: Plays random audio clips from the `sounds` folder. Add your own!
*   ✅ **Unobtrusive**: Runs in the system tray, displaying the remaining time until your next break in a tooltip.

## 🚀 Installation

This project uses the [UV](https://github.com/astral-sh/uv) package manager for installation and running.

### 1. Preparation

*   Ensure you have **Python 3.8+** installed.
*   Install **UV**:
    ```shell
    # Windows (Powershell)
    irm https://astral.sh/uv/install.ps1 | iex
    ```
*   Clone the repository:
    ```shell
    git clone https://github.com/Benisy/EyeRestReminder.git
    cd your-repository
    ```

### 2. Create environment and install dependencies

1.  **Create a virtual environment:**
    ```shell
    uv venv
    ```

2.  **Create a `requirements.txt` file** with the following content:
    ```txt
    pystray
    Pillow
    plyer
    playsound==1.2.2
    ```
    > **Important**: `playsound` version `1.3.0` can cause issues on Windows. It is recommended to use version `1.2.2`.

3.  **Install the dependencies:**
    ```shell
    uv pip install -r requirements.txt
    ```

### 3. Prepare Resources

1.  Place the application icon `icon.ico` in the root folder of the project.
2.  Create a `sounds` folder in the project root.
3.  Place your `.mp3` sound files into the `sounds` folder.

## ▶️ Usage

To run the application, use `uv run`.

*   **Run with a console window (for debugging):**
    ```shell
    uv run python main.py
    ```
*   **Run in the background (without a console):**
    ```shell
    uv run pythonw main.py
    ```
    The application will appear in the system tray. Right-click the icon to access the settings.

## 🔧 Customization

### Audio Notifications

The fun part! You can fully customize the sounds.
Just record your own phrases (funny, sarcastic, harsh in the style of GLaDOS—anything goes!) and place the `.mp3` files in the `sounds` folder. The application will randomly select one for each notification.

### Basic Settings

Some basic parameters, such as `APP_NAME` or notification texts, can be changed at the top of the `main.py` file.

## 📦 Building into an .exe file

You can compile the script into a single executable `.exe` file using **PyInstaller**.

1.  **Install PyInstaller:**
    ```shell
    uv pip install pyinstaller
    ```

2.  **Run the build:**
    Run the command below from the project's root folder. It will bundle all the necessary resources into a single file.

    ```shell
    pyinstaller --onefile --windowed --hidden-import plyer.platforms.win.notification --icon="icon.ico" --add-data "icon.ico;." --add-data "sounds;sounds" --name EyeRestReminder main.py
    ```
    **Command Breakdown:**
    *   `--onefile`: Creates a single `.exe` file.
    *   `--windowed`: Runs the application without a console window.
    *   `--icon="icon.ico"`: Sets the icon for the `.exe` file.
    *   `--add-data="sounds;sounds"`: Includes the `sounds` folder in the build.
    *   `--add-data="icon.ico;."`: Includes the icon file for use in notifications.
    *   `--name`: The name for the application.

3.  The finished `.exe` file will be located in the `dist` folder.


## 📄 License

This project is dual-licensed for its code and media assets.

### Code

**The code** for this project (`main.py` and related scripts) is distributed under the **MIT License**. You are free to use, modify, and distribute it in accordance with the terms set forth in the [LICENSE](LICENSE) file.

### Audio Assets

**The audio assets** in the `sounds` folder were created using the [ElevenLabs](https://elevenlabs.io/) service and are governed by their **Terms of Service**. The distribution and use of these files must comply with the ElevenLabs policy applicable to the subscription plan on which they were generated.

---