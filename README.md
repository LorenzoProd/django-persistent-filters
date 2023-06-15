# Django Persistent Filters

Django Persistent Filters is a Python package which provide a django middleware that take care to persist the
querystring in the browser cookies or in the Django Request object.

If you have a ListView with a Form for filter the objects, this package is perfect for you!

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install:

```bash
pip install django-persistent-filters
```

## Usage

Put the middleware in the `settings.py` file:

```python
MIDDLEWARE = [
    ...,
    "persistent_filters.middleware.PersistentFiltersMiddleware"
]
```

If you want to store filters in the Request object instead Cookies, add in the `settings.py` file:
```python
PERSISTENT_FILTERS_IN_REQUEST = True
```
Add the urls with a filter form in `settings.py` file:

```python
PERSISTENT_FILTERS_URLS = [
    # You can use name urls
    reverse_lazy("user:list"),

    # or you can write the path without domain
    "/user/list"
]
```

Add in the form the button for reset filters:

```html
<button type="submit" name="reset-filters">Reset</button>
```
