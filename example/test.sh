#!/bin/bash -x

set -e 

do_bundle () {
    source /usr/local/share/chruby/chruby.sh
    source /usr/local/share/chruby/auto.sh
    cd ruby_rake_module
    bundle
    cd ..
}

ansible-playbook -i inventory playbook.yml -vvv 

if [[ $? == 0 ]]; then
    echo "TEST succesfully executed"
else
    echo "TESTs failed"
fi


