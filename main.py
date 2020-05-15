from Manager import Manager

# create manager and add accounts
manager = Manager()
manager.addAccountsFrom('accounts')

# run accounts
# manager.runAccounts()

# manager.openAccount(manager.accounts[0])

manager.runAccount(manager.accounts[0])