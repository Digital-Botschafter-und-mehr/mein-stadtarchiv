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

from mongoengine import ReferenceField, DateTimeField, StringField, ListField, IntField, DictField, FloatField
from .Base import Base
from .File import File
from mongoengine import signals


class Document(Base):
    uid = StringField()
    order_id = StringField()
    orderId = StringField()

    title = StringField(fulltext=True, sortable=True)
    description = StringField(fulltext=True)
    note = StringField(fulltext=True)
    origination = StringField()
    help_required = IntField(default=0)
    helpRequired = IntField(default=0)

    date = DateTimeField(datetime_format='date')
    dateBegin = DateTimeField(datetime_format='date')
    dateEnd = DateTimeField(datetime_format='date')
    dateText = StringField()

    category = ListField(ReferenceField('Category', deref_document=True))
    tags = ListField(StringField())

    address = StringField()
    postcode = StringField()
    locality = StringField()
    lat = FloatField()
    lon = FloatField()

    georeferencePrecision = StringField()
    georeferenceDone = DateTimeField(datetime_format='datetime')

    extraFields = DictField(delete_document=True)
    document_type = StringField()  # TO DELETE
    documentType = StringField()

    _file_cache = None

    @property
    def files(self):
        if self._file_cache is not None:
            return self._file_cache
        self._file_cache = []
        for file in File.objects(document=self).all():
            self._file_cache.append(file)
        return self._file_cache

    def __repr__(self):
        return '<Document %r>' % self.title


def update_index(sender, document):
    from ..data_worker.DataWorkerHelper import worker_celery_single as index_document
    index_document.apply_async((str(document.id), ), countdown=5)


signals.pre_save.connect(update_index, sender=Document)
