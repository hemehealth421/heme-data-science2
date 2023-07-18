import boto3
import logging
import os
import time
from botocore.exceptions import BotoCoreError, ClientError

# Set up logging
logger = logging.getLogger(__name__)

class TextractExtractor:
    """
    A class to handle AWS Textract extraction tasks.

    Attributes
    ----------
    client : boto3.client
        A low-level, service-oriented client for AWS Textract service.

    Methods
    -------
    invoke_text_detect_job(s3_bucket_name, object_name)
        Initiates a text detection job in AWS Textract.
    check_job_complete(job_id)
        Polls AWS Textract to check if a job is completed.
    process_response(job_id)
        Processes the AWS Textract response.
    get_raw_text_list(s3_bucket_name, document_name)
        Gets a list of raw texts from AWS Textract.
    """
    
    def __init__(self):
        """
        Constructs the boto3 client with AWS credentials.
        """

        # AWS Credentials stored in environment variables
        aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
        aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        aws_default_region = os.getenv('AWS_DEFAULT_REGION')

        try:
            self.client = boto3.client(
                service_name="textract",
                region_name=aws_default_region,
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key
            )
        except (BotoCoreError, ClientError) as e:
            logger.exception("Failed to initialize boto3 client")
            raise e

    def invoke_text_detect_job(self, s3_bucket_name, object_name):
        """
        Initiates a text detection job in AWS Textract.
        """
        try:
            response = self.client.start_document_text_detection(
                DocumentLocation={
                    'S3Object': {
                        'Bucket': s3_bucket_name,
                        'Name': object_name
                    }
                })
            return response.get("JobId")
        except (BotoCoreError, ClientError) as e:
            logger.exception(f"Failed to invoke text detection job: {e}")
            raise e

    def check_job_complete(self, job_id):
        """
        Polls AWS Textract to check if a job is completed.
        """
        try:
            time.sleep(5)
            response = self.client.get_document_text_detection(JobId=job_id)
            status = response.get("JobStatus")
            logger.debug(f"Job status: {status}")

            while status == "IN_PROGRESS":
                time.sleep(5)
                response = self.client.get_document_text_detection(JobId=job_id)
                status = response.get("JobStatus")
                logger.debug(f"Job status: {status}")

            return status
        except (BotoCoreError, ClientError) as e:
            logger.exception(f"Failed to check job completion: {e}")
            raise e

    def process_response(self, job_id):
        """
        Processes the AWS Textract response.
        """
        pages = []
        page_lines = {}

        try:
            response = self.client.get_document_text_detection(JobId=job_id)
            pages.append(response)
            next_token = response.get("NextToken")

            while next_token:
                response = self.client.get_document_text_detection(JobId=job_id, NextToken=next_token)
                pages.append(response)
                next_token = response.get("NextToken")

            for page in pages:
                for item in page.get("Blocks", []):
                    if item.get("BlockType") == "LINE":
                        page_lines.setdefault(item.get("Page"), []).append(item.get("Text"))
                    
            return page_lines
        except (BotoCoreError, ClientError) as e:
            logger.exception(f"Failed to process response: {e}")
            raise e

    def get_raw_text_list(self, s3_bucket_name, document_name):
        """
        Gets a list of raw texts from AWS Textract.
        """
        report_text_list = []

        try:
            job_id = self.invoke_text_detect_job(s3_bucket_name, document_name)
            logger.debug(f"Textract Started job with id: {job_id}")

            if self.check_job_complete(job_id):
                pdf_report_text = self.process_response(job_id)

            for i in pdf_report_text.values():
                report_text_list.append(" ".join(i))

            return str(report_text_list)
        except Exception as error:
            logger.error(f"Textract failed to extract text")
            logger.exception("Error details:")
            return report_text_list






