

class CustomException(Exception):
    '''
    Custom Exception

    Parameters
    __________

    amount: float, required
            Amount in $USD to be used to place order

    symbol: str, required
            Asset symbol to trade


    Returns
    _______

    param: data_type
            description

    '''

    def __init__(self, message, *args, **kwargs):
        '''
        Init Method

        Attributes
        __________

        message: str, required
                Exception description message

        code: int, required
                Error code

        '''
        self.code = kwargs['code']
        self.message = message
