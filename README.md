# Email webhook

## Prerequisites
- Docker installed on the webhook server
- SMTP relay server

## Scalr setup

Log into Scalr at the global scope, and click on Webhooks in the main menu.
In the Endpoints section, create a new endpoint with URL: `http://<webhook server IP>:5000/sendmail/`

Note down the *signing key* that Scalr generated, we will need it later.

The following Global Variable will need to be added in Scalr for the email recipient:
```
smtp_to
```

## Webhook handler setup
```
mkdir -p /opt/email-webhook/
cd /opt/email-webhook/
git clone https://github.com/scalr-tutorials/email_webhook.git .
```

- Install the Python dependencies
```
pip install -r requirements.txt -U
```

Create the configuration file:
```bash
cp uwsgi.ini.example uwsgi.ini
```

Edit `uwsgi.ini` to set the configuration variables:

* `SCALR_SIGNING_KEY`: signing key obtained when creating the webhook endpoint
* `SMTP_TO`: name of the global variable to use for the domain names
* `SCALR_SIGNING_KEY`=scalr_webhook_signinkey
* `SMTP_SERVER`=1.1.1.1
* `SMTP_FROM`=demo@scalr.com

## Run with Docker

Use the `relaunch.sh` bash script:

```bash
./relaunch.sh
```


## Check the logs

```bash
docker logs -f email-webhook
```
