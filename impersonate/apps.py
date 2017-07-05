# -*- coding: utf-8 -*-
from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class AccountsConfig(AppConfig):
    icon = '<i class="material-icons">transfer_within_a_station</i>'

    name = 'impersonate'
    verbose_name = _('Impersonate')

    def ready(self):
        from . import signals
