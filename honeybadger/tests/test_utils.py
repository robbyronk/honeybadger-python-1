from honeybadger.utils import filter_dict

def test_filter_dict():
    data = {'foo': 'bar', 'bar': 'baz'}
    expected = {'foo': '[FILTERED]', 'bar': 'baz'}
    filter_keys = ['foo']
    assert filter_dict(data, filter_keys) == expected
