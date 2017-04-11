def ensure_trailing_slash(url):
    if not url.endswith('/'):
        url += '/'
    return url
