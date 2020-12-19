import config
import logging
import asyncio
from aiogram import Bot, Dispatcher, executor, types
from PostgresqlHandler import PostgresqlHandler

from Kufar import Kufar

logging.basicConfig(level=logging.INFO)
bot = Bot(token=config.API_TOKEN)
dp = Dispatcher(bot)
db = PostgresqlHandler()
kf = Kufar('lastkey.txt')

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer("Добро пожаловать к боту поисковику:) \n Для подписки на рассылку введите команду " +
        "\n/subscribe \nДля отписки от рассылки\n /unsubscribe\nНадеюсь вы найдете то, что ищете:)")

@dp.message_handler(commands=['subscribe'])
async def subscribe(message: types.Message):
    if(not db.subscriber_exists(message.from_user.id)):
        db.add_subscriber(message.from_user.id)
    else:
        db.update_subscription(message.from_user.id, True)
    
    await send_all_ads(message.from_user.id)
    await message.answer("Вы успешно подписались на рассылку!\nПри появлении новых объявлений вам придет уведомление.")

@dp.message_handler(commands=['unsubscribe'])
async def unsubscribe(message: types.Message):
    if(not db.subscriber_exists(message.from_user.id)):
        db.add_subscriber(message.from_user.id, False)
        await message.answer("Вы итак не подписаны.")
    else:
        db.update_subscription(message.from_user.id, False)
        await message.answer("Вы успешно отписаны от рассылки.")

async def scheduled(wait_for):
    while True:
        await asyncio.sleep(wait_for)
        new_ads = kf.get_new_ads()

        if(new_ads):
            new_ads.reverse()
            for na in new_ads:
                info = kf.get_ad_info(na)
                subscribers = db.get_subscribers()
                for s in subscribers:
                    await bot.send_photo(
                        s[1],
                        photo= info['image'],
                        caption = info['title'] + "\n" + "Размер: " + info['size'] + "\n" + info['cost'] + "\n" + info['district'] + "\n\n" + na,
                        disable_notification = False
                    )
                kf.update_lastkey(info['id'])

async def send_all_ads(user_id):
    ads = kf.get_all_ads()
    if(ads):
        ads.reverse()
        for a in ads:
            info = kf.get_ad_info(a)
            await bot.send_photo(
                user_id,
                photo= info['image'],
                caption = info['title'] + "\n" + "Размер: " + info['size'] + "\n" + info['cost'] + "\n" + info['district'] + "\n\n" + a,
                disable_notification = False
            )

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(scheduled(600))
    executor.start_polling(dp, skip_updates=True, loop=loop)