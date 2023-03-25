# premedy

## Quickstart

### Service Accounts
TODO
`.goblet/config.json`

### Topic and Project
TODO

### Deploy Example
```shell
$ gcloud config set project <project>
$ git clone https://github.com/premedy/premedy
$ cd premedy
$ python3 -m venv venv
$ . venv/bin/activate
(venv) $ pip install .
(venv) $ cd example
# set <topic> and <project> in example/main.py
(venv) $ goblet deploy -l <location> -p <project>
(venv) $ gcloud run services list # get service url
(venv) $ cd ..
(venv) $ cd utils
(venv) $ ./post_finding.py ./sample_findings/FEATURE_DEMO.json <service url>
```


