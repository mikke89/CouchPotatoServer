from couchpotato.api import addApiView
from couchpotato.core.event import addEvent,fireEvent
from couchpotato.core.plugins.base import Plugin
from couchpotato.environment import Env
from sqlalchemy.orm import joinedload_all
from sqlalchemy.sql.expression import or_


class Charts(Plugin):

    enabled_option = 'automation_charts_display_enabled'

    def __init__(self):
        addApiView('charts.view', self.automationView)
        addEvent('app.load', self.setCrons)

    def setCrons(self):
        fireEvent('schedule.interval', 'charts.update_cache', self.updateViewCache, hours = self.conf('hour', default = 12))


    def automationView(self):

        cached_charts = self.getCache('charts_cached')

        if cached_charts:
            charts = cached_charts
        else:
            charts = self.updateViewCache()

        return {
            'success': True,
            'count': len(charts),
            'charts': charts
        }


    def updateViewCache(self):

        charts = fireEvent('automation.get_movie_list')

        for chart in charts[:]:
            if not chart['success']:
                charts.remove(chart)

        self.setCache('charts_cached', charts, timeout = 86400) # Cache for 24 hours

        return charts

