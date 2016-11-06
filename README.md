PynamoDB Testing Helper
=======================


Purpose
-------

`TestPynamoMixin` is a mixin for easier using of PynamoDB in tests:


- allows to automatically delete data created during tests (class-data, test-data)


- allows using DynamoDBLocal



Usage
-----

The class `pynamodb.Engine` is wrapped, and all the testing data are removed after the tests.

To use this mixin, just inherit your test class:

```python
class TestMyStuff(PynamoDBMixin):

    # a list of models which will be automatically created in DynamoDB
    register_dynamo_models = [MyPynamoModel]

    @classmethod
    def setup_class_custom(cls):
        """
        setup_class is used in PynamoDBMixin, please use this function instead
        """
        # the following model will be deleted after all tests in this class will run
        cls.instance = instance = MyPynamoModel('cls pk', {'data': True})
        instance.save()

    @classmethod
    def teardown_class_custom(cls):
        """
        teardown_class is used in PynamoDBMixin, please use this function instead
        """
        pass

    def test_stuff(self):
        # the following model will be deleted after the test
        MyPynamoModel('pk', {'data': True}).save()
```


Connection to remote DynamoDB can be overriden and DynamoDBLocal can be used instead.

For this cause use the following environment variable:

`$ MOCK_DYNAMODB=true py.test ./tests`


