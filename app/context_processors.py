def search_query(request):
    """テンプレートで常に利用できる検索クエリ 'q' を提供します。
    POST が存在すれば優先し、なければ GET を使用します。存在しない場合は空文字を返します。
    """
    q = ''
    try:
        q = request.POST.get('q') or request.GET.get('q') or ''
    except Exception:
        q = ''
    return {'q': q}
