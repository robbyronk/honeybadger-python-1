import os


class MockAwsLambdaManager:
    """
    Context manager that sets mock environment variables when calling
    the example lammbda function and destroys it on exit
    """
    def __init__(self):
        self.mock_env_variables = {
            '_HANDLER': 'mocked handler value',
            'AWS_REGION': 'mocked aws region',
            'AWS_EXECUTION_ENV': 'mock aws lambda environment',
            'AWS_LAMBDA_FUNCTION_NAME': 'test function',
            'AWS_LAMBDA_LOG_GROUP_NAME': 'test log group',
            'AWS_LAMBDA_LOG_STREAM_NAME': 'test log stream name',
            'AWS_LAMBDA_FUNCTION_VERSION': '0',
            'AWS_LAMBDA_FUNCTION_MEMORY_SIZE': '512'
        }

    def __enter__(self): 
        for key, value in self.mock_env_variables.items():
            os.environ[key] = value
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        for key in self.mock_env_variables.keys():
            del os.environ[key]

