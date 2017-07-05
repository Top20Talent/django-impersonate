# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth import get_user_model
from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

User = get_user_model()


class ImpostorUser(User):
    class Meta:
        proxy = True


class ImpersonationLog(models.Model):
    """
    Stores details of each impersonation session.

    This model is used to persist details of impersonations. It hooks
    in to the session_begin and session_end signals to capture the
    details of the user impersonating and the user who is being
    impersonated. It also stores the Django session key.

    """
    impersonator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        help_text='The user doing the impersonating.',
        related_name='impersonations',
        verbose_name=_('Impersonator'),
    )
    impersonating = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='impersonated_by',
        help_text='The user being impersonated.',
        verbose_name=_('Impersonating'),
    )
    session_key = models.CharField(
        max_length=40,
        help_text='The Django session request key.',
        verbose_name=_('Session Key'),
    )
    session_started_at = models.DateTimeField(
        help_text='The time impersonation began.',
        null=True,
        blank=True,
        verbose_name=_('Session Started At'),
    )
    session_ended_at = models.DateTimeField(
        help_text='The time impersonation ended.',
        null=True,
        blank=True,
        verbose_name=_('Session Ended At'),
    )

    class Meta:
        verbose_name = _('ImpersonationLog')
        verbose_name_plural = _('ImpersonationLogs')

    @property
    def duration(self):
        return self._duration()

    def _duration(self):
        from .helpers import duration_string
        if all((self.session_started_at, self.session_ended_at)):
            return duration_string(
                self.session_ended_at - self.session_started_at,
            )
        return ''
    _duration.short_description = _('Duration')
