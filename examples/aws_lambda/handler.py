import json
import logging

from honeybadger import honeybadger

from utils import MockAwsLambdaManager

honeybadger.configure(api_key='your api key')


def lambda_handler(event, context):
    """
    A buggy lambda function that tries to perform a zero division
    """
    a = 1
    b = 0

    return (a/b)

#Run this file on your terminal to test this lambda function
if __name__ == '__main__':

    with MockAwsLambdaManager() as manager:
        event = {}
        context = {}
        lambda_handler(event, context) 
