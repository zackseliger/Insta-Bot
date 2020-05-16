from Manager import Manager
from InstaBrowser import InstaBrowser

# create manager and add accounts
manager = Manager()
manager.addAccountsFrom('accounts')

# run accounts
manager.runAccounts()

# manager.openAccount(manager.accounts[0])