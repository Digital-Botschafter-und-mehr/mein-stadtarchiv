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

from flask import g
from ..models import Category


def get_category_data(category_id):
    if category_id:
        category = Category.get(category_id)
        if not category:
            return get_root_category()
        return {
            'current': category.to_dict(),
            'parent': category.parent.to_dict() if category.parent else None,
            'children': category.get_children_list()
        }
    return get_root_category()


def get_root_category():
    category = {
        'current': {
            'id': 'all',
            'title': 'Alle Archive'
        },
        'parent': None,
        'children': []
    }
    if g.subsite:
        if len(g.subsite.categories) > 1:
            archives = Category.objects(parent__exists=False, id__in=g.subsite.categories).order_by('+title').all()
        else:
            archives = Category.objects(parent=g.subsite.categories[0]).order_by('+title').all()
    else:
        archives = Category.objects(parent__exists=False).order_by('+title').all()
    for archive in archives:
        category['children'].append(
            archive.to_dict()
        )
    return category
