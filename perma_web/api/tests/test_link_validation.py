import os
import requests
from .utils import TEST_ASSETS_DIR, ApiResourceTestCase, ApiResourceTransactionTestCase, ApiResourceLiveServerTestCase
from perma.models import Link, LinkUser
from django.test.utils import override_settings


class LinkValidationMixin():

    resource_url = '/archives'
    rejected_status_code = 400  # Bad Request

    fixtures = ['fixtures/users.json',
                'fixtures/folders.json',
                'fixtures/api_keys.json',
                'fixtures/archive.json']

    def setUp(self):
        super(LinkValidationMixin, self).setUp()

        self.admin_user = LinkUser.objects.get(pk=1)
        self.org_user = LinkUser.objects.get(pk=3)

        self.link = Link.objects.get(pk="3SLN-JHX9")
        self.unrelated_link = Link.objects.get(pk="7CF8-SS4G")

        self.unrelated_url = "{0}{1}/".format(self.list_url, self.unrelated_link.pk)


class LinkValidationTestCase(LinkValidationMixin, ApiResourceTestCase):

    ########
    # URLs #
    ########
    def test_should_fail_gracefully_if_passed_long_unicode(self):
        '''
            See https://github.com/harvard-lil/perma/issues/1841
            The unicode chars -> ☃
        '''
        u = b"This is a block of text that contains 64 or more characters, including one or more unicode characters like \xe2\x98\x83"

        self.rejected_post(self.list_url,
                           user=self.org_user,
                           data={'url': u})

    def test_should_reject_malformed_url1(self):
        self.rejected_post(self.list_url,
                           user=self.org_user,
                           data={'url': 'httpexamplecom'})

    def test_should_reject_malformed_url2(self):
        self.rejected_post(self.list_url,
                           user=self.org_user,
                           data={'url': '[http://example.com'})

    def test_should_reject_malformed_url3(self):
        self.rejected_post(self.list_url,
                           user=self.org_user,
                           data={'url': ']http://example.com'})

    def test_should_reject_bad_unicode_url(self):
        self.rejected_post(self.list_url,
                           user=self.org_user,
                           data={'url': 'https://www.ntanet.org/some-article.pdf\x00'})

    @override_settings(RESOURCE_LOAD_TIMEOUT=0.25) # only wait 1/4 second before giving up
    def test_should_reject_unresolvable_domain_url(self):
        self.rejected_post(self.list_url,
                           user=self.org_user,
                           data={'url': 'http://this-is-not-a-functioning-url.com'})

    def test_should_reject_unloadable_url(self):
        self.rejected_post(self.list_url,
                           user=self.org_user,
                           # https://stackoverflow.com/a/10456065/4074877
                           data={'url': 'http://198.51.100.1/'})

    def test_should_reject_invalid_folder_id(self):
        self.rejected_post(self.list_url,
                           user=self.org_user,
                           data={'url': 'http://example.com',
                                 'folder': 'not-an-integer'})


class LinkValidationTransactionTestCase(LinkValidationMixin, ApiResourceTransactionTestCase):

    serve_files = ['target_capture_files/test.html',
                   'target_capture_files/test.jpg']

    ########
    # URLs #
    ########

    @override_settings(BANNED_IP_RANGES=["127.0.0.0/8"])
    def test_should_reject_invalid_ip(self):
        resp = self.rejected_post(self.list_url,
                                  user=self.org_user,
                                  data={'url': "http://127.0.0.0"})
        self.assertIn(b"Not a valid IP", resp.content)

    @override_settings(MAX_ARCHIVE_FILE_SIZE=1024)
    def test_should_reject_large_url(self):
        self.rejected_post(self.list_url,
                           user=self.org_user,
                           data={'url': self.server_url + '/test.jpg'})

    #########
    # Files #
    #########

    def test_should_reject_invalid_file_format(self):
        with open(os.path.join(TEST_ASSETS_DIR, 'target_capture_files', 'test.html'), 'rb') as test_file:
            self.rejected_post(self.list_url,
                               format='multipart',
                               user=self.org_user,
                               data={'url': self.server_url + '/test.html',
                                     'file': test_file})

    @override_settings(MAX_ARCHIVE_FILE_SIZE=1024)
    def test_should_reject_large_file(self):
        with open(os.path.join(TEST_ASSETS_DIR, 'target_capture_files', 'test.jpg'), 'rb') as test_file:
            self.rejected_post(self.list_url,
                               format='multipart',
                               user=self.org_user,
                               data={'url': self.server_url + '/test.html',
                                     'file': test_file})


@override_settings(SECURE_SSL_REDIRECT=False)
class LinkValidationLiveTestCase(LinkValidationMixin, ApiResourceLiveServerTestCase):

    def test_should_reject_file_redirecting_url_without_exception(self):

        domain = f"http://perma.test:{self.live_server_url.split(':')[-1]}"
        url = f'{domain}/api/tests/redirect-to-file'

        # verify that the test route redirects as expected
        redirects = self.client.get(url)
        self.assertEqual(redirects.status_code, 301)
        self.assertRegex(redirects.url, r'^file:///')

        # verify that requests raises the exception we expect, when loading it
        with self.assertRaises(requests.exceptions.InvalidSchema):
            requests.get(url)

        # verify that the capture request does not raise an exception, but
        # rather, returns BadRequest
        resp = self.rejected_post(self.list_url,
                           user=self.org_user,
                           data={'url': url},
                           expected_status_code=400,
                           expected_data={})
        self.assertIn(b"Couldn't load URL", resp.content)
