import json

from django.conf import settings

from mock import patch
from nose.tools import eq_

from lib.paypal.header import escape
from lib.sellers.models import SellerPaypal
from lib.sellers.tests.utils import make_seller_paypal
from solitude.base import APITest


class TestGet(APITest):

    def setUp(self):
        self.api_name = 'paypal'
        self.uid = 'sample:uid'
        self.seller, self.paypal, self.product = make_seller_paypal(self.uid)
        self.paypal.token = 'f'
        self.paypal.secret = 'b'
        self.paypal.save()

    @patch('lib.paypal.client.Client.get_personal_basic')
    def test_basic_data(self, result):
        result.return_value = {'first_name': '..'}
        res = self.client.post(self.get_list_url('personal-basic'),
                               data={'seller': self.uid})
        eq_(res.status_code, 201, res.content)
        eq_(json.loads(res.content)['first_name'], '..')
        obj = SellerPaypal.objects.get(pk=self.paypal.pk)
        eq_(obj.first_name, '..')

    @patch('lib.paypal.client.Client.get_personal_basic')
    @patch.object(settings, 'DEBUG', False)
    def test_email_differs(self, result):
        result.return_value = {'email': 'foo@bar.com'}
        res = self.client.post(self.get_list_url('personal-basic'),
                               data={'seller': self.uid})
        err = json.loads(res.content)
        eq_(err['error_code'], '100001')
        eq_(err['error_data'], {'email': 'foo@bar.com'})

    def test_email_differs_mock(self):
        with self.settings(PAYPAL_MOCK=True):
            res = self.client.post(self.get_list_url('personal-basic'),
                                   data={'seller': self.uid})
            eq_(json.loads(res.content)['email'], 'batman@gmail.com')

    @patch('lib.paypal.client.Client.get_personal_advanced')
    def test_advanced_data(self, result):
        result.return_value = {'phone': '..'}
        res = self.client.post(self.get_list_url('personal-advanced'),
                               data={'seller': self.uid})
        eq_(res.status_code, 201, res.content)
        eq_(json.loads(res.content)['phone'], '..')
        obj = SellerPaypal.objects.get(pk=self.paypal.pk)
        eq_(obj.phone, '..')


def test_header():
    eq_(escape('foo'), 'foo')
    eq_(escape('&'), '%26')
