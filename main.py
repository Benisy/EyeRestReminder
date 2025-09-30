import time
import threading
import os
import sys
import ctypes
import winreg
import random
import json
from playsound import playsound
from pystray import MenuItem as item, Icon, Menu
from PIL import Image
from plyer import notification

# --- НАСТРОЙКИ ---
APP_NAME = "EyeRestReminder"
NOTIFICATION_TITLE = "Отдых для глаз"
NOTIFICATION_MESSAGE = "Посмотри вдаль в течение 20 секунд, чтобы расслабить глаза."
ICON_FILE = "icon.ico"
SOUNDS_DIR = "sounds"
DEFAULT_TOOLTIP = "Напоминание об отдыхе"
WELCOME_NOTIFICATION_TITLE = f"{APP_NAME} запущен!"
WELCOME_NOTIFICATION_MESSAGE = (
    "Приложение работает в фоновом режиме. Я напомню вам об отдыхе."
)
RUN_KEY_PATH = r"Software\Microsoft\Windows\CurrentVersion\Run"
appdata_path = os.getenv("APPDATA") or os.path.expanduser("~")
SETTINGS_DIR = os.path.join(appdata_path, APP_NAME)
SETTINGS_FILE_PATH = os.path.join(SETTINGS_DIR, "settings.json")


# Структура для получения информации о последнем вводе
class LASTINPUTINFO(ctypes.Structure):
    _fields_ = [
        ("cbSize", ctypes.c_uint),
        ("dwTime", ctypes.c_uint),
    ]


def get_idle_duration():
    """Возвращает время бездействия пользователя в секундах."""
    lastInputInfo = LASTINPUTINFO()
    lastInputInfo.cbSize = ctypes.sizeof(lastInputInfo)
    ctypes.windll.user32.GetLastInputInfo(ctypes.byref(lastInputInfo))
    millis = ctypes.windll.kernel32.GetTickCount() - lastInputInfo.dwTime
    return millis / 1000.0


def get_executable_path():
    """Получает путь к исполняемому файлу (.exe или .py)."""
    if getattr(sys, "frozen", False):
        # Если приложение скомпилировано (frozen)
        return sys.executable
    else:
        # Если запускается как скрипт
        return os.path.abspath(sys.argv[0])


def is_autostart_enabled(item):
    """Проверяет, включен ли автозапуск для приложения."""
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY_PATH, 0, winreg.KEY_READ)
        winreg.QueryValueEx(key, APP_NAME)
        winreg.CloseKey(key)
        return True
    except FileNotFoundError:
        return False


def add_to_autostart():
    """Добавляет приложение в автозапуск."""
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER, RUN_KEY_PATH, 0, winreg.KEY_WRITE
        )
        path = get_executable_path()
        # Создаем запись в реестре. Для .py файлов будет запускаться python, для .exe - сам файл.
        if path.endswith(".py"):
            # Для запуска скрипта нужен интерпретатор
            python_exe = sys.executable.replace(
                "python.exe", "pythonw.exe"
            )  # Используем pythonw для запуска без консоли
            winreg.SetValueEx(
                key, APP_NAME, 0, winreg.REG_SZ, f'"{python_exe}" "{path}"'
            )
        else:
            winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, f'"{path}"')
        winreg.CloseKey(key)
        print(f"{APP_NAME} добавлен в автозапуск.")
    except Exception as e:
        print(f"Ошибка при добавлении в автозапуск: {e}")


def remove_from_autostart():
    """Удаляет приложение из автозапуска."""
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER, RUN_KEY_PATH, 0, winreg.KEY_WRITE
        )
        winreg.DeleteValue(key, APP_NAME)
        winreg.CloseKey(key)
        print(f"{APP_NAME} удален из автозапуска.")
    except FileNotFoundError:
        print(f"Приложение не было в автозапуске.")
    except Exception as e:
        print(f"Ошибка при удалении из автозапуска: {e}")


# ОСНОВНАЯ ЛОГИКА ПРИЛОЖЕНИЯ
class EyeRestApp:
    def __init__(self, icon):
        self.icon = icon
        self.work_interval = 20 * 60
        self.idle_threshold = 5 * 60
        self.load_settings()
        self.last_activity_time = time.time()
        self.running = True
        self.send_welcome_notification()

    def load_settings(self):
        """Загружает настройки из JSON-файла."""
        try:
            if os.path.exists(SETTINGS_FILE_PATH):
                with open(SETTINGS_FILE_PATH, "r", encoding="utf-8") as f:
                    settings = json.load(f)
                    self.work_interval = settings.get(
                        "work_interval_sec", self.work_interval
                    )
                    self.idle_threshold = settings.get(
                        "idle_threshold_sec", self.idle_threshold
                    )
                    print(f"Настройки успешно загружены из {SETTINGS_FILE_PATH}")
        except (json.JSONDecodeError, IOError) as e:
            print(
                f"Ошибка загрузки настроек: {e}. Будут использованы значения по умолчанию."
            )

    def save_settings(self):
        """Сохраняет текущие настройки в JSON-файл."""
        try:
            # Убедимся, что директория для настроек существует
            os.makedirs(SETTINGS_DIR, exist_ok=True)
            settings = {
                "work_interval_sec": self.work_interval,
                "idle_threshold_sec": self.idle_threshold,
            }
            with open(SETTINGS_FILE_PATH, "w", encoding="utf-8") as f:
                json.dump(settings, f, indent=4)
            print(f"Настройки сохранены в {SETTINGS_FILE_PATH}")
        except IOError as e:
            print(f"Ошибка сохранения настроек: {e}")

    def set_work_interval(self, minutes):
        print(f"Новый интервал работы: {minutes} минут.")
        self.work_interval = minutes * 60
        self.last_activity_time = time.time()
        self.save_settings()

    def set_idle_threshold(self, minutes):
        print(f"Новый порог бездействия: {minutes} минут.")
        self.idle_threshold = minutes * 60
        self.save_settings()

    def send_welcome_notification(self):
        """Отправляет приветственное уведомление при запуске."""
        time.sleep(2)
        print("Отправка приветственного уведомления...")
        try:
            minutes = self.work_interval // 60
            message = (
                f"Приложение работает. Я напомню вам об отдыхе через {minutes} минут."
            )
            notification.notify(  # type: ignore
                title=WELCOME_NOTIFICATION_TITLE,
                message=message,
                app_name=APP_NAME,
                app_icon=resource_path(ICON_FILE),
                timeout=10,
            )
        except Exception as e:
            print(f"Не удалось отправить приветственное уведомление: {e}")

    def play_random_sound(self):
        """Находит и воспроизводит случайный .mp3 файл из папки sounds."""
        try:
            sounds_path = resource_path(SOUNDS_DIR)
            if not os.path.isdir(sounds_path):
                print(f"Папка для звуков не найдена: {sounds_path}")
                return

            # Ищем файлы .mp3
            sound_files = [f for f in os.listdir(sounds_path) if f.endswith(".mp3")]
            if not sound_files:
                print(f"В папке {SOUNDS_DIR} нет .mp3 файлов.")
                return

            random_sound = random.choice(sound_files)
            full_sound_path = os.path.join(sounds_path, random_sound)
            print(f"Воспроизведение звука: {random_sound}")

            # playsound по умолчанию блокирует поток. Чтобы этого избежать, запускаем его в отдельном потоке
            sound_thread = threading.Thread(
                target=playsound, args=(full_sound_path,), daemon=True
            )
            sound_thread.start()

        except Exception as e:
            print(f"Ошибка при воспроизведении звука: {e}")

    def send_notification(self):
        """Отправляет уведомление пользователю."""
        print("Отправка уведомления...")

        notification.notify(  # type: ignore
            title=NOTIFICATION_TITLE,
            message=NOTIFICATION_MESSAGE,
            app_name=APP_NAME,
            app_icon=resource_path(ICON_FILE),
            timeout=10,
        )

        # Пауза перед воспроизведением звука
        time.sleep(1)

        self.play_random_sound()

    def _format_time(self, seconds):
        """Форматирует секунды в строку ММ:СС."""
        minutes, seconds = divmod(int(seconds), 60)
        return f"{minutes:02d}:{seconds:02d}"

    def main_loop(self):
        """Главный цикл, который отслеживает активность и таймер."""
        while self.running:
            idle_seconds = get_idle_duration()

            if idle_seconds < self.idle_threshold:
                # Пользователь активен
                current_time = time.time()
                elapsed_active_time = current_time - self.last_activity_time

                # Обновляем тултип с оставшимся временем
                remaining_time = self.work_interval - elapsed_active_time
                formatted_time = self._format_time(remaining_time)
                new_tooltip = f"{DEFAULT_TOOLTIP}\nДо отдыха: {formatted_time}"

                if elapsed_active_time >= self.work_interval:
                    self.send_notification()
                    self.last_activity_time = time.time()
            else:
                # Пользователь неактивен, сбрасываем таймер и флаг уведомления
                self.last_activity_time = time.time()
                new_tooltip = f"{DEFAULT_TOOLTIP}\nЗаснул..."

            # Обновляем заголовок иконки, если она уже создана
            # Это предотвращает ошибку во время инициализации
            if self.icon and self.icon.title != new_tooltip:
                self.icon.title = new_tooltip

            # Пауза, чтобы не нагружать процессор
            time.sleep(5)

    def stop(self):
        """Останавливает основной цикл и приложение."""
        self.running = False
        # Даем потоку секунду на завершение перед закрытием иконки
        time.sleep(1)
        if self.icon:
            self.icon.stop()


# ФУНКЦИИ ДЛЯ ИКОНКИ В ТРЕЕ
def resource_path(relative_path):
    """Получаем абсолютный путь к ресурсу, работает и для скрипта, и для .exe"""
    base_path = getattr(sys, "_MEIPASS", os.path.abspath("."))
    return os.path.join(base_path, relative_path)


def setup_tray(app_instance):
    """Настраивает и запускает иконку в системном трее."""

    WORK_OPTIONS = [10, 15, 20, 25, 30, 45, 60]
    IDLE_OPTIONS = [2, 5, 7, 10, 15]

    def create_work_interval_callback(minutes):
        """Создает и возвращает функцию-обработчик для интервала работы."""

        def callback(icon, item):
            app_instance.set_work_interval(minutes)

        return callback

    def create_idle_threshold_callback(minutes):
        """Создает и возвращает функцию-обработчик для порога бездействия."""

        def callback(icon, item):
            app_instance.set_idle_threshold(minutes)

        return callback

    def on_toggle_autostart(icon, item):
        if not item.checked:
            add_to_autostart()
        else:
            remove_from_autostart()

    def on_exit(icon, item):
        app_instance.stop()

    work_submenu = [
        item(
            f"{m} минут",
            create_work_interval_callback(m),
            checked=lambda item, v=m: app_instance.work_interval == v * 60,
            radio=True,
        )
        for m in WORK_OPTIONS
    ]

    idle_submenu = [
        item(
            f"{m} минут",
            create_idle_threshold_callback(m),
            checked=lambda item, v=m: app_instance.idle_threshold == v * 60,
            radio=True,
        )
        for m in IDLE_OPTIONS
    ]

    image = Image.open(resource_path(ICON_FILE))

    menu = Menu(
        item("Интервал работы", Menu(*work_submenu)),
        item("Порог бездействия", Menu(*idle_submenu)),
        Menu.SEPARATOR,
        item("Автозапуск", on_toggle_autostart, checked=is_autostart_enabled),
        item("Выход", on_exit),
    )

    icon = Icon(APP_NAME, image, "Напоминание об отдыхе", menu)
    app_instance.icon = icon
    icon.run()


if __name__ == "__main__":
    # Создаем экземпляр приложения
    app = EyeRestApp(
        None
    )  # Временно передаем None, иконка будет установлена в setup_tray

    # Запускаем основной цикл в отдельном потоке
    logic_thread = threading.Thread(target=app.main_loop, daemon=True)
    logic_thread.start()

    # Запускаем иконку в трее (это блокирующая операция, она будет выполняться до выхода)
    setup_tray(app)
