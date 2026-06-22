from datetime import datetime, date, timezone, timedelta
from io import BytesIO

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

def comprimir_imagem(arquivo, largura_max: int = 800, qualidade: int = 80) -> bytes:
    """
    Comprime uma imagem enviada via st.file_uploader.
 
    - Redimensiona mantendo proporção, limitando a largura a `largura_max`.
    - Converte para JPEG com a `qualidade` informada (1-100).
    - Remove transparência (RGBA -> RGB) para garantir compatibilidade com JPEG.
 
    Retorna os bytes da imagem já comprimida, prontos para upload.
    """
    from PIL import Image
 
    imagem = Image.open(arquivo)
 
    # Remove canal alpha se existir (PNG com transparência, etc.)
    if imagem.mode in ("RGBA", "P"):
        imagem = imagem.convert("RGB")
 
    largura_atual, altura_atual = imagem.size
    if largura_atual > largura_max:
        proporcao = largura_max / largura_atual
        nova_largura = largura_max
        nova_altura = int(altura_atual * proporcao)
        imagem = imagem.resize((nova_largura, nova_altura), Image.LANCZOS)
 
    buffer = BytesIO()
    imagem.save(buffer, format="JPEG", quality=qualidade, optimize=True)
    buffer.seek(0)
    return buffer.read()