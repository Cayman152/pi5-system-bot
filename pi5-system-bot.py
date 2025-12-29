import os
import psutil
import platform
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# =========================
# Настройки
# =========================
TOKEN = "xxxxxxxxxxxxxx-xxxxxxxxxxxxxxx-xxxxxxxxxxxxxxx-xxxxxxxxxxxxxxxx"  # твой токен
AUTHORIZED_USER_ID = 1234567890  # твой user_id

# =========================
# Получение температуры CPU
# =========================
def get_cpu_temp():
    try:
        path = "/sys/class/thermal/thermal_zone0/temp"
        if os.path.exists(path):
            with open(path, "r") as f:
                temp = int(f.read().strip()) / 1000.0
                return round(temp, 1)
    except Exception:
        pass
    return None

# =========================
# Получение системной информации
# =========================
def get_system_info():
    cpu = psutil.cpu_percent(interval=1)
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage("/")

    temp = get_cpu_temp()
    temp_str = f"{temp}°C" if temp is not None else "N/A"

    # Определяем ОС
    system = platform.system()
    if system == "Linux":
        try:
            with open("/etc/os-release") as f:
                for line in f:
                    if line.startswith("PRETTY_NAME"):
                        system = line.split("=")[1].strip().strip('"')
                        break
        except Exception:
            pass

    now = datetime.now().strftime("%d.%m.%Y %H:%M")

    info = (
        f"📊 <b>Системная информация</b>\n\n"
        f"🧠 CPU: {cpu}%\n"
        f"💾 RAM: {mem.percent}% ({mem.used // (1024**2)} / {mem.total // (1024**2)} MB)\n"
        f"💽 Диск: {disk.percent}% ({disk.used // (1024**3)} / {disk.total // (1024**3)} GB)\n"
        f"🌡 Температура CPU: {temp_str}\n"
        f"⚙️ ОС: {system}\n\n\n"
        f"{now}"
    )
    return info

# =========================
# Кнопки меню
# =========================
def main_menu():
    buttons = [
        [InlineKeyboardButton("📊 Статус системы", callback_data="status")],
    ]
    return InlineKeyboardMarkup(buttons)

# =========================
# Обработчики
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != AUTHORIZED_USER_ID:
        await update.message.reply_text("⛔ Доступ запрещён.")
        return
    await update.message.reply_text("👋 Привет! Я Pi5 System Bot.", reply_markup=main_menu())

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.from_user.id != AUTHORIZED_USER_ID:
        await query.edit_message_text("⛔ Доступ запрещён.")
        return

    if query.data == "status":
        info = get_system_info()
        await query.edit_message_text(info, parse_mode="HTML", reply_markup=main_menu())

# =========================
# Основной запуск
# =========================
def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    print("✅ Бот запущен.")
    app.run_polling()

if __name__ == "__main__":
    main()
