import pytest
import os
import uuid
from datetime import datetime
from datetime import timedelta
from ..api_client import ApiClient
from ..models.keyword import Keyword
from ..models.out_message import OutMessage
from ..models.strex_merchant import StrexMerchant
from ..models.one_time_password import OneTimePassword
from ..models.transaction import Transaction


@pytest.fixture
def valid_short_number_id():
    return 'NO-0000'


@pytest.fixture
def transaction_id():
    return '79f35793-6d70-423c-a7f7-ae9fb1024f3b'


@pytest.fixture(scope="session")
def random_transaction_id():
    return str(uuid.uuid4())


@pytest.fixture
def api_key_name():
    return os.environ['API_KEY_NAME']


@pytest.fixture
def api_private_key():
    return os.environ['API_PRIVATE_KEY']


@pytest.fixture
def client(api_key_name, api_private_key):
    base_uri = "https://test.target365.io/"

    client = ApiClient(base_uri, api_key_name, api_private_key)

    return client


def test_keyword_sequence(client, valid_short_number_id):
    keyword = Keyword()
    keyword.shortNumberId = valid_short_number_id
    keyword.keywordText = str(uuid.uuid4())
    keyword.mode = "Wildcard"
    keyword.forwardUrl = "https://tempuri.org"
    keyword.enabled = True
    keyword.created = "2018-04-12T12:00:00Z"
    keyword.lastModified = "2018-04-15T14:00:00Z"
    keyword.tags = ["Foo", "Bar"]

    # Create a keyword
    created_id = client.create_keyword(keyword)

    # Get the created keyword
    fetched_keyword = client.get_keyword(str(created_id))
    assert fetched_keyword.keywordText == keyword.keywordText

    # Update keyword
    fetched_keyword.keywordText = str(uuid.uuid4())
    client.update_keyword(fetched_keyword)
    updated_keyword = client.get_keyword(str(created_id))
    assert updated_keyword.keywordText == fetched_keyword.keywordText

    # Get all with filters returns record
    all_keywords = client.get_all_keywords(valid_short_number_id, None, "Wildcard", "Foo")
    assert len(all_keywords) > 0

    # Delete
    client.delete_keyword(str(created_id))

    # Trying to fetch returns None
    assert client.get_keyword(str(created_id)) is None


def test_out_message_sequence(client, valid_short_number_id):
    tomorrow = _add_days(datetime.utcnow(), 1)
    formatted = _format_datetime(tomorrow)

    # create
    out_message = OutMessage()
    out_message.sender = "0000"
    out_message.recipient = "+4798079008"
    out_message.content = "Hi! This is a message from 0000 :)"
    out_message.sendTime = formatted
    identifier = client.create_out_message(out_message)

    # get
    fetched = client.get_out_message(identifier)
    fetched.content += fetched.content

    # update
    client.update_out_message(fetched)
    updated = client.get_out_message(identifier)
    assert updated.content == fetched.content

    # delete
    client.delete_out_message(identifier)
    assert client.get_out_message(identifier) is None

    # create batch
    t1 = uuid.uuid4()
    t2 = uuid.uuid4()
    t3 = uuid.uuid4()
    out_message1 = OutMessage()
    out_message1.transactionId = str(t1)
    out_message1.sender = "0000"
    out_message1.recipient = "+4798079008"
    out_message1.content = "Hi! This is a message from 0000 :)"
    out_message1.sendTime = formatted
    out_message2 = OutMessage()
    out_message2.transactionId = str(t2)
    out_message2.sender = "0000"
    out_message2.recipient = "+4798079008"
    out_message2.content = "Hi! This is a message from 0000 :)"
    out_message2.sendTime = formatted
    out_message3 = OutMessage()
    out_message3.transactionId = str(t3)
    out_message3.sender = "0000"
    out_message3.recipient = "+4798079008"
    out_message3.content = "Hi! This is a message from 0000 :)"
    out_message3.sendTime = formatted
    messages = [out_message1, out_message2, out_message3]
    client.create_out_message_batch(messages)

    client.delete_out_message(str(t1))
    client.delete_out_message(str(t2))
    client.delete_out_message(str(t3))


def test_prepare_msisdns(client):
    client.prepare_msisdns(["+4798079008"])


def test_get_in_message(client, valid_short_number_id, transaction_id):
    in_message = client.get_in_message(valid_short_number_id, transaction_id)
    assert in_message.transactionId == transaction_id


def test_lookup_should_return_result(client):
    assert client.loopup("+4798079008") is not None


def test_strex_merchant_sequence(client, valid_short_number_id):
    merchant_id_identifier = "12341"

    # create        
    strex_merchant = StrexMerchant()
    strex_merchant.merchantId = merchant_id_identifier
    strex_merchant.shortNumberId = valid_short_number_id
    strex_merchant.password = "abcdef"
    client.save_merchant(strex_merchant)

    # get by id
    fetched = client.get_merchant(merchant_id_identifier)
    assert fetched is not None

    # get all
    assert len(client.get_merchant_ids()) > 0

    # delete
    client.delete_merchant(merchant_id_identifier)


def test_create_one_time_password(client, random_transaction_id):
    one_time_password_data = {
        'transactionId': random_transaction_id,
        'merchantId': 'mer_test',
        'recipient': '+4798079008',
        'sender': 'Test',
        'recurring': False
    }

    one_time_password = OneTimePassword(**one_time_password_data)

    client.create_one_time_password(one_time_password)


def test_get_time_password(client, transaction_id):
    one_time_password = client.get_one_time_password(transaction_id)

    assert one_time_password.transactionId == transaction_id


def test_transaction_sequence(client, random_transaction_id):
    transaction_data = {
        "created": "2018-11-02T12:00:00Z",
        "invoiceText": "Thank you for your donation",
        "lastModified": "2018-11-02T12:00:00Z",
        "merchantId": "mer_test",
        "price": 10,
        "recipient": "+4798079008",
        "serviceCode": "14002",
        "shortNumber": "2001",
        "transactionId": random_transaction_id
    }

    transaction = Transaction(**transaction_data)

    client.create_transaction(transaction)

    transaction = client.get_transaction(random_transaction_id)
    assert transaction.transactionId == random_transaction_id

    client.delete_transaction(random_transaction_id)


def test_get_server_public_key(client):
    public_key = client.get_server_public_key('2017-11-17')

    assert public_key.accountId == 8


@pytest.mark.testnow
def test_get_client_public_keys(client, api_key_name):
    client_public_keys = client.get_client_public_keys()

    found_key = False
    for client_public_key in client_public_keys:
        if client_public_key.name == api_key_name:
            found_key = True

    assert found_key is True


def test_get_client_public_key(client, api_key_name):
    client_public_key = client.get_client_public_key(api_key_name)

    assert client_public_key.name == api_key_name


# Formats datetime object into utc string
# got from https://stackoverflow.com/q/19654578/1241791
def _format_datetime(d):
    return d.strftime('%Y-%m-%dT%H:%M:%S') + d.strftime('.%f')[:4] + 'Z'


def _add_days(d, days_count):
    return d + timedelta(days=days_count)