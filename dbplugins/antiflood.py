import asyncio
from telethon import events
from telethon.tl.functions.channels import EditBannedRequest
from telethon.tl.types import ChatBannedRights
from uniborg.util import admin_cmd
import sql_helpers.antiflood_sql as sql


CHAT_FLOOD = sql.__load_flood_settings()
# warn mode for anti flood
ANTI_FLOOD_WARN_MODE = ChatBannedRights(
    until_date=True,
    view_messages=None,
    send_messages=True
)


@borg.on(admin_cmd(incoming=True))
async def _(event):
    # logger.info(CHAT_FLOOD)
    if not CHAT_FLOOD:
        return
    if not (str(event.chat_id) in CHAT_FLOOD):
        return
    # TODO: exempt admins from this
    should_ban = sql.update_flood(event.chat_id, event.message.from_id)
    if not should_ban:
        return
    try:
        await borg(EditBannedRequest(
            event.chat_id,
            event.message.from_id,
            ANTI_FLOOD_WARN_MODE
        ))
    except Exception as e:  # pylint:disable=C0103,W0703
        no_admin_privilege_message = await borg.send_message(
            entity=event.chat_id,
            message=""" """.format(event.message.from_id, str(e)),
            reply_to=event.message.id
        )
        await asyncio.sleep(100)
        await no_admin_privilege_message.edit(
            "[Kurallar](http://telegra.ph/Yabancı-DiziFilm-Grup-Kuralları-10-13)",
            link_preview=True
        )
    else:
        no_admin_privilege_message = await borg.send_message(
            entity=event.chat_id,
            message="""[Sayın Üye,](tg://user?id={})\n\n__Üst üste çok fazla sayıda mesaj gönderdiğiniz için mesaj göndermeniz kısıtlandı, bizimle özelden iletişime geçebilirsiniz.__""".format(event.message.from_id),
            reply_to=event.message.id
        )
        await asyncio.sleep(100)
        await no_admin_privilege_message.edit(
            "[Kurallar](http://telegra.ph/Yabancı-DiziFilm-Grup-Kuralları-10-13)",
            link_preview=True
        )


@borg.on(admin_cmd(pattern="setflood (.*)"))
async def _(event):
    if event.fwd_from:
        return
    input_str = event.pattern_match.group(1)
    try:
        sql.set_flood(event.chat_id, input_str)
        CHAT_FLOOD = sql.__load_flood_settings()
        await event.edit("Antiflood updated to {} in the current chat".format(input_str))
    except Exception as e:  # pylint:disable=C0103,W0703
        await event.edit(str(e))
