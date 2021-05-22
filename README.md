<p align="center">
  <a href="https://dev.to/vumdao">
    <img alt="CI/CD For CDN Invalidation Using AWS Lambda Function And Gitlab Pipeline" src="https://github.com/vumdao/cicd-invalidation-cdn/blob/master/image/cover.jpg?raw=true" width="700" />
  </a>
</p>
<h1 align="center">
  <div><b>CI/CD For CDN Invalidation Using AWS Lambda Function And Gitlab Pipeline</b></div>
</h1>

### - CloudFront can speed up the delivery of your static content (for example, images, style sheets, JavaScript, and so on) to viewers across the globe. By using CloudFront, you can take advantage of the AWS backbone network and CloudFront edge servers to give your viewers a fast, safe, and reliable experience when they visit your website.

### - A simple approach for storing and delivering static content is to use an Amazon S3 bucket. Using S3 together with CloudFront has a number of advantages, including the option to use Origin Access Identity (OAI) to easily restrict access to your S3 content.

### - When developers want to update the static files, they just need to push the commit of changes, everything else leave for Gitlab pipeline job

### - **General Flow:** Gitlab piple job sync files to S3 -> S3 notification event triggers lambda function -> Lambda function create invalidation request to cloudfront

<h1 align="center">
  <br>
  <img src="https://github.com/vumdao/cicd-invalidation-cdn/blob/master/image/flow.png?raw=true" />
</h1>

---

## What’s In This Document
- [Create Gitlab pipeline job for sync file changes to S3](#-Create-Gitlab-pipeline-job-for-sync-file-changes-to-S3)
- [Create lambda Function associate with the S3 event using AWS Chalice](#-Create-lambda-Function-associate-with-the-S3-event-using-AWS-Chalice)
- [Conclusion](#-Conclusion)

---

### 🚀 **[Create Gitlab pipeline job for sync file changes to S3](#-Create-Gitlab-pipeline-job-for-sync-file-changes-to-S3)**

```
⚡ $ cat .gitlab-ci.yaml 
before_script:
  - echo "Deploy CDN"

deploy_cdn:
  stage: deploy
  timeout: 5m
  script:
    - aws s3 sync static/src s3://static-demo/src/
  only:
    refs:
      - master
    changes:
      - static/src/**/*
  tags:
    - gitlab-runner
```

### 🚀 **[Create lambda Function associate with the S3 event using AWS Chalice](#-Create-lambda-Function-associate-with-the-S3-event-using-AWS-Chalice)**

<h1 align="center">
  <br>
  <img src="https://github.com/vumdao/cicd-invalidation-cdn/blob/master/image/s3_lambda.png?raw=true" />
</h1>

- Pre-requisite: Getting started with chalice: [Quickstart and Tutorial](https://chalice.readthedocs.io/en/stable/quickstart.html)

![Alt-Text](https://github.com/vumdao/cicd-invalidation-cdn/blob/master/image/chalice.png?raw=true)

**1. Create aws chalice new-project cdn-invalidation**

```
⚡ $ chalice new-project cdn-invalidation
⚡ $ tree
.
├── app.py
├── invalidation-cdn.json
├── __pycache__
│   └── app.cpython-38.pyc
├── README.md
└── requirements.txt

1 directory, 6 files
```

**2. Define which region to create lambda function instead of the default in local aws configuration**
```
⚡ $ export AWS_DEFAULT_REGION=us-east-1
```

**3. Create lamdba function handler which create invalidation of object files input**
- The handler listen to `s3:ObjectCreated:Put` event so any changes in `s3://mybucket/static/src` will trigger the lambda function with input of only changed object files

https://github.com/vumdao/cicd-invalidation-cdn/blob/master/cdn-invalidation/app.py


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

**4. Update` requirements.txt` to include boto3 in lambda fuction**

```
⚡ $ cat requirements.txt
boto3
```

**5. Chalice Deploy to create the lambda function**
```
⚡ $ chalice deploy
```

**6. Result**
- S3 event notifications

![Alt-Text](https://github.com/vumdao/cicd-invalidation-cdn/blob/master/image/s3_event.png?raw=true)

- Lambda Function with s3 event layer

![Alt-Text](https://github.com/vumdao/cicd-invalidation-cdn/blob/master/image/lambda_layer.png?raw=true)

### 🚀 **[Conclusion](#-Conclusion)**
- Create CI/CD of CDN Invalidateion will boost-up the deployment and clear edged location cache of your static files
- The combine of S3 notification event and lambda function will secure your flow better than executing in gitlab runner or aws cli commands
- Thank you for reading this blog, hope you learned some new thing.

---

<h3 align="center">
  <a href="https://dev.to/vumdao">:stars: Blog</a>
  <span> · </span>
  <a href="https://github.com/vumdao/cicd-invalidation-cdn">Github</a>
  <span> · </span>
  <a href="https://stackoverflow.com/users/11430272/vumdao">stackoverflow</a>
  <span> · </span>
  <a href="https://www.linkedin.com/in/vu-dao-9280ab43/">Linkedin</a>
  <span> · </span>
  <a href="https://www.linkedin.com/groups/12488649/">Group</a>
  <span> · </span>
  <a href="https://www.facebook.com/CloudOpz-104917804863956">Page</a>
  <span> · </span>
  <a href="https://twitter.com/VuDao81124667">Twitter :stars:</a>
</h3>

