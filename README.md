# bitwarden-utils

a simple wrapper around bitwarden cli with its primary job to export all attachments

## setup with github
```
pip install -e git+https://github.com/ZackaryW/bitwarden-utils.git#egg=bwutil[all]
```

## running
* both clients will attempt to find bitwarden cli
### running cli
run `bwUtilCli [options]`

![image](https://user-images.githubusercontent.com/36378555/179439123-8e365659-4f55-4fdb-84ec-02c4ba5f5254.png)

use `bwUtilCli --help` for options or reference below

### running gui
run `bwUtilGui`

![image](https://user-images.githubusercontent.com/36378555/179439197-330fa9e1-f7e4-4cf3-85ad-3ef1ab95cad6.png)

## using GUI client
1. click cli client will open a selection window

![image](https://user-images.githubusercontent.com/36378555/179439328-03c210c3-2549-4c36-bb04-07a35deb8965.png)
* select file - will prompt a file dialog to locate the cli
* download file to temp - will download the latest release of cli to a temp folder

2. once cli client is resolved, clicking the cli client again will open the folder that contains the cli

![image](https://user-images.githubusercontent.com/36378555/179439412-5a132818-713d-42bb-85b5-cdaa838b870e.png)

3. once logged in and unlocked, all features for this gui interface will be unlocked

![image](https://user-images.githubusercontent.com/36378555/179439580-17c321f4-6548-46b0-8552-8aff7a592853.png)

4. run command will return a window containing the output

![image](https://user-images.githubusercontent.com/36378555/179439693-a1f2d03c-b16c-4993-b8b5-9caebcd74cfb.png)

## Options for CLI
* runcmd - instead of exporting attachments, runs any command
* bwpath - path to bw cli
* username
* password
* totp
* downloadtemp - downloads bitwarden cli from the web and deletes it on completion
* sync/no-sync - whether to sync vault before operation
* export - export path
