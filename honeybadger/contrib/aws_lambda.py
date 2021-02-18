import sys

from honeybadger import honeybadger
from honeybadger.plugins import Plugin
from honeybadger.utils import filter_dict

from threading import local

_thread_locals = local()
REQUEST_LOCAL_KEY = '__awslambda_current_request'

def get_execution_params():
    """
    Return current execution event & context for this thread.
    """
    return getattr(_thread_locals, REQUEST_LOCAL_KEY, None)

def set_execution_params(aws_event, aws_context):
    """
    Set current execution event & context for this thread.
    """
    request = {
        'aws_event':aws_event,
        'aws_context':aws_context
    }
    setattr(_thread_locals, REQUEST_LOCAL_KEY, request)

def clear_execution_params():
    """
    Clears execution params for this thread.
    """
    if hasattr(_thread_locals, REQUEST_LOCAL_KEY):
        setattr(_thread_locals, REQUEST_LOCAL_KEY, None)

def reraise(tp, value, tb=None):
    """
    Re-raises a caught error
    """
    assert value is not None
    if value.__traceback__ is not tb:
        raise value.with_traceback(tb)
    raise value
    
def get_lambda_bootstrap():
    """
    Get AWS Lambda bootstrap module
    """

    if "bootstrap" in sys.modules:
        return sys.modules["bootstrap"]
    elif "__main__" in sys.modules:
        if hasattr(sys.modules["__main__"], "bootstrap"):
            return sys.modules["__main__"].bootstrap  # type: ignore
        return sys.modules["__main__"]
    else:
        return None

def _wrap_lambda_handler(handler):

    def wrapped_handler(aws_event, aws_context, *args, **kwargs):
        set_execution_params(aws_event, aws_context)

        honeybadger.begin_request(aws_event)
        try:
            return handler(aws_event, aws_context, *args, **kwargs)
        except Exception as e:
            honeybadger.notify(e)
            exc_info = sys.exc_info()
            clear_execution_params()
            honeybadger.reset_context()

            #Rerase exception to proceed with normal aws error handling
            reraise(*exc_info)

    return wrapped_handler


class AWSLambdaPlugin(Plugin):

    def __init__(self):
        super(AWSLambdaPlugin, self).__init__('AWSLambda')
        lambda_bootstrap = get_lambda_bootstrap()
        self.initialize_request_handler(lambda_bootstrap)
        
    def supports(self, config, context):
        return config.is_aws_lambda_environment

    def generate_payload(self, config, context):
        """
        Generate payload by checking the lambda's
        request event & context.
        """
        request = get_execution_params()
        event = request['aws_event']
        context = request['aws_context']

        payload = {
            "handler": context.function_name,
            "version": context.function_version,
            "memory": context.memory_limit_in_mb,
            "request_id": context.aws_request_id, 
            "log_group_name": context.log_group_name,
            "log_stream_name": context.log_stream_name,
            "event": filter_dict(event, config.params_filters),
        }

        return payload
        
    def initialize_request_handler(self, lambda_bootstrap):
        """
        Here we fetch the http & event handler from the lambda bootstrap module
        and override it with a wrapped version
        """
        #Get the original handler for events & http request
        original_event_handler = lambda_bootstrap.handle_event_request
        original_http_handler = lambda_bootstrap.handle_http_request
        
        def event_handler(request_handler, *args, **kwargs):
            request_handler = _wrap_lambda_handler(request_handler)
            return original_event_handler(request_handler, *args, **kwargs)
            
        def http_handler(request_handler, *args, **kwargs):
            request_handler = _wrap_lambda_handler(request_handler)
            return original_http_handler(request_handler, *args, **kwargs)
        
        #Replace the original handlers for events & http request with a wrapped one
        lambda_bootstrap.handle_event_request = event_handler
        lambda_bootstrap.handle_http_request = http_handler
        
        
        
