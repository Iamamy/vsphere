__author__ = 'amy1'

from flask import Flask, render_template, request, flash
from forms import vshpereForm
from forms import oper_choices
from vsphere import vsphere
import yaml


app = Flask(__name__)
app.secret_key = 'development key'

@app.route('/home')
def home():
  return render_template('home.html')

@app.route('/about')
def about():
  return render_template('about.html')

@app.route('/log')
def showlog():
    return render_template('log.html')


@app.route('/', methods=['GET', 'POST'])
def vspherepage():
  form = vshpereForm()
  dict_yaml = {}
  if request.method == 'POST':
    if form.validate() == False:
        flash('All fields are required.')
        return render_template('vsphere.html', form=form)
    else:
        dict_yaml['host'] = str(form.host._value())
        dict_yaml['port'] = str(form.port._value())
        dict_yaml['user'] = str(form.user._value())
        dict_yaml['password'] = str(form.password._value())
        dict_yaml['operation'] = dict(oper_choices).get(form.operation.data)
        dict_yaml['vappname'] = str(form.vappname._value())
        dict_yaml['snapname'] = str(form.snapname._value())
        with open('params.yml', 'w') as outfile:
            outfile.write( yaml.dump(dict_yaml, default_flow_style=False) )
        vsphereInstance = vsphere()
        vsphereInstance.start_operation()
        return '%s is kicked off for the VMs inside vApp %s'%(dict_yaml['operation'], dict_yaml['vappname'])

  elif request.method == 'GET':
    return render_template('vsphere.html', form=form)


if __name__ == '__main__':
  app.run(debug=True)