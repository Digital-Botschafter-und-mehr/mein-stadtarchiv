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

from bson import ObjectId
from flask import request
from wtforms import SelectMultipleField
from wtforms.utils import unset_value
from ..models import Category


class ArchiveMultibleField(SelectMultipleField):
    def __init__(self, *args, all_option=False, **kwargs):
        super(ArchiveMultibleField, self).__init__(*args, **kwargs)

        archives = Category.objects(parent__exists=False)
        self.choices = []
        for archive in archives:
            self.choices.append((str(archive.id), archive.title))

    def process(self, formdata, data=unset_value):
        if data != unset_value and request.method == 'GET' and data:
            data = [str(item.id) for item in data]
        super(ArchiveMultibleField, self).process(formdata, data)

    def populate_obj(self, obj, name):
        setattr(obj, name, [ObjectId(object_id) for object_id in self.data])


class SubsiteMultibleField(SelectMultipleField):
    def __init__(self, *args, all_option=False, **kwargs):
        super(SubsiteMultibleField, self).__init__(*args, **kwargs)

        subsites = Category.objects(parent__exists=False)
        self.choices = []
        for subsite in subsites:
            self.choices.append((str(subsite.id), subsite.title))

    def process(self, formdata, data=unset_value):
        if data != unset_value and request.method == 'GET' and data:
            data = [str(item.id) for item in data]
        super(SubsiteMultibleField, self).process(formdata, data)

    def populate_obj(self, obj, name):
        setattr(obj, name, [ObjectId(object_id) for object_id in self.data])
