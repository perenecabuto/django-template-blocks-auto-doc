#!/usr/bin/env python

from setuptools import setup


setup(
    name='django_template_blocks_auto_doc',
    version='0.1',
    description='Generates hirarquical django base templates documentation',
    author='Felipe Ramos Ferreira',
    author_email='perenecabuto@gmail.com',
    maintainer='Felipe Ramos Ferreira',
    maintainer_email='perenecabuto@gmail.com',
    url='https://github.com/perenecabuto/django-template-blocks-auto-doc',
    scripts=['bin/django_tmpl_doc.py'],
    include_package_data=True,
    install_requires=['lxml==3.1.1', 'Pygments==2.7.4'],
    zip_safe=False,

    keywords='django, template, documentation',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Code Generators',
        'Topic :: Software Development :: Quality Assurance',
        'Topic :: Software Development :: Testing',
    ],
)
