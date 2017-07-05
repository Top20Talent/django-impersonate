#  -*- coding: utf-8 -*-
import logging
from django.conf import settings
from django.contrib import admin
from django.urls import reverse
from django.utils.translation import ugettext
from django.utils.translation import ugettext_lazy as _
from .helpers import User, users_impersonable
from .models import ImpersonationLog, ImpersonateUser

logger = logging.getLogger(__name__)


def friendly_name(user):
    '''Return proper name if exists, else username.'''
    name = None
    if hasattr(user, 'get_full_name'):
        name = user.get_full_name()
    return name or user.username


class SessionStateFilter(admin.SimpleListFilter):
    ''' Custom admin filter based on the session state.

        Provides two filter values - 'complete' and 'incomplete'.
        A session that has no session_ended_at timestamp is
        considered incomplete. This field is set from the
        session_end signal receiver.
    '''
    title = 'session state'
    parameter_name = 'session'

    def lookups(self, request, model_admin):
        return (
            ('incomplete', 'Incomplete'),
            ('complete', 'Complete'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'incomplete':
            return queryset.filter(session_ended_at__isnull=True)
        if self.value() == 'complete':
            return queryset.filter(session_ended_at__isnull=False)
        else:
            return queryset


class ImpersonatorFilter(admin.SimpleListFilter):
    ''' Custom admin filter based on the impersonator.

        Provides a set of users who have impersonated at some point.
        It is assumed that this is a small list of users - a subset
        of staff and superusers. There is no corresponding filter
        for users who have been impersonated, as this could be a
        very large set of users.

        If the number of unique impersonators exceeds MAX_FILTER_SIZE,
        then the filter is removed (shows only 'All').
    '''
    title = 'impersonator'
    parameter_name = 'impersonator'

    def lookups(self, request, model_admin):
        ''' Return list of unique users who have been an impersonator.
        '''
        # the queryset containing the ImpersonationLog objects
        MAX_FILTER_SIZE = getattr(settings, 'IMPERSONATE_MAX_FILTER_SIZE', 100)
        try:
            # Evaluate here to raise exception if needed
            ids = list(
                model_admin.get_queryset(
                    request,
                ).order_by().values_list(
                    'impersonator_id',
                    flat=True,
                ).distinct('impersonator_id')
            )
        except NotImplementedError:
            # Unit tests use sqlite db backend which doesn't support distinct.
            qs = model_admin.get_queryset(request).only('impersonator_id')
            ids = set([x.impersonator_id for x in qs])

        if len(ids) > MAX_FILTER_SIZE:
            logger.debug(
                ('Hiding admin list filter as number of impersonators [{0}] '
                 'exceeds MAX_FILTER_SIZE [{1}]').format(
                     len(ids),
                     MAX_FILTER_SIZE,
                 )
            )
            return

        impersonators = \
            User.objects.filter(id__in=ids).order_by(User.USERNAME_FIELD)
        for i in impersonators:
            yield (i.id, friendly_name(i))

    def queryset(self, request, queryset):
        if self.value() in (None, ''):
            return queryset
        else:
            return queryset.filter(impersonator_id=self.value())


class ImpersonationLogAdmin(admin.ModelAdmin):
    icon = '<i class="material-icons">history</i>'

    list_display = (
        'impersonator',
        'impersonating',
        'session_key',
        'session_started_at',
        'duration'
    )
    readonly_fields = (
        'impersonator',
        'impersonating',
        'session_key',
        'session_started_at',
        'session_ended_at',
    )
    list_filter = (
        SessionStateFilter,
        ImpersonatorFilter,
        'session_started_at',
    )

    @staticmethod
    def impersonator(obj):
        return friendly_name(obj.impersonator)

    @staticmethod
    def impersonating(obj):
        return friendly_name(obj.impersonating)


class ImpersonateUserAdmin(admin.ModelAdmin):
    icon = '<i class="material-icons">transfer_within_a_station</i>'
    list_display = ('username', 'impersonate')
    search_fields = ('username',)
    actions = None

    list_display_links = None

    def get_queryset(self, request):
        return users_impersonable(request)

    def has_add_permission(self, request):
        return False

    def impersonate(self, obj):
        return '<a href="{}" class="btn grey lighten-3"><i class="material-icons left">play_arrow</i>{}</a>'.format(
            reverse('impersonate-start', kwargs={'uid': obj.pk}),
            ugettext('Impersonate')
        )

    impersonate.allow_tags = True
    impersonate.short_description = _("Impersonate")


admin.site.register(ImpersonationLog, ImpersonationLogAdmin)
admin.site.register(ImpersonateUser, ImpersonateUserAdmin)
