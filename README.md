# genshinhelper

A Python library for miHoYo bbs and HoYoLAB Community.

## Installation

Via pip:

```
pip install genshinhelper
```

Or via source code:

```
git clone https://github.com/y1ndan/genshinhelper2.git
cd genshinhelper2
python setup.py install
```

## Basic Usage

```python
import genshinhelper as gh

cookie = 'account_id=16393939; cookie_token=jPjdK4yd7oeIifkdYhkFhkkjde00hdUgh'
g = gh.Genshin(cookie)
roles = g.roles_info
print(roles)
```

