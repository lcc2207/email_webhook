# IPAM webhook

## Scalr setup

In Scalr, create a webhook endpoint with url:
```
    http://<webhook server IP>:5000/sendmail/
```

Then, for each email recipent that you intend to notify with Scalr:
 - In the Advanced Webhook configuration, set the user data to the email address (e.g. demo1@scalr.com) each address on a
   new line


## Configuration

Create the configuration file:
```bash
cp uwsgi.ini.example uwsgi.ini
```

Edit `uwsgi.ini` to set the configuration variables:

* `SCALR_SIGNING_KEY`: signing key obtained when creating the webhook endpoint
* `DOMAIN_GV`: name of the global variable to use for the domain names
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
