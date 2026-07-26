from collections.abc import Callable, Iterable
from typing import Any

from django import forms
from django.utils.html import format_html, format_html_join


class DatalistTextInput(forms.TextInput):
    """Text input with native browser suggestions from a dynamic value source."""

    def __init__(self, datalist_id: str, values: Iterable[str] | Callable[[], Iterable[str]], attrs=None):
        attrs = {**(attrs or {}), "list": datalist_id}
        super().__init__(attrs=attrs)
        self.datalist_id = datalist_id
        self.values = values

    def render(self, name: str, value: Any, attrs=None, renderer=None):
        input_html = super().render(name, value, attrs=attrs, renderer=renderer)
        values = self.values() if callable(self.values) else self.values
        options = format_html_join("", '<option value="{}"></option>', ((item,) for item in values if item))
        return format_html('{}<datalist id="{}">{}</datalist>', input_html, self.datalist_id, options)
