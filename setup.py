from distutils.core import setup
# https://medium.com/@joel.barmettler/how-to-upload-your-python-package-to-pypi-65edc5fe9c56
setup(
    name='create_lira_issue',
    packages=['create_jira_issue'],
    version='0.1',
    license='MIT',
    description='Command line app for work with Atlassian Jira',
    author='44dw',
    author_email='elevation1987@gmail.com',
    url='https://github.com/44dw',
    download_url='https://github.com/44dw/create_jira_issue/archive/refs/tags/0.1.tar.gz',
    keywords=['Jira', 'Console'],
    install_requires=[
        'requests',
        'argparse',
        'urllib3',
        'url_normalize'
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Utilities',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
)
