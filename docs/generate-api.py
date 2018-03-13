"""Create Sphinx API Doc for all packages."""

# Standard Library
import subprocess
import pkgutil

# Pyramid
import jinja2

# Websauna
import websauna.system  # noQA
import websauna.tests  # noQA
import websauna.utils  # noQA

CMD_TEMPLATE = 'sphinx-apidoc -f -o {output_path} --separate --module-first {module_path}'
output_path = 'source/api/'
index_path = '{output_path}/index.rst'.format(output_path=output_path)
module_path = '{output_path}/websauna.rst'.format(output_path=output_path)


INDEX_TEMPLATE = """
.. raw:: html

    <style>
        .toctree-wrapper ul,
        .toctree-wrapper li {
            list-style: none !important;
            font-weight: bold;
            font-style: italic;
            margin-left: 0 !important;
        }
    </style>

===
API
===

Core
----

:doc:`websauna.system.Initializer <./websauna.system>`
    Websauna application entry point as an Initializer class, also serving as the platform configuration for customization.

.. toctree::
    :maxdepth: 4

    modules
{% for name, intro in modules.core %}

.. toctree::
    :maxdepth: 1

    {{ name }}

.. raw:: html

    <dl>
        <dd>
            {{ intro }}
        </dd>
    </dl>

{% endfor %}


Utilities
---------

{% for name, intro in modules.utils %}

.. toctree::
    :maxdepth: 1

    {{ name }}

.. raw:: html

    <dl>
        <dd>
            {{ intro }}
        </dd>
    </dl>

{% endfor %}


Testing
-------

{% for name, intro in modules.testing %}

.. toctree::
    :maxdepth: 1

    {{ name }}

.. raw:: html

    <dl>
        <dd>
            {{ intro }}
        </dd>
    </dl>

{% endfor %}
"""

MODULE_TEMPLATE = """websauna package
================

.. automodule:: websauna
    :members:
    :undoc-members:
    :show-inheritance:

Subpackages
-----------

.. toctree::

    websauna.system
    websauna.tests
    websauna.utils

"""

template = jinja2.Template(INDEX_TEMPLATE)


# http://stackoverflow.com/a/15723105/315168
def get_submodules(mod):
    modules = []
    for loader, module_name, is_pkg in pkgutil.iter_modules(mod.__path__):
        if module_name.startswith("test_"):
            continue

        mod_name = mod.__name__ + "." + module_name
        # print("Found module ", mod_name)
        module = pkgutil.importlib.import_module(mod_name)
        modules.append(module)

    results = []
    for mod in modules:
        try:
            intro = mod.__doc__.split("\n")[0]
        except Exception as exc:
            print("Module missing a docstring: {mod}".format(mod=mod))

        results.append((mod.__name__, intro))
    return results


def generate_apidoc(mod):
    module_name = mod.__package__
    module_path = '../../{module_name}/websauna'.format(module_name=module_name)
    cmd = CMD_TEMPLATE.format(output_path=output_path, module_path=module_path)
    subprocess.run(cmd, shell=True, check=True)


modules = (
    ('core', websauna.system),
    ('utils', websauna.utils),
    ('testing', websauna.tests),
)

all_modules = {}
for name, mod in modules:
    generate_apidoc(mod)
    all_modules[name] = get_submodules(mod)

with open(index_path, 'w') as fout:
    fout.write(template.render(dict(modules=all_modules)))

with open(module_path, 'w') as fout:
    fout.write(MODULE_TEMPLATE)
