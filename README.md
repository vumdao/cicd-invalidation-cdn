## CI/CD Of Invalidation AWS CDN Using Gitlab Pipeline
![Alt Text](https://dev-to-uploads.s3.amazonaws.com/i/qcnf51y1twpjo3v8yqv3.jpg)

- CloudFront can speed up the delivery of your static content (for example, images, style sheets, JavaScript, and so on) to viewers across the globe. By using CloudFront, you can take advantage of the AWS backbone network and CloudFront edge servers to give your viewers a fast, safe, and reliable experience when they visit your website.

- A simple approach for storing and delivering static content is to use an Amazon S3 bucket. Using S3 together with CloudFront has a number of advantages, including the option to use Origin Access Identity (OAI) to easily restrict access to your S3 content.

- When developers want to update the static files, they just need to push the commit of changes, everything else leave for Gitlab pipeline job

![Alt Text](https://dev-to-uploads.s3.amazonaws.com/i/302ewebpowkc4kq5qvp3.png)

**General Flow:** Gitlab piple job sync files to S3 -> S3 notification event triggers lambda function -> Lambda function create invalidation request to cloudfront

###**1. Create Gitlab pipeline job**
```
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

###**3. [Create lambda Function associate with the S3 event using AWS chalice](https://dev.to/vumdao/create-aws-lambda-function-triggered-by-s3-notification-event-9p0)**

