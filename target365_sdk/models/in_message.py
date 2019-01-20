from .model import Model

class InMessage(Model):


    def _accepted_params(self):

        return [
            'messageId',
            'transactionId',
            'processed',
            'processAttempts',
            'sender',
            'recipient',
            'content',
            'keywordId',
            'isStopMessage',
            'created',
            'properties',
            'tags',
            'eTag',  # TODO the API is going to be changed to stop returning this property
        ]
