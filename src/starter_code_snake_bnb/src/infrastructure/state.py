import services.data_service as svc

from data.owners import Owner


active_account: Owner = None


def reload_account():
    global active_account
    if not active_account:
        return

    # TODO: pull owner account from the database.
    active_account = svc.find_account_by_email(active_account.email)
