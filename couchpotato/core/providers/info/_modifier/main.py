from couchpotato import get_session
from couchpotato.core.event import addEvent, fireEvent
from couchpotato.core.helpers.variable import mergeDicts, randomString
from couchpotato.core.logger import CPLog
from couchpotato.core.plugins.base import Plugin
from couchpotato.core.providers.base import MultiProvider
from couchpotato.core.settings.model import Library
import copy
import traceback

log = CPLog(__name__)


class InfoResultModifier(MultiProvider):

    def getTypes(self):
        return [Movie, Show]


class ModifierBase(Plugin):
    pass


class Movie(ModifierBase):

    default_info = {
        'tmdb_id': 0,
        'titles': [],
        'original_title': '',
        'year': 0,
        'images': {
            'poster': [],
            'backdrop': [],
            'poster_original': [],
            'backdrop_original': []
        },
        'runtime': 0,
        'plot': '',
        'tagline': '',
        'imdb': '',
        'genres': [],
        'mpaa': None
    }

    def __init__(self):
        addEvent('result.modify.info.search', self.returnByType)
        addEvent('result.modify.movie.search', self.combineOnIMDB)
        addEvent('result.modify.movie.info', self.checkLibrary)

    def returnByType(self, results):

        new_results = {'unknown':[]}
        for r in results:
            if r.get('type'):
                type_name = r.get('type') + 's'
                if not new_results.has_key(type_name):
                    new_results[type_name] = []

                new_results[type_name].append(r)
            else:
                new_results['unknown'].append(r)

        if len(new_results['unknown']) == 0:
            del new_results['unknown']

        # Combine movies, needs a cleaner way..
        if new_results.has_key('movies'):
            new_results['movies'] = self.combineOnIMDB(new_results['movies'])

        return new_results

    def combineOnIMDB(self, results):

        temp = {}
        order = []

        # Combine on imdb id
        for item in results:
            random_string = randomString()
            imdb = item.get('imdb', random_string)
            imdb = imdb if imdb else random_string

            if not temp.get(imdb):
                temp[imdb] = self.getLibraryTags(imdb)
                order.append(imdb)

            # Merge dicts
            temp[imdb] = mergeDicts(temp[imdb], item)

        # Make it a list again
        temp_list = [temp[x] for x in order]

        return temp_list

    def getLibraryTags(self, imdb):

        temp = {
            'in_wanted': False,
            'in_library': False,
        }

        # Add release info from current library
        db = get_session()
        try:
            l = db.query(Library).filter_by(identifier = imdb).first()
            if l:

                # Statuses
                active_status, done_status = fireEvent('status.get', ['active', 'done'], single = True)

                for movie in l.media:
                    if movie.status_id == active_status['id']:
                        temp['in_wanted'] = fireEvent('movie.get', movie.id, single = True)

                    for release in movie.releases:
                        if release.status_id == done_status['id']:
                            temp['in_library'] = fireEvent('movie.get', movie.id, single = True)
        except:
            log.error('Tried getting more info on searched movies: %s', traceback.format_exc())

        return temp

    def checkLibrary(self, result):

        result = mergeDicts(copy.deepcopy(self.default_info), copy.deepcopy(result))

        if result and result.get('imdb'):
            return mergeDicts(result, self.getLibraryTags(result['imdb']))
        return result


class Show(ModifierBase):
    pass
