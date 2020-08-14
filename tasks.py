# coding=utf-8
"""
__purpose__ = Short commands based on invoke
__author__  = JeeysheLu <Jeeyshe@gmail.com> <https://www.lujianxin.com/> [2020/8/3 17:24]

    Copyright (c) 2020 JeeysheLu

This software is licensed to you under the MIT License. Looking forward to making it better.
"""

import os
import shutil

from invoke import task

__version__ = "3.3.0-dev"
root = os.path.dirname(os.path.abspath(__file__))
release = os.path.join(root, f"release/conan-{__version__}.tar.gz")


@task
def build(ctx):
    """
    -- build a gzipped package
    """
    print("Please build with Dockerfile or Makefile instead..")


@task
def clean(ctx):
    """
    -- clean unused files in project
    """
    files = [
        "_build",
        "build",
        "dist",
        "*.log",
        "*.pyc",
        "*.sqlite3",
        "*.xls",
        "__pycache__",
    ]
    for file in files:
        ctx.run(f"find ./ -name '{file}'| xargs rm -rf", echo=True)


@task
def install(ctx):
    """--install requirements.txt.lock or requirements.txt"""
    file = "requirements.txt.lock" if os.path.exists(
        os.path.join(root, "requirements.txt.lock")) else "requirements.txt"
    ctx.run(f'pip install -r {file} --no-cache', echo=True)


@task
def lock(ctx):
    """--lock requirements"""
    cmds = [
        'pip freeze > requirements.txt',
        'rm -rf requirements.txt.lock',
        'pip-compile --generate-hashes --allow-unsafe requirements.txt -o requirements.txt.lock'
    ]
    for cmd in cmds:
        ctx.run(cmd, echo=True)


@task
def version(ctx, new):
    """
    -- change current version to new
    """
    files = [
        ".bumpversion.cfg",
        "VERSION",
        "utils/__init__.py",
        "core/__init__.py",
        "core/settings.py",
    ]
    ctx.run(f"bumpversion --new-version {new} {' '.join(files)}", echo=True)
