
from domain_services.interfaces import ITransaction, ITransactionWriter


class Transaction(ITransaction):

    def __init__(self):
        self.after_funcs = []

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        after_funcs = self.after_funcs
        self.items = [] # clear in case of exception
        self.after_funcs = [] 
        for func in after_funcs:
            func()

    def write(self, item):
        pass

    def then(self, func):
        self.after_funcs.append(func)

    def clear(self):
        self.after_funcs = []


class TransactionWriter(ITransactionWriter):

    def create(self) -> ITransaction:
        return Transaction()
