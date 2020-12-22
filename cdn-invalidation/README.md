## Create AWS Lambda Function Triggered By S3 Notification Event
![Alt Text](https://dev-to-uploads.s3.amazonaws.com/i/mas2ibsh4qgai9pi184w.png)

- The Amazon S3 notification feature is able to receive notifications when certain events happen in your bucket.
- To enable notifications, it must first adds a notification configuration that identifies the events that want Amazon S3 to publish and the destinations where to send the notifications here is lambda function
- [Overview of notifications](https://docs.aws.amazon.com/AmazonS3/latest/dev/NotificationHowTo.html)
- This post describe how to use AWS chalice to create this.

![Alt Text](https://dev-to-uploads.s3.amazonaws.com/i/1x6etu16pe1ovse4fjjq.png)

###**1. Create aws chalice new-project cdn-invalidation**
```
⚡ $ chalice new-project cdn-invalidation
⚡ $ ls cdn-invalidation
app.py  requirements.txt
```

###**2. Define which region to create lambda function instead of the default in local aws configuration**
```
⚡ $ export AWS_DEFAULT_REGION=us-east-1
```

###**3. Create lamdba function handler**
- The handler listen to `s3:ObjectCreated:Put` event so any changes in s3://mybucket/static/src will trigger the lambda function
```
from chalice import Chalice
import boto3
import time


app_name = 'cdn-invalidation'
app = Chalice(app_name=app_name)
app.debug = True


class InvalidateCDN:
    """ Invalidate CDN """
    def __init__(self):
        self.distribution_id = 'A1AA1AA11A11AA'
        self.client = boto3.client('cloudfront')

    def create_invalidation(self, file_change):
        try:
            res = self.client.create_invalidation(
                DistributionId=self.distribution_id,
                InvalidationBatch={
                    'Paths': {
                        'Quantity': 1,
                        'Items': ["/{}".format(file_change)]
                    },
                    'CallerReference': str(time.time()).replace(".", "")
                }
            )
            invalidation_id = res['Invalidation']['Id']
            return invalidation_id
        except Exception as err:
            print(f"Failed to create invalidation, error {err}")
            exit(1)

    def get_invalidation_status(self, inval_id):
        try:
            res = self.client.get_invalidation(
                DistributionId=self.distribution_id,
                Id=inval_id
            )
            return res['Invalidation']['Status']
        except Exception as err:
            print(f"Failed to get invalidation status ID {inval_id}, error {err}")
            exit(1)

    def run(self, key):
        print(f"Deploying CDN file: {key}")
        the_id = self.create_invalidation(key)
        count = 0
        while True:
            status = self.get_invalidation_status(the_id)
            if status == 'Completed':
                print(f"Completed, id: {the_id}")
                break
            elif count < 10:
                count += 1
                time.sleep(30)
            else:
                print("Timeout, please check CDN")
                break


@app.on_s3_event(bucket='mybucket',
                 prefix='static/src/',
                 events=['s3:ObjectCreated:Put'])
def handle_s3_event(event):
    cdn = InvalidateCDN()
    cdn.run(event.key)
```

###**4. Update requirements.txt to include boto3 in lambda fuction**
```
⚡ $ cat requirements.txt
boto3
```

###**5. Deploy**
```
⚡ $ chalice deploy
```
![Alt Text](https://dev-to-uploads.s3.amazonaws.com/i/hxctt81rfhbglbgg0lur.png)

![Alt Text](https://dev-to-uploads.s3.amazonaws.com/i/brc3bn6wy1lztx0h2xy3.png)

Ref: https://dev.to/vumdao/create-aws-lambda-function-triggered-by-s3-notification-event-9p0
