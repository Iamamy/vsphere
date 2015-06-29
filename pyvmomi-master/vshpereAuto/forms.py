__author__ = 'amy1'

from flask.ext.wtf import Form
from wtforms import StringField, SubmitField, validators, SelectField, PasswordField
oper_choices = [('createsnapshot','createsnapshot'),('revertsnapshot','revertsnapshot'),('deletesnapshot','deletesnapshot')]


class vshpereForm(Form):
    host = StringField("Vsphere host", default='vm.splunk.io')
    port = StringField("Vsphere port", default='443')
    user = StringField("Vsphere user")
    password = PasswordField("Vsphere password")
    operation = SelectField("Operation", choices=oper_choices)
    vappname = StringField("Vapp name")
    snapname = StringField("Snapshot name")
    submit = SubmitField("Kick off")