#!/usr/bin/env python
# -*- coding: utf-8 -*-

# (c) 2016, Antonio Perez-Aranda <ant30tx@gmail.com>
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.
#

DOCUMENTATION = '''
---
module: ruby_rake
short_description: Manage tasks for ruby app.
description:
     - A specific module to launch ruby rakes tasks in a given environment.
version_added: "2.1"
options:
  command:
    description:
      - The tasks to execute
    required: true
  app_path:
    description:
      - The path to the root of the project
    required: true
  use_bundle_context:
    description:
      - Use bundle exec context if true
    required: false
  ruby_context:
    description:
      - Select the ruby changer method, valid values are [chruby]
    requireed: false
  environment:
    description:
      - A yaml dictionary with extra environment variables. A simple bash
        interpolation can be done here.
    required: false
notes:
   - Add some notes here.
author: "Antonio Perez-Aranda (@ant30)"
'''

EXAMPLES = """
# Execute a ruby rake tasks.
- ruby_rake:
    - name: Check VARIABLE_1 exists
      ruby_rake:
        command: poc:var_present[VARIABLE_1]
        environment:
          VARIABLE_1: VALUE_1

"""

import datetime
import os
import re
import sys

from ansible.module_utils.basic import *  # NOQA


def _fail(module, cmd, out, err, **kwargs):
    msg = ''
    if out:
        msg += "stdout: %s" % (out, )
    if err:
        msg += "\n:stderr: %s" % (err, )
    module.fail_json(cmd=cmd, msg=msg, **kwargs)


RE_VAR_SEARCHERS = [
    re.compile(r"\$\{(\w+)\}"),
    re.compile(r"\$(\w+)")
]


def _interpolate_env_var(value):
    """ We want to interpolate env vars to allow to execute the rake in a secure
        shell
    """
    for var_searcher in RE_VAR_SEARCHERS:
        searched = var_searcher.findall(value)
        for envvar in searched:
            value = value.replace("${}".format("envvar"),
                                  os.environ.get(envvar, ""))
    return value


def _load_chruby(module):
    # TODO: This should be change to be execute out of the rake and capture
    # environment vars. Otherwise this could be incusecure to execute.
    app_path = os.path.expanduser(module.params['app_path'])
    return ("source /usr/local/share/chruby/chruby.sh ; "
            "chruby $(cat {}/.ruby-version) ; ".format(app_path))


# TODO: Implements ruby contexts for rvm, rbenv
RUBY_CONTEXTS = {
    'chruby': _load_chruby,
}


def _verify_ruby_context(module, ruby_context):
    if ruby_context is not None and ruby_context not in RUBY_CONTEXTS:
        _fail(module, "", "", "{} is not a valid ruby context".format(
            ruby_context))


def _load_ruby_context(ruby_context, module):
    return RUBY_CONTEXTS[ruby_context](module)


def main():
    module = AnsibleModule(
        argument_spec=dict(
            command=dict(default=None, required=True),
            app_path=dict(default=None, required=True),
            environment=dict(default={}, required=False),
            use_bundle_context=dict(default=True, required=False, type='bool'),
            ruby_context=dict(default=None, required=False),
        ),
    )

    command = module.params['command']
    app_path = os.path.expanduser(module.params['app_path'])
    use_bundle_context = module.params['use_bundle_context']
    environment = module.params['environment']
    ruby_context = module.params['ruby_context']

    _verify_ruby_context(module, ruby_context)

    cmd = "("

    if ruby_context:
        cmd += _load_ruby_context(ruby_context, module)

    if use_bundle_context:
        cmd += "bundle exec"

    cmd = "{} rake {}".format(cmd, command)

    if environment:
        cmd = "{} -- {}".format(
            cmd,
            " ".join(["=".join((key, _interpolate_env_var(value)))
                      for (key, value) in environment.iteritems()])
        )

    cmd += ")"

    startd = datetime.datetime.now()

    rc, out, err = module.run_command(cmd, executable="/bin/bash", cwd=app_path,
                                      use_unsafe_shell=True)

    endd = datetime.datetime.now()
    delta = endd - startd

    if rc != 0:
        _fail(module, cmd, out, err, path=os.environ["PATH"], syspath=sys.path)

    changed = False

    module.exit_json(
        changed=changed,
        cmd=cmd,
        rc=rc,
        app_path=app_path,
        environment=environment,
        use_bundle_context=use_bundle_context,
        stdout=out.rstrip("\r\n"),
        stderr=err.rstrip("\r\n"),
        start=str(startd),
        end=str(endd),
        delta=str(delta),
    )

main()
