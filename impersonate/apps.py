# -*- coding: utf-8 -*-
from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class AccountsConfig(AppConfig):
    name = 'impersonate'
    verbose_name = _('Impersonate')

    def ready(self):
        from . import signals
