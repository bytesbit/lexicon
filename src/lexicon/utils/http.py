import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


def requests_retry_session(
    retries=3,
    backoff_factor=0.9,
    status_forcelist=(500, 502, 504),
    session=None,
):
    #  deepcode ignore missing~close~requests.Session: we already take care
    #  of it
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


def request_with_retry(method, url, retry_options=None, **kwargs):
    if retry_options is None:
        retry_options = {}
    with requests.sessions.Session() as session:
        retry_options["session"] = session
        session = requests_retry_session(**retry_options)
        return session.request(method=method, url=url, **kwargs)
