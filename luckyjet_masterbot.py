import os
import json
import random
from statistics import mean
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes
)

TOKEN = os.getenv("TOKEN") or "ВСТАВЬ_СЮДА_ТОКЕН"
CHANNEL_ID = os.getenv("CHANNEL_ID")

data_file = "data.json"
current_risk = "medium"
risk_levels = {"low": 1.3, "medium": 1.5, "high": 1.7}
history_cache = []

# Загрузка истории
def load_data():
    if not os.path.exists(data_file):
        return {"history": []}
    with open(data_file, "r") as f:
        return json.load(f)

# Сохранение истории
def save_data(data):
    with open(data_file, "w") as f:
        json.dump(data, f)

# AI-квантовый прогноз
def quantum_predict():
    recent = history_cache[-10:] if len(history_cache) >= 10 else history_cache
    avg = mean(recent) if recent else 1.5
    noise = random.uniform(-0.1, 0.2)
    next_crash = round(avg + noise, 2)
    return max(1.01, min(next_crash, 20.0))

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎰 Привет! Я LuckyJet Quantum Bot!\nНапиши /signal чтобы получить предсказание.")

# /signal
async def signal_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    crash = quantum_predict()
    threshold = risk_levels.get(current_risk, 1.5)
    signal = "✅ ВХОДИ!" if crash >= threshold else "❌ Пропусти"

    history_cache.append(crash)
    if len(history_cache) > 100:
        history_cache.pop(0)

    await update.message.reply_text(
        f"📡 Предсказание: {crash}x\n🎯 Риск: {current_risk.upper()}\n📢 Сигнал: {signal}"
    )

    data = load_data()
    data["history"].append({"crash": crash, "signal": signal})
    save_data(data)

    if CHANNEL_ID:
        await context.bot.send_message(
            chat_id=CHANNEL_ID,
            text=f"📡 Предсказание: {crash}x\n🎯 Риск: {current_risk.upper()}\n📢 Сигнал: {signal}"
        )

# /risk
async def set_risk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global current_risk
    if context.args and context.args[0].lower() in risk_levels:
        current_risk = context.args[0].lower()
        await update.message.reply_text(f"✅ Уровень риска установлен на: {current_risk.upper()}")
    else:
        await update.message.reply_text("Используй: /risk low | medium | high")

# Запуск
async def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("signal", signal_command))
    app.add_handler(CommandHandler("risk", set_risk))
    await app.initialize()
    await app.start()
    await app.updater.start_polling()  # Можно оставить, если используется polling
    await app.updater.idle()

# Для Python 3.7+
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
