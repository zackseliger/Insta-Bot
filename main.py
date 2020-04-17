from Manager import Manager

# create manager and add accounts
manager = Manager()
manager.addAccountsFrom('accounts')

# run accounts
manager.runAccounts()