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

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email
from ..common.form import SearchBaseForm
from ..common.form_validator import ValidateDateRange


class InstallForm(FlaskForm):
    email = StringField(
        'E-Mail',
        [
            Email(
                message='Bitte geben Sie eine E-Mail an'
            )
        ]
    )
    password = PasswordField(
        'Passwort',
        [
            DataRequired(
                message='Bitte geben Sie ein Passwort ein.'
            )
        ]
    )
    mapbox_token = StringField(
        'Mapbox Token',
        [
            DataRequired(
                message='Bitte geben Sie ein Mapbox Token ein.'
            )
        ]
    )
    minio_url = StringField(
        'Öffentliche Minio URL',
        validators=[
            DataRequired(
                message='Bitte geben Sie eine öffentliche Minio URL ein.'
            )
        ]
    )
    mail_server = StringField(
        'Mail Hostname',
        [
            DataRequired(
                message='Bitte geben Sie ein Mail Hostname ein.'
            )
        ]

    )
    mail_user = StringField(
        'Mail Nutzer',
        [
            DataRequired(
                message='Bitte geben Sie ein Mail Nutzer ein.'
            )
        ]

    )
    mail_password = PasswordField(
        'Mail Passwort',
        [
            DataRequired(
                message='Bitte geben Sie ein Mail Passwort ein.'
            )
        ]

    )
    submit = SubmitField('login')



