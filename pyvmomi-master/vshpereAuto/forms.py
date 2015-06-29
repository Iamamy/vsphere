__author__ = 'amy1'

from flask.ext.wtf import Form
from wtforms import StringField, SubmitField, validators, SelectField
oper_choices = [('createsnapshot','createsnapshot'),('revertsnapshot','revertsnapshot'),('deletesnapshot','deletesnapshot')]


class vshpereForm(Form):
    host = StringField("Vsphere host")
    port = StringField("Vsphere port")
    user = StringField("Vsphere user")
    password = StringField("Vsphere password")
    operation = SelectField("Operation", choices=oper_choices)
    vappname = StringField("Vapp name")
    snapname = StringField("Snapshot name")
    submit = SubmitField("Kick off")