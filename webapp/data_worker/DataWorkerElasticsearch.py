# encoding: utf-8

"""
Copyright (c) 2017, Ernesto Ruge
All rights reserved.
Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

import re
import string
from bs4 import BeautifulSoup
from datetime import datetime
from flask import (Flask, Blueprint, render_template, current_app, request, flash, url_for, redirect, session, abort,
                   jsonify, send_from_directory)
from ..models import Document, Category
from ..extensions import es


class DataWorkerElasticsearch():
    def __init__(self):
        pass

    def run(self, *args):
        self.statistics = {
            'created': 0,
            'updated': 0
        }

        if not es.indices.exists_alias(name=current_app.config['ELASTICSEARCH_DOCUMENT_INDEX'] + '-latest'):
            now = datetime.utcnow()
            index_name = current_app.config['ELASTICSEARCH_DOCUMENT_INDEX'] + '-' + now.strftime('%Y%m%d-%H%M')
            mapping = self.es_mapping_generator(Document, 'deref_document')

            mapping['properties']['category_full'] = {
                'type': 'string'
            }
            mapping['properties']['date_sort'] = {
                'type': 'date',
                'format': 'date'
            }

            mapping['properties']['extra_field_text'] = {
                'type': 'string',
                'fields': {
                    'fulltext': {
                        'type': 'string',
                        'index': 'analyzed',
                        'analyzer': 'default_analyzer'
                    }
                }
            }

            mapping['properties']['autocomplete'] = {
                "type": "completion",
                "analyzer": "livesearch_import_analyzer",
                "search_analyzer": "livesearch_search_analyzer"
            }

            es.indices.create(index=index_name, body={
                'settings': self.es_settings(),
                'mappings': {
                    'document': mapping
                }
            })

            es.indices.update_aliases({
                'actions': {
                    'add': {
                        'index': index_name,
                        'alias': current_app.config['ELASTICSEARCH_DOCUMENT_INDEX'] + '-latest'
                    }
                }
            })

        else:
            index_name = list(es.indices.get_alias(current_app.config['ELASTICSEARCH_DOCUMENT_INDEX'] + '-latest'))[0]

        category_cache = {}
        for category in Category.objects.all():
            category_list = []
            category_tmp = category
            while category_tmp:
                category_list.insert(0, category_tmp.title)
                category_tmp = category_tmp.parent
            category_cache[str(category.id)] = ' → '.join(category_list)

        for document in Document.objects():
            document_dict = document.to_dict('deref_document', format_datetime=True, delete='delete_document')
            if document.files:
                document_dict['file_count'] = len(document.files)
            else:
                document_dict['file_count'] = 0

            replace_punctuation_re = re.compile('[%s\n\r]' % re.escape(string.punctuation))
            extra_fields = []
            for extra_field_value in document.extra_fields.values():
                extra_fields.append(extra_field_value)
            document_dict['extra_field_text'] = ' '.join(extra_fields)

            document_dict['category_full'] = []
            for category in document.category:
                document_dict['category_full'].append(category_cache[str(category.id)])
            if document.date:
                document_dict['date_sort'] = document.date.strftime('%Y-%m-%d')
            elif document.date_begin:
                document_dict['date_sort'] = document.date_begin.strftime('%Y-%m-%d')
            document_dict['autocomplete'] = []
            for field in ['title', 'description', 'extra_field_text']:
                if field in document_dict:
                    if document_dict[field]:
                        # Sämtliche Newlines und Zeichen entfernen
                        autocomplete_keywords = replace_punctuation_re.sub(' ', document_dict[field])
                        # Sämtliche HTML Tags entfernen
                        autocomplete_soup = BeautifulSoup(autocomplete_keywords, 'html.parser')
                        autocomplete_keywords = ' '.join(autocomplete_soup.findAll(text=True))
                        # Wörter mit Gewichtung hinzufügen
                        autocomplete_keywords = autocomplete_keywords.split(' ')
                        while '' in autocomplete_keywords:
                            autocomplete_keywords.remove('')
                        document_dict['autocomplete'].append({
                            'input': autocomplete_keywords,
                            'weight': 20 if field == 'title' else 10
                        })
            new_doc = es.index(
                index=index_name,
                id=str(document.id),
                doc_type='document',
                body=document_dict
            )
            if new_doc['result'] in ['created', 'updated']:
                self.statistics[new_doc['result']] += 1
            else:
                current_app.logger.info.warn('Unknown result at %s' % document.id)
        current_app.logger.info('ElasticSearch import successfull: %s created, %s updated' % (
        self.statistics['created'], self.statistics['updated']))

    def es_mapping_generator(self, base_object, deref=None, nested=False):
        mapping = {}
        for field in base_object._fields:
            if base_object._fields[field].__class__.__name__ == 'ListField':
                if base_object._fields[field].field.__class__.__name__ == 'ReferenceField':
                    if getattr(base_object._fields[field].field, deref):
                        mapping[field] = self.es_mapping_generator(base_object._fields[field].field.document_type,
                                                                   deref, True)
                    else:
                        mapping[field] = self.es_mapping_field_object()
                else:
                    mapping[field] = self.es_mapping_field_generator(base_object._fields[field].field)
                    if mapping[field] == None:
                        del mapping[field]
            elif base_object._fields[field].__class__.__name__ == 'ReferenceField':
                if getattr(base_object._fields[field], deref):
                    mapping[field] = self.es_mapping_generator(base_object._fields[field].document_type, deref, True)
                else:
                    mapping[field] = self.es_mapping_field_object()
            else:
                mapping[field] = self.es_mapping_field_generator(base_object._fields[field])
                if mapping[field] == None:
                    del mapping[field]
        mapping = {
            'properties': mapping
        }
        if nested:
            mapping['type'] = 'nested'
        return mapping

    def es_mapping_field_generator(self, field):
        result = {'store': True}
        if field.__class__.__name__ == 'ObjectIdField':
            result['type'] = 'string'
            result['fielddata'] = True
        elif field.__class__.__name__ == 'IntField':
            result['type'] = 'integer'
        elif field.__class__.__name__ == 'DateTimeField':
            result['type'] = 'date'
            if field.datetime_format == 'datetime':
                result['format'] = 'date_hour_minute_second'
            elif field.datetime_format == 'date':
                result['format'] = 'date'
        elif field.__class__.__name__ == 'StringField':
            result['fields'] = {}
            result['type'] = 'string'
            if hasattr(field, 'fulltext'):
                result['fields']['fulltext'] = {
                    'index': 'analyzed',
                    'type': 'string',
                    'analyzer': 'default_analyzer'
                }
            else:
                result['index'] = 'not_analyzed'
            if hasattr(field, 'sortable'):
                result['fields']['sort'] = {
                    'type': 'string',
                    'analyzer': 'sort_analyzer',
                    'fielddata': True
                }
        elif field.__class__.__name__ == 'BooleanField':
            result['type'] = 'boolean'
        else:
            return None
        return result

    def es_mapping_field_object(self):
        return {
            'store': True,
            'type': 'string'
        }

    def es_settings(self):
        return {
            'index': {
                'mapping': {
                    'nested_fields': {
                        'limit': 500
                    },
                    'total_fields': {
                        'limit': 2000
                    }
                },
                'analysis': {
                    'filter': {
                        'german_stop': {
                            "type": 'stop',
                            "stopwords": '_german_'
                        },
                        'german_stemmer': {
                            "type": 'stemmer',
                            "language": 'light_german'
                        },
                        'custom_stop': {
                            "type": 'stop',
                            'stopwords': self.generate_stopword_list()
                        }
                    },
                    'char_filter': {
                        'sort_char_filter': {
                            'type': 'pattern_replace',
                            'pattern': '"',
                            'replace': ''
                        }
                    },
                    'analyzer': {
                        # Der Standard-Analyzer, welcher case-insensitive Volltextsuche bietet
                        'default_analyzer': {
                            'type': 'custom',
                            'tokenizer': 'standard',
                            'filter': [
                                'standard',
                                'lowercase',
                                'custom_stop',
                                'german_stop',
                                'german_stemmer'
                            ]
                        },
                        'sort_analyzer': {
                            'tokenizer': 'keyword',
                            'filter': [
                                'lowercase',
                                'asciifolding',
                                'custom_stop',
                                'german_stop',
                                'german_stemmer'
                            ],
                            'char_filter': [
                                'sort_char_filter'
                            ]
                        },
                        'livesearch_import_analyzer': {
                            'tokenizer': 'keyword',
                            'filter': [
                                'lowercase',
                                'asciifolding',
                                'custom_stop',
                                'german_stop',
                                'german_stemmer'
                            ],
                            'char_filter': [
                                'html_strip'
                            ]
                        },
                        # Analyzer für die Live-Suche. Keine Stopwords, damit z.B. die -> diesel funktioniert
                        'livesearch_search_analyzer': {
                            'tokenizer': 'keyword',
                            'filter': [
                                'lowercase',
                                'asciifolding',
                                'german_stemmer'
                            ],
                            'char_filter': [
                                'html_strip'
                            ]
                        }
                    }
                }
            }
        }

    def generate_stopword_list(self):
        return []
