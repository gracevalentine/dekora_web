class User:
    def __init__(self, user_id, first_name, last_name, email, address=None, postal_code=None, wallet=None):
        self._user_id = user_id
        self._first_name = first_name
        self._last_name = last_name
        self._email = email
        self._address = address
        self._postal_code = postal_code
        self._wallet = wallet
