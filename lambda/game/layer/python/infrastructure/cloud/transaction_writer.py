"""Wrappers for writing to DynamoDB in transactions"""
from domain_services.interfaces import ITransaction, ITransactionWriter


class Transaction(ITransaction):
    MAX_ITEMS = 25
  
    def __init__(self, client):
        self.client = client
        self.items = []
        self.after_funcs = []

    def __enter__(self):
        assert self.items == [], 'Tried creating a new transaction before the previous one was completed'
        return self

    def __exit__(self, type, value, traceback):
        if not self.items:
            return

        items = self.items
        after_funcs = self.after_funcs
        self.items = [] # clear in case of exception
        self.after_funcs = [] 
        self.client.transact_write_items(TransactItems=items)
        for func in after_funcs:
            func()

    def write(self, item):
        assert len(item) < self.MAX_ITEMS, 'Too many writes for a transaction'
        self.items.append(item)

    def then(self, func):
        self.after_funcs.append(func)

    def clear(self):
        self.items = []
        self.after_funcs = []


class TransactionWriter(ITransactionWriter):
    """Created to perform multiple database writes in a single transaction.
    https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html#DynamoDB.Client.transact_write_items
    
    Example usage:
    
        with DynamoDbTransactionWriter.create() as transaction:
            transaction.write(...) # not executed
            transaction.write(...) # not executed
        # both are now executed
    """

    def __init__(self, client):
        self.client = client

    def create(self) -> ITransaction:
      return Transaction(self.client)
