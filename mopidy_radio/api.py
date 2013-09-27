#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#     Copyright (C) 2012 Tristan Fischer (sphere@dersphere.de)
#
#     Adapted for Mopidy by Ronald Hecht (ronald.hecht@gmx.de)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#

import json
from urllib import urlencode
from urllib2 import urlopen, Request, HTTPError, URLError
import random


class RadioApiError(Exception):
    pass


class RadioApi():

    MAIN_URLS = {
        'english': 'http://rad.io/info',
        'german': 'http://radio.de/info',
        'french': 'http://radio.fr/info',
    }

    CATEGORY_TYPES = (
        'genre', 'topic', 'country', 'city', 'language',
    )

    USER_AGENT = 'Mopidy Radio Extension'

    def __init__(self, language='english', user_agent=USER_AGENT):
        self.set_language(language)
        self.user_agent = user_agent

    def set_language(self, language):
        if not language in RadioApi.MAIN_URLS.keys():
            raise ValueError('Invalid language')
        self.api_url = RadioApi.MAIN_URLS[language]

    def get_recommendation_stations(self):
        self.log('get_recommendation_stations started')
        path = 'broadcast/editorialreccomendationsembedded'
        return self.__api_call(path)

    def get_top_stations(self):
        self.log('get_top_stations started')
        path = 'menu/broadcastsofcategory'
        param = {'category': '_top'}
        return self.__api_call(path, param)

    def get_local_stations(self, num_entries=25):
        self.log('get_local_stations started with num_entries=%d'
                 % num_entries)
        most_wanted_stations = self._get_most_wanted(num_entries)
        return self._get_most_wanted(num_entries)['localBroadcasts']

    def get_category_types(self):
        self.log('get_category_types started')
        return RadioApi.CATEGORY_TYPES

    def get_categories(self, category_type):
        self.log('get_categories started with category_type=%s'
                 % category_type)
        if not category_type in RadioApi.CATEGORY_TYPES:
            raise ValueError('Bad category_type')
        path = 'menu/valuesofcategory'
        param = {'category': '_%s' % category_type}
        categories = self.__api_call(path, param)
        return categories

    def get_stations_by_category(self, category_type, category_value):
        self.log(('get_stations_by_category started with category_type=%s, '
                  'category_value=%s') % (category_type, category_value))
        if not category_type in self.get_category_types():
            raise ValueError('Bad category_type')
        path = 'menu/broadcastsofcategory'
        param = {
            'category': '_%s' % category_type,
            'value': category_value.encode('utf-8'),
        }
        return self.__api_call(path, param)

    def search_stations_by_string(self, search_string):
        self.log('search_stations_by_string started with search_string=%s'
                 % search_string)
        path = 'index/searchembeddedbroadcast'
        param = {
            'q': search_string.encode('utf-8'),
            'start': '0',
            'rows': '100',
        }
        return self.__api_call(path, param)

    def get_station_by_station_id(self, station_id):
        self.log('get_station_by_station_id started with station_id=%s'
                 % station_id)
        path = 'broadcast/getbroadcastembedded'
        param = {'broadcast': str(station_id)}
        return self.__api_call(path, param)

    def resolve_playlist(self, station_id):
        self.log('resolve_playlist started with station_id=%s'
                 % station_id)
        path = 'playlist/resolveplaylist'
        param = {'broadcast': str(station_id)}
        return self.__api_call(path, param)

    def _get_most_wanted(self, num_entries=25):
        self.log('get_most_wanted started with num_entries=%d'
                 % num_entries)
        if not isinstance(num_entries, int):
            raise TypeError('Need int')
        path = 'account/getmostwantedbroadcastlists'
        param = {'sizeoflists': str(num_entries)}
        stations_lists = self.__api_call(path, param)
        return stations_lists

    def __api_call(self, path, param=None):
        self.log('__api_call started with path=%s, param=%s'
                 % (path, param))
        url = '%s/%s' % (self.api_url, path)
        if param:
            url += '?%s' % urlencode(param)
        response = self.__urlopen(url)
        json_data = json.loads(response)
        return json_data

    def __urlopen(self, url):
        self.log('__urlopen opening url=%s' % url)
        req = Request(url)
        req.add_header('User-Agent', self.user_agent)
        try:
            response = urlopen(req).read()
        except HTTPError, error:
            self.log('__urlopen HTTPError: %s' % error)
            raise RadioApiError('HTTPError: %s' % error)
        except URLError, error:
            self.log('__urlopen URLError: %s' % error)
            raise RadioApiError('URLError: %s' % error)
        return response

    @staticmethod
    def log(text):
        print 'RadioApi: %s' % repr(text)