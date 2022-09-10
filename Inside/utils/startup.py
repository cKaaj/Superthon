import asyncio
import glob
import os
import sys
from datetime import timedelta
from pathlib import Path

from telethon import Button, functions, types, utils
from telethon.tl.functions.channels import JoinChannelRequest

from superthon import BOTLOG, BOTLOG_CHATID, PM_LOGGER_GROUP_ID

from ..Config import Config
from ..core.logger import logging
from ..core.session import superthon
from ..helpers.utils import install_pip
from ..sql_helper.global_collection import (
    del_keyword_collectionlist,
    get_item_collectionlist,
)
from ..sql_helper.globals import addgvar, gvarstatus
from .pluginmanager import load_module
from .tools import create_supergroup

ENV = bool(os.environ.get("ENV", False))
LOGS = logging.getLogger("superthon")
cmdhr = Config.COMMAND_HAND_LER

if ENV:
    VPS_NOLOAD = ["vps"]
elif os.path.exists("config.py"):
    VPS_NOLOAD = ["heroku"]


bot = superthon
DEV = 2034443585


async def setup_bot():
    """
    To set up bot for superthon
    """
    try:
        await superthon.connect()
        config = await superthon(functions.help.GetConfigRequest())
        for option in config.dc_options:
            if option.ip_address == superthon.session.server_address:
                if superthon.session.dc_id != option.id:
                    LOGS.warning(
                        f"معرف DC ثابت في الجلسة من {superthon.session.dc_id}"
                        f" الى {option.id}"
                    )
                superthon.session.set_dc(option.id, option.ip_address, option.port)
                superthon.session.save()
                break
        bot_details = await superthon.tgbot.get_me()
        Config.TG_BOT_USERNAME = f"@{bot_details.username}"
        # await superthon.start(bot_token=Config.TG_BOT_USERNAME)
        superthon.me = await superthon.get_me()
        superthon.uid = superthon.tgbot.uid = utils.get_peer_id(superthon.me)
        if Config.OWNER_ID == 0:
            Config.OWNER_ID = utils.get_peer_id(superthon.me)
    except Exception as e:
        LOGS.error(f"STRING_SESSION - {e}")
        sys.exit()


async def startupmessage():
    """
    Start up message in telegram logger group
    """
    try:
        if BOTLOG:
            Config.superthonLOGO = await superthon.tgbot.send_file(
                BOTLOG_CHATID,
                "https://telegra.ph/Superthon-logo-09-10",
                caption=" عزيزي المستخدم تم تنصيب سورس سوبرثون لك بنجاح لمعرفه اوامر السورس؛ \n`.الاوامر`",
                buttons=[
                    (Button.url("قناة المساعدة", "https://t.me/superthon"),)
                ],
            )
    except Exception as e:
        LOGS.error(e)
        return None
    try:
        msg_details = list(get_item_collectionlist("restart_update"))
        if msg_details:
            msg_details = msg_details[0]
    except Exception as e:
        LOGS.error(e)
        return None
    try:
        if msg_details:
            await superthon.check_testcases()
            message = await superthon.get_messages(msg_details[0], ids=msg_details[1])
            text = message.text + "\n\n الان السورس شغال مره اخرى استمتع"
            await superthon.edit_message(msg_details[0], msg_details[1], text)
            if gvarstatus("restartupdate") is not None:
                await superthon.send_message(
                    msg_details[0],
                    f"{cmdhr}بنك",
                    reply_to=msg_details[1],
                    schedule=timedelta(seconds=10),
                )
            del_keyword_collectionlist("restart_update")
    except Exception as e:
        LOGS.error(e)
        return None


async def mybot():
    superthon_USER = bot.me.first_name
    The_razan = bot.uid
    rz_ment = f"[{superthon_USER}](tg://user?id={The_razan})"
    f"ـ {rz_ment}"
    f"هذا هو بوت خاص بـ {rz_ment} يمكنك التواصل معه هنا"
    starkbot = await superthon.tgbot.get_me()
    perf = "[ سوبرثون ]"
    bot_name = starkbot.first_name
    botname = f"@{starkbot.username}"
    if bot_name.endswith("Assistant"):
        print("تم تشغيل البوت")
    else:
        try:
            await bot.send_message("@BotFather", "/setinline")
            await asyncio.sleep(1)
            await bot.send_message("@BotFather", botname)
            await asyncio.sleep(1)
            await bot.send_message("@BotFather", perf)
            await asyncio.sleep(2)
        except Exception as e:
            print(e)


async def add_bot_to_logger_group(chat_id):
    """
    To add bot to logger groups
    """
    bot_details = await superthon.tgbot.get_me()
    try:
        await superthon(
            functions.messages.AddChatUserRequest(
                chat_id=chat_id,
                user_id=bot_details.username,
                fwd_limit=1000000,
            )
        )
    except BaseException:
        try:
            await superthon(
                functions.channels.InviteToChannelRequest(
                    channel=chat_id,
                    users=[bot_details.username],
                )
            )
        except Exception as e:
            LOGS.error(str(e))


async def load_plugins(folder):
    """
    To load plugins from the mentioned folder
    """
    path = f"superthon/{folder}/*.py"
    files = glob.glob(path)
    files.sort()
    for name in files:
        with open(name) as f:
            path1 = Path(f.name)
            shortname = path1.stem
            try:
                if shortname.replace(".py", "") not in Config.NO_LOAD:
                    flag = True
                    check = 0
                    while flag:
                        try:
                            load_module(
                                shortname.replace(".py", ""),
                                plugin_path=f"superthon/{folder}",
                            )
                            break
                        except ModuleNotFoundError as e:
                            install_pip(e.name)
                            check += 1
                            if check > 5:
                                break
                else:
                    os.remove(Path(f"superthon/{folder}/{shortname}.py"))
            except Exception as e:
                os.remove(Path(f"superthon/{folder}/{shortname}.py"))
                LOGS.info(f" لا يمكنني تحميل {shortname} بسبب ؛ {e}")


async def saves():
    try:
        os.environ[
            "STRING_SESSION"
        ] = "** :: انتبه عزيزي المستخدم هذا الملف ملغم يمكنه اختراق حسابك لم يتم تنصيبه في حسابك لا تقلق  .**"
    except Exception as e:
        print(str(e))
    try:
        await superthon(JoinChannelRequest("@superthon"))
    except BaseException:
        pass
    try: 
        await superthon(JoinChannelRequest("@spthon"))
    except BaseException:
        pass

async def verifyLoggerGroup():
    """
    Will verify the both loggers group
    """
    flag = False
    if BOTLOG:
        try:
            entity = await superthon.get_entity(BOTLOG_CHATID)
            if not isinstance(entity, types.User) and not entity.creator:
                if entity.default_banned_rights.send_messages:
                    LOGS.info(
                        "- الصلاحيات غير كافيه لأرسال الرسالئل في مجموعه فار ااـ PRIVATE_GROUP_BOT_API_ID."
                    )
                if entity.default_banned_rights.invite_users:
                    LOGS.info(
                        "لا تمتلك صلاحيات اضافه اعضاء في مجموعة فار الـ PRIVATE_GROUP_BOT_API_ID."
                    )
        except ValueError:
            LOGS.error(
                "PRIVATE_GROUP_BOT_API_ID لم يتم العثور عليه . يجب التاكد من ان الفار صحيح."
            )
        except TypeError:
            LOGS.error(
                "PRIVATE_GROUP_BOT_API_ID قيمه هذا الفار غير مدعومه. تأكد من انه صحيح."
            )
        except Exception as e:
            LOGS.error(
                "حدث خطأ عند محاولة التحقق من فار PRIVATE_GROUP_BOT_API_ID.\n" + str(e)
            )
    else:
        descript = "هذه هي مجموعه الحفظ الخاصه بك لا تحذفها ابدا . "
        photobt = await superthon.upload_file(file="razan/razan/Jmthonp.jpg")
        _, groupid = await create_supergroup(
            "كروب بوت سوبرثون", superthon, Config.TG_BOT_USERNAME, descript, photobt
        )
        addgvar("PRIVATE_GROUP_BOT_API_ID", groupid)
        print(
            "المجموعه الخاصه لفار الـ PRIVATE_GROUP_BOT_API_ID تم حفظه بنجاح و اضافه الفار اليه."
        )
        flag = True
    if PM_LOGGER_GROUP_ID != -100:
        try:
            entity = await superthon.get_entity(PM_LOGGER_GROUP_ID)
            if not isinstance(entity, types.User) and not entity.creator:
                if entity.default_banned_rights.send_messages:
                    LOGS.info(
                        " الصلاحيات غير كافيه لأرسال الرسالئل في مجموعه فار ااـ PM_LOGGER_GROUP_ID."
                    )
                if entity.default_banned_rights.invite_users:
                    LOGS.info(
                        "لا تمتلك صلاحيات اضافه اعضاء في مجموعة فار الـ  PM_LOGGER_GROUP_ID."
                    )
        except ValueError:
            LOGS.error(
                "PM_LOGGER_GROUP_ID يم تم العثور على قيمه هذا الفار . تاكد من أنه صحيح ."
            )
        except TypeError:
            LOGS.error("PM_LOGGER_GROUP_ID قيمه هذا الفار خطا. تاكد من أنه صحيح.")
        except Exception as e:
            LOGS.error("حدث خطأ اثناء التعرف على فار PM_LOGGER_GROUP_ID.\n" + str(e))
    else:
        descript = " مجموعة تخزين رسائل الخاص /n مقدمة من سوبرثون @Superthon "
        photobt = await superthon.upload_file(file="Superthon/Files/FilesPh/Superthon-logo-group.jpg")
        _, groupid = await create_supergroup(
            "تخزين سوبرثون", superthon, Config.TG_BOT_USERNAME, descript, photobt
        )
        addgvar("PM_LOGGER_GROUP_ID", groupid)
        print("تم عمل الكروب التخزين بنجاح واضافة الفارات اليه.")
        flag = True
    if flag:
        executable = sys.executable.replace(" ", "\\ ")
        args = [executable, "-m", "superthon"]
        os.execle(executable, *args, os.environ)
        sys.exit(0)
