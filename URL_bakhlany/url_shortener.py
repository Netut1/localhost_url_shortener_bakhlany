import hashlib
import re
from urllib.parse import urlparse

def get_base_url(long_url):
    parsed = urlparse(long_url)
    base = f"{parsed.scheme}://{parsed.netloc}"
    return base

def extract_domain_hint(url):
    try:
        parsed = urlparse(url)
        domain = parsed.netloc
        domain = re.sub(r'^www\.', '', domain)
        parts = domain.split('.')
        main_part = parts[0] if parts[0] != 'www' else parts[1]
        hint = main_part[:4].lower()
        return hint
    except:
        return "url"

def create_short_path(base_url):
    parsed = urlparse(base_url)
    domain = parsed.netloc
    if domain.startswith('www.'):
        domain = domain[4:]
    hash_object = hashlib.sha256(domain.encode())
    hash_hex = hash_object.hexdigest()[:8]
    domain_hint = extract_domain_hint(base_url)
    short_path = f"{domain_hint}-{hash_hex}"
    return short_path

def shorten_url(long_url, base_domain="short.url"):
    if not long_url.startswith(('http://', 'https://')):
        long_url = 'https://' + long_url
    base_url = get_base_url(long_url)
    short_path = create_short_path(base_url)
    short_url = f"https://{base_domain}/{short_path}"
    return short_url, base_url

def lengthen_url(short_url):
    parsed = urlparse(short_url)
    path = parsed.path.strip('/')
    parts = path.split('-')
    if len(parts) >= 2:
        domain_hint = parts[0]
        return f"https://{domain_hint}.com"
    return None