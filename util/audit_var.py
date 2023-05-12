import disnake
from datetime import datetime, timezone, timedelta


class AuditData:
    audit_data = {}

    @staticmethod
    async def init_audit_date(bot):
        for guild in bot.guilds:
            async for entry in guild.audit_logs(action=disnake.AuditLogAction.message_delete,
                                                after=datetime.now(tz=timezone.utc) - timedelta(minutes=6)):
                if str(entry.id) not in AuditData.audit_data:
                    AuditData.audit_data[str(entry.id)] = {"count": entry.extra.count, "created_at": entry.created_at,
                                                           "user": entry.user}
                else:
                    if entry.extra.count != AuditData.audit_data[str(entry.id)]["count"]:
                        AuditData.audit_data[str(entry.id)]["count"] = entry.extra.count
