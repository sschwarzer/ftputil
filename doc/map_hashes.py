#! /usr/bin/env python3

import datetime
import pathlib


def map_date_to_hash(text):
    """
    Return a dictionary from `datetime` object to hash string for `text`.

    Each line in `text` has the format "<hash> <date>", for example

    a07e12d6fdfb81ed737045d33a87daa52560f944 2020-01-01 17:34:58 +0100
    """
    datetime_to_hash = {}
    for line in text.splitlines():
        hash_, date_text = line.split(" ", 1)
        datetime_ = datetime.datetime.strptime(date_text,
                                               "%Y-%m-%d %H:%M:%S %z")
        datetime_to_hash[datetime_] = hash_
    # Sort by ascending datetime.
    datetime_to_hash = dict((k, v) for (k, v) in sorted(datetime_to_hash.items()))
    return datetime_to_hash


def main():
    hg_text = pathlib.Path("hg_hashes_and_dates.txt").read_text()
    git_text = pathlib.Path("git_hashes_and_dates.txt").read_text()
    hg_map = map_date_to_hash(hg_text)
    git_map = map_date_to_hash(git_text)
    with pathlib.Path("hash_map.txt").open("w") as fobj:
        print("# Mercurial hash, Git hash", file=fobj)
        for datetime_, hg_hash_text in hg_map.items():
            try:
                # Some Mercurial commits don't have corresponding Git commits,
                # probably because adding a tag creates a commit in Mercurial,
                # but not in Git.
                git_hash_text = git_map[datetime_]
            except KeyError:
                pass
            print(hg_hash_text, git_hash_text, file=fobj)


if __name__ == "__main__":
    main()
