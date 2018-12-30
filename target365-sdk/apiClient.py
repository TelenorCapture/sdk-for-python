from helpers.http_client import HttpClient
from helpers.http_error_handler import HttpErrorHandler
from models.lookup_result import LookupResult
from models.keyword import Keyword
from models.out_message import OutMessage
from models.strex_merchant_id import StrexMerchantId
from models.one_time_password_info import OneTimePasswordInfo


#
# TODO - not yet covered by this client library
#
# Four endpoints in swagger documentation under the "public-keys" heading



name = "target365-sdk"

class ApiClient:
    PING = "api/ping"
    LOOKUP = "api/lookup"
    KEYWORDS = "api/keywords"
    OUT_MESSAGES = "api/out-messages"
    IN_MESSAGES = "api/in-messages"
    PREPARE_MSISDNS = "api/prepare-msisdns"
    STREX_MERCHANTS = "api/strex/merchants"
    STREX_TRANSACTIONS = "api/strex/transactions"
    STREX_ONE_TIME_PASSWORDS = "api/strex/one-time-passwords"

    NOT_FOUND = 404

    def __init__(self, baseUri, keyName, privateKey):
        self.client = HttpClient(baseUri, keyName, privateKey)
        self.errorHandler = HttpErrorHandler()

    # Ping controller
    def Ping(self):
        """
          Pings the service and returns a hello message
          :return: return description
        """
        response = self.client.get(self.PING)
        self.errorHandler.throwIfNotSuccess(response)
        return response.text # returns the string "pong"

    # Lookup controller

    def Lookup(self, msisdn):
        """
        Looks up address info on a mobile phone number.
        :msisdn: Mobile phone number (required)
        :return: LookupResult
        """

        if msisdn is None:
            raise ValueError("msisdn")
        payload = {"msisdn": msisdn}
        response = self.client.getWithParams(self.LOOKUP, payload)
        if response.status_code == self.NOT_FOUND:
            return None
        self.errorHandler.throwIfNotSuccess(response)
        lookupResult = LookupResult()
        lookupResult.fromDict(response.json())
        return lookupResult

    # Keyword controller

    def CreateKeyword(self, keyword):
        """
        Creates a new keyword.
        :keyword: Keyword
        :return: string
        """
        if keyword is None:
            raise ValueError("keyword")
        response = self.client.post(self.KEYWORDS, keyword)
        self.errorHandler.throwIfNotSuccess(response)

        return self._getIdFromHeader(response.headers)

    def GetAllKeywords(self, shortNumberId=None, keyword=None, mode=None, tag=None):
        """
        Gets all keywords.
        :return: Keyword[]
        """
        params = {}
        if shortNumberId is not None:
            params["shortNumberId"] = shortNumberId
        if keyword is not None:
            params["keywordText"] = keyword
        if mode is not None:
            params["mode"] = mode
        if tag is not None:
            params["tag"] = tag

        response = self.client.getWithParams(self.KEYWORDS, params)
        self.errorHandler.throwIfNotSuccess(response)
        return Keyword().fromResponseList(response.json())

    def GetKeyword(self, keywordId):
        """
        Gets a keyword.
        :keywordId: string
        :return: Keyword
        """
        if keywordId is None:
            raise ValueError("keywordId")

        response = self.client.get(self.KEYWORDS + "/" + keywordId)
        if response.status_code == self.NOT_FOUND:
            return None

        self.errorHandler.throwIfNotSuccess(response)
        
        keyword = Keyword()
        keyword.fromDict(response.json())
        return keyword

    def UpdateKeyword(self, keyword):
        """
        Updates a keywrod
        :keyword: Keyword to update      
        """
        if keyword is None:
            raise ValueError("keyword")
        if keyword.keywordId is None:
            raise ValueError("keywordId")

        response = self.client.put(
            self.KEYWORDS + "/" + keyword.keywordId, keyword)

        self.errorHandler.throwIfNotSuccess(response)

    def DeleteKeyword(self, keywordId):
        """
        Deletes a keyword
        :keywordId: string
        """
        if keywordId is None:
            raise ValueError("keywordId")

        response = self.client.delete(self.KEYWORDS + "/" + keywordId)
        self.errorHandler.throwIfNotSuccess(response)

    # OutMessage controller
    def PrepareMsisdns(self, msisdns):
        """
        MSISDNs to prepare as a string array
        :message: string[]
        """
        if msisdns is None:
            raise ValueError("msisdns")
        response = self.client.post(self.PREPARE_MSISDNS, msisdns)
        self.errorHandler.throwIfNotSuccess(response)

    def CreateOutMessage(self, message):
        """
        Creates a new out-message
        :message: OutMessage
        """
        if message is None:
            raise ValueError("message")

        response = self.client.post(self.OUT_MESSAGES, message)
        self.errorHandler.throwIfNotSuccess(response)

        return self._getIdFromHeader(response.headers)

    def CreateOutMessageBatch(self, messages):
        """
        Creates a new out-message batch.
        :messages: OutMessage[]
        """
        if messages is None:
            raise ValueError("messages")

        response = self.client.post(self.OUT_MESSAGES + "/batch", messages)
        self.errorHandler.throwIfNotSuccess(response)

    def GetOutMessage(self, transactionId):
        """
        Gets and out-message
        :transactionId: string
        :return: OutMessage
        """
        if transactionId is None:
            raise ValueError("transactionId")

        response = self.client.get(self.OUT_MESSAGES + "/" + transactionId)
        if response.status_code == self.NOT_FOUND:
            return None

        self.errorHandler.throwIfNotSuccess(response)
        outMessage = OutMessage()
        outMessage.fromDict(response.json())
        return outMessage

    def UpdateOutMessage(self, message):
        """
        Updates a future scheduled out-message.
        :message: OutMessage
        """
        if message is None:
            raise ValueError("message")
        if message.transactionId is None:
            raise ValueError("transactionId")

        response = self.client.put(
            self.OUT_MESSAGES + "/" + message.transactionId, message)
        self.errorHandler.throwIfNotSuccess(response)

    def DeleteOutMessage(self, transactionId):
        """
        Deletes a future sheduled out-message.
        :transactionId: string
        """
        if transactionId is None:
            raise ValueError("transactionId")

        response = self.client.delete(self.OUT_MESSAGES + "/" + transactionId)
        self.errorHandler.throwIfNotSuccess(response)


    # TODO def inMessage
    # GET / api / in -messages / {shortNumberId} / {transactionId}
    # I have writtena unit test for this already, but for some reason was getting this error
    # Unauthorized - incorrect HMAC signature @ https://test.target365.io/api/in-messages/no-0000/79f35793-6d70-423c-a7f7-ae9fb1024f3b
    def GetInMessage(self, shortNumberId, transactionId):
        """
        GET /api/in-messages/{shortNumberId}/{transactionId}
        Gets and in-message
        :shortNumberId: string
        :transactionId: string
        :return: InMessage TODO no inmessage class at the moment
        """
        if transactionId is None:
            raise ValueError("transactionId")

        response = self.client.get(self.IN_MESSAGES + "/" + shortNumberId + "/" + transactionId)

        print(response)

        # if response.status_code == self.NOT_FOUND:
        #     return None
        #
        # TODO this still coded to OutMessage
        # self.errorHandler.throwIfNotSuccess(response)
        # outMessage = OutMessage()
        # outMessage.fromDict(response.json())
        # return outMessage


    # StrexMerchantIds controller

    def GetMerchantIds(self):
        """
        GET /api/strex/merchants
        Gets all merchant ids.
        :return: StrexMerchantId[]
        """
        response = self.client.get(self.STREX_MERCHANTS)
        self.errorHandler.throwIfNotSuccess(response)
        return StrexMerchantId().fromResponseList(response.json())

    def GetMerchant(self, merchantId):
        """
        GET /api/strex/merchants/{merchantId}
        Gets a merchant.
        :merchantId: string
        :returns: StrexMerchantId
        """
        if merchantId is None:
            raise ValueError("merchantId")

        response = self.client.get(self.STREX_MERCHANTS + "/" + merchantId)
        if response.status_code == self.NOT_FOUND:
            return None

        self.errorHandler.throwIfNotSuccess(response)
        strexMerchantId = StrexMerchantId()
        strexMerchantId.fromDict(response.json())
        return strexMerchantId

    def SaveMerchant(self, merchant):
        """
        PUT /api/strex/merchants/{merchantId}
        Creates/updates a merchant.
        :merchant: StrexMerchantId
        """
        if merchant is None:
            raise ValueError("merchant")
        if merchant.merchantId is None:
            raise ValueError("merchantId")

        response = self.client.put(self.STREX_MERCHANTS + "/" + merchant.merchantId, merchant)
        self.errorHandler.throwIfNotSuccess(response)

    def DeleteMerchant(self, merchantId):
        """
        DELETE /api/strex/merchants/{merchantId}
        Deletes a merchant
        :merchantId: string
        """
        if merchantId is None:
            raise ValueError("merchantId")

        response = self.client.delete(self.STREX_MERCHANTS + "/" + merchantId)
        self.errorHandler.throwIfNotSuccess(response)


    def CreateOneTimePassword(self, oneTimePasswordInfo):
        """
        POST /api/strex/one-time-passwords
        :return:
        """

        if oneTimePasswordInfo is None:
            raise ValueError("invalid oneTimePasswordInfo")
        if oneTimePasswordInfo.transactionId is None:
            raise ValueError("invalid oneTimePasswordInfo.transactionId")
        if oneTimePasswordInfo.merchantId is None:
            raise ValueError("invalid oneTimePasswordInfo.merchantId")
        if oneTimePasswordInfo.recipient is None:
            raise ValueError("invalid oneTimePasswordInfo.recipient")
        if oneTimePasswordInfo.sender is None:
            raise ValueError("invalid oneTimePasswordInfo.sender")
        if oneTimePasswordInfo.recurring is None:
            raise ValueError("invalid oneTimePasswordInfo.recurring")

        x = {
            'transactionId': '79f35793-6d70-423c-a7f7-ae9fb1024f3b',
            'merchantId': 'mer_test',
            'recipient': '+4798079008',
            'sender': 'Test',
            'recurring': False,
        }

        # TODO getting error {'Message': "Failed to save one-time password '79f35793-6d70-423c-a7f7-ae9fb1024f3b'."}


        response = self.client.post(self.STREX_ONE_TIME_PASSWORDS, x)
        self.errorHandler.throwIfNotSuccess(response)
        print(response.text)
        # TODO return value and tidy off unittest


    def GetOneTimePassword(self, transactionId):
        """
        GET /api/strex/one-time-passwords/{transactionId}

        :param transactionId:
        :return: OneTimePasswordInfo
        """

        response = self.client.get(self.STREX_ONE_TIME_PASSWORDS + '/' + transactionId)
        self.errorHandler.throwIfNotSuccess(response)

        oneTimePasswordInfo = OneTimePasswordInfo()
        oneTimePasswordInfo.fromDict(response.json())

        return oneTimePasswordInfo

    def CreateTransaction(self):
        """
        POST /api/strex/transactions
        :return:
        """

        junk = {
          "created": "2018-11-02T12:00:00Z",
          "invoiceText": "Thank you for your donation",
          "lastModified": "2018-11-02T12:00:00Z",
          "merchantId": "mer_test",
          "price": 10,
          "recipient": "+4798079008",
          "serviceCode": "14002",
          "shortNumber": "2001",
          "transactionId": "8502b85f-fac2-47cc-8e55-a20ab8680427"
        }

        # TODO Tidy this up

        response = self.client.post(self.STREX_TRANSACTIONS, junk)
        self.errorHandler.throwIfNotSuccess(response)
        print(response.text)

        print(self._getIdFromHeader(response.headers))


    def GetTransaction(self, transactionId):
        """
        GET /api/strex/transactions/{transactionId}
        :return:
        """

        # TODO getting this error below
        # {'Message': "System.Collections.Generic.KeyNotFoundException: The given key 'Sender' was not present in the dictionary.\r\n   at System.Collections.Generic.Dictionary`2.get_Item(TKey key)\r\n   at Target365.Services.TableStorageExtensions.ToStrexTransaction(DynamicTableEntity entity) in C:\\Target365\\Source\\Core\\NewApi\\Target365.Services\\TableStorageExtensions.cs:line 268\r\n   at Target365.Services.TableStorageStrexTransactionService.GetStrexTransactionAsync(String transactionId, Int64 accountId) in C:\\Target365\\Source\\Core\\NewApi\\Target365.Services\\Strex\\TableStorageStrexTransactionService.cs:line 235\r\n   at CoreApi.StrexTransactions.<>c__DisplayClass5_0.<<GetStrexTransaction>b__0>d.MoveNext() in C:\\Target365\\Source\\Core\\NewApi\\CoreApi\\Functions\\StrexTransactions.cs:line 133\r\n--- End of stack trace from previous location where exception was thrown ---\r\n   at CoreApi.ApplicationHelper.ExecuteFunctionAsync(ExecutionContext context, HttpRequestMessage request, Func`2 executor) in C:\\Target365\\Source\\Core\\NewApi\\CoreApi\\Utils\\ApplicationHelper.cs:line 40"}
        # This seems strange as teh swagger documentation indicates there is no additioanl params passed except the transactionId


        response = self.client.get(self.STREX_TRANSACTIONS + '/' + transactionId)
        self.errorHandler.throwIfNotSuccess(response)
        print(response.text)


    def DeleteTransaction(self, transactionId):
        """
        DELETE /api/strex/transactions/{transactionId}
        :param transactionId:
        :return:
        """
        # TODO Need a transaction which I can delete
        pass


    def _getIdFromHeader(self, headers):
        """
        Returns the newly created resource's identifier from the Locaion header
        :returns: resource identifier
        """
        chunks = headers["Location"].split("/")
        return chunks[-1]

