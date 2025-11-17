from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from controlers.get_expired_users import get_expired_clients  # Убедись, что путь верный
from controlers.disable_inbound import disable_inbound
from controlers.delete_inbound import delete_inbound
from datetime import datetime, timedelta
from keyboards.inline_keyboards import extend_keyboard
import logging

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


async def check_subscriptions(bot: Bot):
    """Проверка подписок и выполнение действий"""
    logger.info("Checking subscriptions")
    try:
        expired_clients = get_expired_clients()
        logger.info(f"Found {len(expired_clients)} expired clients: {expired_clients}")
        for client in expired_clients:
            if len(client) < 6:
                logger.error(f"Invalid client data: {client}, expected 6 elements")
                continue

            tg_id = client[0]
            username = client[1]
            payment_status = client[2]
            end_date = client[3]
            server_country = client[4]
            disabled_at = client[5]

            logger.info(f"Processing client {tg_id}: username={username}, payment_status={payment_status}, end_date={end_date}, server_country={server_country}, disabled_at={disabled_at}")

            try:
                if not disabled_at:
                    logger.info(f"Subscription expired for user {tg_id}, disabling inbound {username}")
                    disabled_at = disable_inbound(tg_id)
                    text = (
                        f"⚠️ Твой доступ к Зиону истёк ({end_date}). Связь с реальностью отключена.\n"
                        "Продли подписку, чтобы вернуть подключение:"
                    )
                    try:
                        await bot.send_message(tg_id, text, reply_markup=extend_keyboard())
                    except Exception as e:
                        logger.warning(f"Не удалось отправить сообщение пользователю {tg_id}: {str(e)}")

                # Комментируем блок удаления:
                """
                else:
                    try:
                        disabled_at_dt = datetime.strptime(disabled_at, "%Y-%m-%d %H:%M:%S")
                        if (datetime.now() - disabled_at_dt) >= timedelta(minutes=10) and payment_status != "active":
                            logger.info(f"10 minutes passed since disable for user {tg_id}, deleting inbound {username}")
                            delete_inbound(tg_id, username)
                            await bot.send_message(
                                tg_id,
                                "🗑️ Твой доступ к Зиону удалён, так как подписка не была продлена. Выбери красную таблетку снова с помощью /start."
                            )
                    except Exception as e:
                        logger.error(f"Error while parsing disabled_at for user {tg_id}: {str(e)}")
                """
            except Exception as e:
                logger.error(f"Failed to process client {tg_id}: {str(e)}")
                try:
                    await bot.send_message(tg_id, f"❌ Ошибка при обработке твоей подписки: {str(e)}. Свяжитесь с поддержкой.")
                except Exception as send_error:
                    logger.warning(f"Не удалось отправить сообщение об ошибке пользователю {tg_id}: {str(send_error)}")
    except Exception as e:
        logger.error(f"Failed to check subscriptions: {str(e)}")

def setup_scheduler(bot: Bot):
    """Настройка планировщика"""
    scheduler.add_job(
        check_subscriptions,
        trigger=IntervalTrigger(days=5),
        id="check_subscriptions",
        kwargs={"bot": bot}
    )
    scheduler.start()
    logger.info("Scheduler started")

