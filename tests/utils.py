# http://melp.nl/2011/02/phpunit-style-dataprovider-in-python-unit-test/
def data_provider(fn_data_provider):
    """Data provider decorator, allows another callable to provide the data for the test"""
    def test_decorator(fn):
        def repl(self, *args):
            for i in fn_data_provider():
                try:
                    fn(self, *i)
                except AssertionError:
                    print("Assertion error caught with data set %s" % repr(i))
                    raise
        return repl
    return test_decorator