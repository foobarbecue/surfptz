from pythonforandroid.recipe import CythonRecipe


class PyProjRecipe(CythonRecipe):
    version = '2.6.1'
    url = f'https://github.com/pyproj4/pyproj/archive/refs/tags/{version}.zip'
    depends = ['setuptools']
    call_hostpython_via_targetpython = False


recipe = PyProjRecipe()
