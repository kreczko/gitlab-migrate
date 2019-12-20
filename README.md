# gitlab-migrate
Migration utility for GitLab servers



## Usage
### Preparation
1. Get private token from source GitLab instance
2. Get private token from destination GitLab instance
3. Create a configuration file (see examples/)
4. Run one of the commands below

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