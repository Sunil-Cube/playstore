import urlparse
from settings import HEADER


def get_base_url(url):
    u = urlparse.urlparse(url)
    return u.netloc


def get_url_path_sections(url):
    return str(urlparse.urlparse(url).path.rpartition('/')[0])