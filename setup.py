from setuptools import setup

setup(name='can_it',
      version='0.1',
      py_modules=['canit', 'desktop', 'direct_edit', 'main', 'mobile'],
      include_package_data=True,
      install_requires=[
          'streamlit==1.36',
          'pandas==2.1.4'
      ],
      zip_safe=True)
