from setuptools import setup, find_packages

setup(
    name='ApiKeyManager',
    author='Team Narwhal',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'flask', 'elasticsearch', 'certifi', 'psycopg2-binary'
    ],
    entry_points={
        'console_scripts': [
            'send-emails = apikeys.tool:start',
            'update-keys = apikeys.tool:update'
        ],
    },
)
