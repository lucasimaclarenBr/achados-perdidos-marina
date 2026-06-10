from datetime import datetime, date, timezone, timedelta

BRT = timezone(timedelta(hours=-3))


def agora_brt() -> datetime:
    """Retorna o datetime atual no fuso horário de Brasília (UTC-3)."""
    return datetime.now(BRT)


def hoje_brt() -> date:
    """Retorna a data atual no fuso horário de Brasília (UTC-3)."""
    return datetime.now(BRT).date()


def formatar_dt_brt(dt_str: str, formato: str = "%d/%m/%Y %H:%M") -> str:
    """
    Converte uma string de datetime (ISO 8601 / UTC do Supabase)
    para string formatada no horário de Brasília.
    """
    if not dt_str:
        return ""
    dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
    dt_brt = dt.astimezone(BRT)
    return dt_brt.strftime(formato)