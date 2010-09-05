# -*- coding: utf-8
from django.contrib.auth.models import User, Permission

from wiki import settings
import wiki.models as models
import shutil
import tempfile

import logging
logger = logging.getLogger("fnp.wiki.tests")

from django.utils import simplejson as json
from django.test import TestCase

class TestStorageBase(TestCase):
    def setUp(self):
        self.original_path = getattr(settings, "REPOSITORY_PATH", None)
        settings.REPOSITORY_PATH = tempfile.mkdtemp(prefix='nosetest_')
        self.storage = models.getstorage()

    def tearDown(self):
        shutil.rmtree(settings.REPOSITORY_PATH)
        settings.REPOSITORY_PATH = self.original_path

class TestDocumentStorage(TestStorageBase):

    def test_storage_empty(self):
        self.assertEqual(self.storage.all(), [])

    def test_get_text(self):
        self.storage.create_document(u"This is a test document.", u"TEST")
        response = self.client.get("/documents/TEST/text")
        self.assertEqual(response.status_code, 200, "Request failed with code %r" % response.status_code)
        result = json.loads(response.content)
        self.assertEqual(result["text"], "This is a test document.")
        self.assertEqual(result["revision"], 0)

    def test_change_text(self):
        self.storage.create_document(u"V1", u"TEST")

        # make some changes
        response = self.client.post("/documents/TEST/text", {
            "textsave-id": "TEST",
            "textsave-parent_revision": 0,
            "textsave-text": u"V2",
            "textsave-author_name": u"Łukasz",
            "textsave-author_email": u"lrekucki@gmail.com",
            "textsave-comment": u"New version"
        })
        self.assertEqual(response.status_code, 200, "Request failed with code %r" % response.status_code)
        result = json.loads(response.content)
        self.assertEqual(result["text"], u"V2")
        self.assertEqual(result["revision"], 1)


class TestTextRevert(TestStorageBase):

    def setUp(self):
        super(TestTextRevert, self).setUp()

        self.storage.create_document(u"V1", u"TEST")

        # make some changes
        self.client.post("/documents/TEST/text", {
            "textsave-id": "TEST",
            "textsave-parent_revision": 0,
            "textsave-text": u"Version #2",
            "textsave-comment": u"A commit."
        })

        self.client.post("/documents/TEST/text", {
            "textsave-id": "TEST",
            "textsave-parent_revision": 1,
            "textsave-text": u"Version #3",
            "textsave-comment": u"Another commit."
        })

        self.client.post("/documents/TEST/text", {
            "textsave-id": "TEST",
            "textsave-parent_revision": 2,
            "textsave-text": u"Verrrrsion #4",
            "textsave-comment": u"Commit in which someone messes up."
        })


    def test_anonymous(self):
        # start from scratch
        response = self.client.post("/documents/TEST/revert", {"target_revision": 0})

        # reverting requires login
        self.assertEqual(response.status_code, 403, "Request failed with code %r" % response.status_code)

    def test_logged_in(self):
        # login and try again
        User.objects.create_user("lrekucki", "lrekucki@gmail.com", "pass")
        self.assertTrue(self.client.login(username="lrekucki", password="pass"))

        response = self.client.post("/documents/TEST/revert", {"target_revision": 0})

        # reverting requires permissions
        self.assertEqual(response.status_code, 403, "Request failed with code %r" % response.status_code)

    def test_permitted(self):
        user = User.objects.create_user("lrekucki", "lrekucki@gmail.com", "pass")
        logger.info(u'\n'.join(unicode(x) for x in Permission.objects.all()))
        user.user_permissions.add(Permission.objects.get(codename="can_revert_changes"))

        self.assertTrue(self.client.login(username="lrekucki", password="pass"))

        response = self.client.post("/documents/TEST/revert", {"target_revision": 0})
        self.assertEqual(response.status_code, 200, "Request failed with code %r" % response.status_code)

        response = self.client.get("/documents/TEST/text")
        result = json.loads(response.content)
        self.assertEqual(result["text"], "V1")

        # revert produces a new commit
        self.assertEqual(result["revision"], 4)
