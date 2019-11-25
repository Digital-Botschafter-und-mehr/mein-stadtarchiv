# encoding: utf-8

"""
Copyright (c) 2007, Ernesto Ruge
All rights reserved.
Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

from datetime import datetime
from mongoengine import Document, DateTimeField
from mongoengine import signals
from mongoengine.errors import ValidationError
from flask import abort


class Base(Document):
    created = DateTimeField(datetime_format='datetime')
    modified = DateTimeField(datetime_format='datetime')

    meta = {
        'abstract': True,
    }

    def to_dict(self, deref=None, format_datetime=True, delete=False, clean_none=False):
        result = {}
        for field in self._fields:
            if delete:
                if hasattr(self._fields[field], delete):
                    if getattr(self._fields[field], delete):
                        continue
            if clean_none and hasattr(object, field):
                if getattr(object, field):
                    continue
            if self._fields[field].__class__.__name__ == 'ListField':
                if self._fields[field].field.__class__.__name__ == 'ReferenceField':
                    if not field in result:
                        result[field] = []
                    if deref:
                        if getattr(self._fields[field].field, deref):
                            for sub_object in getattr(self, field):
                                result[field].append(sub_object.to_dict(deref=deref, format_datetime=format_datetime, delete=delete))
                        else:
                            for sub_object in getattr(self, field):
                                result[field].append(str(sub_object.id) if sub_object.id else None)
                    else:
                        for sub_object in getattr(self, field):
                            result[field].append(str(sub_object.id) if sub_object.id else None)
                else:
                    result[field] = getattr(self, field)
            elif self._fields[field].__class__.__name__ == 'ReferenceField':
                if getattr(self, field):
                    if deref:
                        if getattr(self._fields[field], deref):
                            result[field] = getattr(self, field).to_dict(deref=deref, format_datetime=format_datetime, delete=delete)
                        else:
                            result[field] = str(getattr(self, field).id) if getattr(self, field).id else None
                    else:
                        result[field] = str(getattr(self, field).id) if getattr(self, field).id else None
                else:
                    result[field] = str(getattr(self, field)) if getattr(self, field) else None
            elif self._fields[field].__class__.__name__ == 'ObjectIdField':
                result[field] = str(getattr(self, field)) if getattr(self, field) else None
            else:
                if getattr(self, field) is not None:
                    if format_datetime:
                        if self._fields[field].__class__.__name__ == 'DateTimeField':
                            if self._fields[field].datetime_format == 'datetime':
                                result[field] = getattr(self, field).strftime('%Y-%m-%dT%H:%M:%S')
                            elif self._fields[field].datetime_format == 'date':
                                result[field] = getattr(self, field).strftime('%Y-%m-%d')
                        else:
                            result[field] = getattr(self, field)
                    else:
                        result[field] = getattr(self, field)
            if field in result and clean_none:
                if result[field] == 'None':
                    del result[field]
        return result

    @classmethod
    def get(self, document_id, *args, **kwargs):
        try:
            kwargs['id'] = document_id
            return self.objects.get(*args, **kwargs)
        except ValidationError:
            return
        except self.DoesNotExist:
            return

    @classmethod
    def get_or_404(self, document_id, *args, **kwargs):
        result = self.get(document_id, *args, **kwargs)
        if not result:
            abort(404)
        return result


def update_modified(sender, document):
    if not document.created:
        document.created = datetime.utcnow()
    document.modified = datetime.utcnow()


signals.pre_save.connect(update_modified)
