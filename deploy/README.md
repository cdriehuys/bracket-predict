# Deployment

Deployment is semi-automated through Ansible.

## Setup

Create an `inventory.yml` file in this directory with the following contents:
```yaml
web:
  hosts:
    <Server IP>:
```

Next, make sure `.vault-password` contains the password for decrypting the
Ansible vault. Finally, install the used Ansible collections:
```shell
ansible-galaxy install -r requirements.yml
```

## Deploying

Invoke `ansible-playbook` to provision the server:
```shell
ansible-playbook -i inventory.yml site.yml
```

To update the source code, SSH into the server as the `ansible` user, and run
the `deploy.sh` script in the home directory.

## Development Tips

To get better diffs for changes to encrypted vault files, add the following
Git configuration:
```shell
git config \
    diff.ansible-vault.textconv \
    "ansible-vault view --vault-password-file deploy/.vault-password"
```
