import re
from unidecode import unidecode

try:
    from urlparse import urlparse, urljoin
except ImportError:
    from urllib.parse import urlparse, urljoin

from flask import request, redirect, url_for, current_app


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


def redirect_back(default='blog.index', **kwargs):
    for target in request.args.get('next'), request.referrer:
        if not target:
            continue
        if is_safe_url(target):
            return redirect(target)
    return redirect(url_for(default, **kwargs))


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['BLUELOG_ALLOWED_IMAGE_EXTENSIONS']


_punct_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')


def slugify(text, delim='-'):
    """生成仅包含ASCII字符的slug。"""
    result = []
    for word in _punct_re.split(text.lower()):
        print(word, end='&')
        result.extend(unidecode(word).lower().split())
        print(result)
    return delim.join(result)


if __name__ == '__main__':
    text = "邻家的豆豆龙"
    slug = slugify(text)
    print(slug)  # 输出: ni-hao-shi-jie-ni-hao-ma
