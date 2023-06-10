#!/usr/bin/env python3
import logging
import math
from collections import defaultdict
from pathlib import Path

import plotly.graph_objs as go
from git import Repo

logging.basicConfig(level=logging.DEBUG)


def clone_repository(repository_url):
    local_path = Path.cwd() / 'data'
    repo_path = local_path / repository_url.split('/')[-1].split('.')[0]
    if repo_path.exists() and (repo_path / '.git').is_dir():
        repo = Repo(repo_path)
        origin = repo.remotes.origin
        logging.info(f'Fetching contents of repository {repository_url} into {local_path}')
        origin.fetch()
    else:
        logging.info(f'Cloning repository {repository_url} into {local_path}')
        Repo.clone_from(repository_url, repo_path)
    return repo_path


def process_files(commit, file_types):
    author_name = commit.author.name
    for item, stats in commit.stats.files.items():
        if '.' in item:
            file_type = item.split('.')[-1]
        else:
            file_type = item.split('/')[-1]
        file_types[author_name][file_type] += stats['lines']


def get_file_types_and_authors(repository_path):
    logging.info(f'Getting file types and authors for repository {repository_path}')
    repo = Repo(repository_path)  # Replace with the path to your Git repository

    file_types = defaultdict(lambda: defaultdict(int))

    for commit in repo.iter_commits(since="1 year ago", no_merges=True):
        process_files(commit, file_types)

    return file_types


def create_stacked_histogram(file_types_and_authors):
    logging.info('Creating stacked histogram')
    data = []
    for author, file_type in file_types_and_authors.items():
        file_types = list(file_type.keys())
        number_of_lines = [math.log(x+.00001) for x in list(file_type.values())]
        trace = go.Bar(x=file_types, y=number_of_lines, name=author)
        data.append(trace)
    layout = go.Layout(barmode='stack')
    fig = go.Figure(data=data, layout=layout)
    fig.show()


file_types_and_authors = get_file_types_and_authors(clone_repository('https://github.com/git/git'))

# Print the results
for author, file_types in file_types_and_authors.items():
    print(f"{author}:")
    for file_type, count in file_types.items():
        print(f"  {file_type}: {count} lines")

create_stacked_histogram(file_types_and_authors)