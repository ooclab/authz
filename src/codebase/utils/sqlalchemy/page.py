from eva.conf import settings
from sqlalchemy import asc, desc, func, inspect


def get_list(hdr, q, default_sort_by="id", allow_sort_by=None, model=None):
    # TODO: 单独测试该函数

    ins = inspect(model)
    pk = ins.primary_key[0]
    total = q.with_entities(func.count(pk)).scalar()

    sb = hdr.get_argument("sort_by", default_sort_by).lower()
    if sb not in allow_sort_by and sb != "id":
        return f"unknown-sort-by:{sb}", None, None
    # TODO: check sort_by exist!
    is_asc = hdr.get_argument("asc", "false") not in ["false", "0"]
    q = q.order_by(asc(sb) if is_asc else desc(sb))

    # pagination
    current_page = int(hdr.get_argument("current_page", 1))
    if current_page < 1:
        return f"no-such-page:{current_page}", None, None
    page_size = int(hdr.get_argument("page_size", settings.PAGE_SIZE))
    start = (current_page - 1) * page_size
    if start > total:
        return f"page-is-too-large:{current_page}", None, None
    stop = current_page * page_size
    q = q.slice(start, stop)

    return (
        "",
        q,
        {
            "page_size": page_size,
            "page": current_page,
            "total": total,
            "sort_by": sb,
            "asc": is_asc,
        },
    )
