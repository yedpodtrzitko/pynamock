import os
import logging

logger = logging.getLogger(__name__)


class TestPynamoMixin(object):
    register_dynamo_models = []
    allow_dynamo_mocking = True

    @classmethod
    def get_testing_dynamo(cls, mocked=False):
        from pynamodb.connection.base import Connection
        class AutoboostrapConnection(Connection):
            def __init__(self, region=None, host=None, *args, **kwargs):
                super(AutoboostrapConnection, self).__init__(region, host, *args, **kwargs)
                if not hasattr(AutoboostrapConnection, '_schema_ready') and cls.register_dynamo_models:
                    logger.info("creating DB schemas: %s" % cls.register_dynamo_models)
                    AutoboostrapConnection._schema_ready = True
                    for item in cls.register_dynamo_models:
                        item.create_table(read_capacity_units=1, write_capacity_units=1)
                else:
                    logger.info("skipping DB schemas creation")

        class MockedConnection(AutoboostrapConnection):
            def __init__(self, region=None, host=None, *args, **kwargs):
                region = 'localhost'
                host = 'http://localhost:8000'
                super(MockedConnection, self).__init__(region, host, *args, **kwargs)

        return MockedConnection if mocked and cls.allow_dynamo_mocking else AutoboostrapConnection

    @classmethod
    def setup_class(cls):
        # marks if the data are for the whole class or for a single test only
        cls._class_items = []
        cls._test_items = []
        cls.class_data = True

        import pynamodb.models
        import pynamodb.connection

        def save_override(self, *args, **kwargs):
            if cls.class_data:
                cls._class_items.append(self)
            else:
                cls._test_items.append(self)

            return original_save(self, *args, **kwargs)

        mock_connection = cls.get_testing_dynamo(os.environ.get('MOCK_DYNAMODB'))
        pynamodb.connection.table.Connection = mock_connection
        original_save = pynamodb.models.Model.save
        pynamodb.models.Model.save = save_override

        cls.setup_class_custom()

        # decide if data are for the whole class or a single test
        cls.class_data = False

    @classmethod
    def setup_class_custom(cls):
        pass

    @classmethod
    def teardown_class(cls):
        for item in cls._class_items:
            item.delete()
        cls._class_items = []
        cls.teardown_class_custom()

    @classmethod
    def teardown_class_custom(cls):
        pass

    def teardown(self):
        for item in self._test_items:
            item.delete()
        self._test_items = []
