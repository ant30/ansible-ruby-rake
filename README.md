# An ansible module to execute ruby rakes wich a concrete environment.

There are an example playbook in examples directory.

To execute that, you can run the ```test.sh``` script in example directory.

 - module: ruby_rake
 - short_description: Manage tasks for ruby app.
 - description:
    - A specific module to launch ruby rakes tasks in a given environment.
 - version_added: "2.1"
 - options:
    - command:
       * description: The tasks to execute
       * required: true
    - app_path:
       * description: The path to the root of the project
       * required: true
    - use_bundle_context:
       * description: Use bundle exec context if true
       * required: false
    - ruby_context:
       * description: Select the ruby changer method, valid values are [chruby]
       * requireed: false
    - environment:
       * description:  A yaml dictionary with extra environment variables. A simple
         bash interpolation can be done here.
       * required: false
 - notes:
    - Add some notes here.
 - author: "Antonio Perez-Aranda (@ant30)"

## Examples

1.  Execute a ruby rake tasks.
   ```
- ruby_rake:
    - name: Check VARIABLE_1 exists
      ruby_rake:
        command: poc:var_present[VARIABLE_1]
        environment:
          VARIABLE_1: VALUE_1

    ```

2.  Execute a ruby rake tasks using chruby and bundle exec
   ```
- ruby_rake:
    - name: Check VARIABLE_1 exists
      ruby_rake:
        command: poc:var_present[VARIABLE_1]
        ruby_context: chruby
        use_bundle_context: true
        environment:
          VARIABLE_1: VALUE_1
