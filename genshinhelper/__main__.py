"""genshinhelper entry point.

Using `python <project_package>` or `python -m <project_package>` command.
"""

if not __package__:
    import os
    import sys

    sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from .utils import get_mihoyo_app_cookie, log, _


def main(cookie):
    app_cookie = get_mihoyo_app_cookie(cookie)
    return app_cookie


if __name__ == "__main__":
    log.info(_('Converting cookie to mihoyo app cookie.'))
    raw_cookie = input(_('Please enter your cookie, similar to `account_id=xxxxxx; login_ticket=xxxxxx`: '))
    main(raw_cookie)
