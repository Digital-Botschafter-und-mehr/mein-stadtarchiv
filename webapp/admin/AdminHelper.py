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

import datetime
from flask import (Flask, Blueprint, render_template, current_app, request, flash, url_for, redirect, session, abort,
                   jsonify, send_from_directory)
from flask_login import login_required, login_user, current_user, logout_user, confirm_login, login_fresh
from ..extensions import db, logger
from ..models import Comment, Category, File, Document

def set_auth(id, auth):
    category = Category.objects(id=id).first()
    if not category:
        print("category does not exist")
        return
    if category.parent:
        print("category is no root category")
        return
    category.auth = auth
    category.save()
    print('auth saved.')

def missing_media():
    for file in File.objects(binary_exists__ne=True).all():
        if file.document:
            if file.fileName:
                print('missing %s at document id %s in category %s' % (file.fileName, file.document.uid, file.document.category.title))
            else:
                print('missing %s at document id %s in category %s' % (file.id, file.document.uid, file.document.category.title))
        else:
            print('missing %s at unknown document' % (file.fileName))

def file_document_reverse():
    for file in File.objects():
        document = Document.objects(files=file.id).first()
        if not document:
            print('file %s is not part of any document')
            continue
        file.document = document.id
        file.save()