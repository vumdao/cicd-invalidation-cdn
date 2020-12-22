from chalice import Chalice
import boto3
import time
from datetime import datetime
import requests
import json
import re


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
