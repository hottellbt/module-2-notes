#!/usr/bin/python3

import typing as T
import argparse
import sys
import os
import subprocess

DESCRIPTION = """glues multiple md documents together using pandoc. tries to be
reasonably effficient by not re-gluing sections that haven't been modified
(inspired by GNU Make). the result is a single markdown file containing all
other files."""

GLUE_FILE_NAME = ".glue.md"


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def flatten(ls) -> list:
    ret = []
    for x in ls:
        if isinstance(x, list):
            for x in flatten(x):
                ret.append(x)
        else:
            ret.append(x)
    return ret


def list_of(*args) -> list:
    ret = []
    for arg in args:
        if isinstance(arg, list):
            ret.extend(flatten(arg))
        else:
            ret.append(arg)
    return ret


def file_modify_time(filename):
    if not os.path.exists(filename):
        return 0
    return os.path.getmtime(filename)


def newest_file_time(files):
    max = 0
    for file in files:
        t = file_modify_time(file)
        if t > max:
            max = t
    return max


class Pandoc:
    def __init__(
            self,
            verbose: bool,
            pandoc_exe: str,
            pandoc_args: str) -> None:
        super().__init__()
        self._pandoc_exe = pandoc_exe
        self._pandoc_args = pandoc_args
        self._verbose = verbose

        if self._verbose:
            eprint(f"pandoc_exe: {self._pandoc_exe}")
            eprint(f"pandoc_args: {self._pandoc_args}")

    def create_args(self, add_args: T.List[str] = None) -> T.List[str]:
        return list_of(self._pandoc_exe, self._pandoc_args, add_args)

    def run(
            self,
            add_args: T.List[str] = None,
            **kwargs):
        args = self.create_args(add_args)

        if self._verbose:
            eprint(f"subprocess: {' '.join(args)}")

        sp = subprocess.run(args=args, **kwargs)

        if sp.returncode != 0:
            raise RuntimeError("pandoc return nonzero exit code")

        return sp


class Document:
    def __init__(
            self,
            verbose: bool,
            path: str,
            pandoc: Pandoc) -> None:
        super().__init__()

        self._verbose = verbose
        self.path = path
        self.glue_file_path = os.path.join(self.path, GLUE_FILE_NAME)
        self._pandoc = pandoc

    def open_glue_doc(self) -> T.TextIO:
        return open(self.glue_file_path, 'a')

    def _append_file(self, path: str):
        if not os.path.exists(path):
            raise ValueError(f"does not exist: {path}")
        if not os.path.isfile(path):
            raise ValueError(f"not a regular file: {path}")
        with open(path, 'r') as f2:
            self._append_io(f2)

    def _append_markdown_file(self, path: str, header_boost: int = 0):
        if not os.path.exists(path):
            raise ValueError(f"does not exist: {path}")
        if not os.path.isfile(path):
            raise ValueError(f"not a regular file: {path}")

        header_level = 1 + header_boost

        add_args = ['-i', path, '--write', 'markdown',
                    '--base-header-level', str(header_level)]

        with self.open_glue_doc() as f:
            f.write('\n')
            self._pandoc.run(
                add_args=add_args,
                stdout=f)
            f.write('\n')

    def _append_io(self, io: T.TextIO):
        with self.open_glue_doc() as f:
            for ln in io:
                f.write(ln)

    def build(self, ignore_age: bool):
        if self._verbose:
            eprint(f'build: {self.glue_file_path}')

        raw_pages = os.listdir(self.path)

        pages = []

        for page in raw_pages:
            if page.startswith('.'):
                continue
            if os.path.isfile(page) and not page.endswith('.md'):
                continue
            pages.append(page)

        dependencies = []

        nonboosted_page_paths = []
        boosted_page_paths = []

        last_built = file_modify_time(self.glue_file_path)

        if 'index.md' in pages:
            pages.remove('index.md')
            index_path = os.path.join(self.path, 'index.md')
            if not os.path.isfile(index_path):
                raise RuntimeError(f"expected file: {index_path}")
            dependencies.append(index_path)
            nonboosted_page_paths.append(index_path)

        pages.sort()

        for page in pages:
            page_path = os.path.join(self.path, page)

            if os.path.isfile(page_path):
                dependencies.append(page_path)
                boosted_page_paths.append(page_path)
            else:
                subdoc = Document(
                    verbose=self._verbose,
                    path=page,
                    pandoc=self._pandoc)

                subdoc.build(ignore_age=ignore_age)
                dependencies.append(subdoc.glue_file_path)
                boosted_page_paths.append(subdoc.glue_file_path)

        newest_dependency = newest_file_time(dependencies)

        newest_dependency = max( 
            newest_dependency,
            file_modify_time(os.path.realpath(__file__)))

        if not ignore_age and last_built > newest_dependency:
            if self._verbose:
                eprint(f"skip!: {self.glue_file_path}")
            return

        with open(self.glue_file_path, 'w'):
            pass  # eliminate file contents

        for nonboosted_path in nonboosted_page_paths:
            self._append_markdown_file(nonboosted_path)

        for boosted_path in boosted_page_paths:
            header_boost = 1 if len(nonboosted_page_paths) > 0 else 0
            self._append_markdown_file(boosted_path, header_boost=header_boost)


def main(
        verbose: bool,
        start_path: str,
        pandoc_exe: str,
        pandoc_args: str,
        always_glue: bool):

    if not os.path.exists(start_path):
        raise ValueError(f"does not exist: {start_path}")
    if not os.path.isdir(start_path):
        raise ValueError(f"is a not a directory: {start_path}")

    pandoc = Pandoc(
        verbose=verbose,
        pandoc_exe=pandoc_exe,
        pandoc_args=pandoc_args)

    document = Document(
        verbose=verbose,
        pandoc=pandoc,
        path=start_path)

    document.build(ignore_age=always_glue)

    return document.glue_file_path


def create_argp():
    argp = argparse.ArgumentParser(
        prog="gluedoc",
        description=DESCRIPTION)

    argp.add_argument(
        '-v', '--verbose',
        default=False, action='store_true',
        help='print additional info')

    argp.add_argument(
        '-f', '--no-fail',
        default=False, action='store_true',
        help='forces the exit code to be 0')

    argp.add_argument(
        '-s', '--start',
        default=os.getcwd(),
        help='root directory where the files are stored, defaults to working directory')

    argp.add_argument(
        '-B', '--always-glue',
        default=False, action='store_true',
        help='unconditionally glue all documents')

    argp.add_argument(
        '-c', '--cat-final',
        default=False, action='store_true',
        help="cat the final glued document instead of printing its path")

    argp.add_argument(
        '--pandoc',
        default='pandoc',
        help='path to or name of the pandoc executable')

    argp.add_argument(
        '--pandoc_args',
        default=[], type=list, nargs='*',
        help='args to always pass to the pandoc executable')

    return argp


if __name__ == '__main__':
    args = create_argp().parse_args()

    try:
        path = main(
            verbose=args.verbose,
            start_path=args.start,
            pandoc_exe=args.pandoc,
            pandoc_args=args.pandoc_args,
            always_glue=args.always_glue)
    except BaseException as e:
        path = None
        if args.verbose:
            import traceback
            traceback.print_exc()
        else:
            eprint(f"error: '{str(e)}'")
            eprint('use verbose mode (-v) for more information')

    if path is None:
        if args.no_fail:
            eprint(f"masking exit code {path}")
            sys.exit(0)
        else:
            sys.exit(1)

    if args.cat_final:
        with open(path, 'r') as f:
            for ln in f:
                print(ln, end='')
    else:
        print(path)

    sys.exit(0)
