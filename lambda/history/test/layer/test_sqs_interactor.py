# import os
# import pytest
# from unittest.mock import patch, MagicMock

# from sqs_interactor import SqsInteractor, grouper


# class TestSqsInteractor:

#   @pytest.fixture(autouse=True)
#   def mock_env_vars(self):
#     with patch.dict(os.environ, {'QUEUE_URL': 'FAKE_URL'}):
#       yield

#   @pytest.fixture(autouse=True)
#   def sqs_mock(self):
#     mock = MagicMock()
#     yield mock

#   @pytest.fixture
#   def obj(self, sqs_mock):
#     yield SqsInteractor(sqs_mock)

#   def test_send_messages(self, obj, sqs_mock):
#     obj.send_messages([{
#       'eventID': 'abcd', 
#       'eventName': 'MODIFY', 
#     }])

#     sqs_mock.send_message_batch.assert_called_once_with(
#       QueueUrl='FAKE_URL',
#       Entries=[
#         {
#           'Id': 'abcd',
#           'MessageBody': '{"eventID": "abcd", "eventName": "MODIFY"}',
#         }  
#       ])

#   def test_get_messages(self, obj, sqs_mock):
#     contents = {
#       'MessageId': 'my_id',
#       'ReceiptHandle': 'my_handle',
#       'Something': 'hello',
#     }
#     sqs_mock.receive_message.side_effect = [
#       {'Messages': [contents]},
#       {},
#     ]
#     response = obj.get_messages()
#     expected = [contents]
#     assert expected == response

#   @pytest.mark.skip
#   def test_delete_messages(self, obj, sqs_mock):
#     pass


# @pytest.mark.parametrize('iterable, n, expected', [
#   pytest.param(
#     [],
#     1,
#     [],
#     id='empty',
#   ),
#   pytest.param(
#     [1, 2, 3, 4, 5],
#     1,
#     [[1], [2], [3], [4], [5]],
#     id='n=1',
#   ),
#   pytest.param(
#     [1, 2, 3, 4, 5],
#     2,
#     [[1, 2], [3, 4], [5]],
#     id='n=2',
#   ),
#   pytest.param(
#     [1, 2, 3, 4, 5],
#     7,
#     [[1, 2, 3, 4, 5]],
#     id='n=7',
#   ),
# ])
# def test_grouper(iterable, n, expected):
#   for a, e in zip(grouper(iterable, n), expected):
#     assert a == e
