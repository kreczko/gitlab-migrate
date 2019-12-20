# gitlab-migrate
Migration utility for GitLab servers



## Usage

### Information
```
gitlab-migrate config.yml --output-file=repos_src.csv
gitlab-migrate config.yml --output-file=repos_dst.csv --server=destination
```

### Migration
```
# testing
gitlab-migrate config.yml --noop

# migration
gitlab-migrate config.yml

```


# Development
```
git clone https://github.com/kreczko/gitlab-migrate.git
cd gitlab-migrate
pip install -U -e .
```