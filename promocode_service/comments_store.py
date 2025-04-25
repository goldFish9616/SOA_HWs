from collections import defaultdict
from datetime import datetime

comments_by_promo = defaultdict(list)

def add_comment(promo_id: str, client_id: str, text: str):
    comments_by_promo[promo_id].append({
        "client_id": client_id,
        "text": text,
        "created_at": datetime.utcnow().isoformat()
    })

def get_comments(promo_id: str, page: int, page_size: int):
    all_comments = comments_by_promo[promo_id]
    start = (page - 1) * page_size
    end = start + page_size
    return all_comments[start:end], len(all_comments)
