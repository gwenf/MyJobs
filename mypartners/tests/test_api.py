import json

from django.core.urlresolvers import reverse

from mypartners.tests.test_views import MyPartnersTestCase
from mypartners.tests.factories import (OutreachEmailAddressFactory,
                                        OutreachRecordFactory)
from myjobs.tests.factories import UserFactory
from mypartners.models import OutreachEmailAddress


class NonUserOutreachTestCase(MyPartnersTestCase):
    """
        Tests related to the non user outreach single page app. These APIs
        provide data to the React-based application.
    """

    def setUp(self):
        super(NonUserOutreachTestCase, self).setUp()
        self.inbox = OutreachEmailAddressFactory(company=self.company)
        self.other_company_inbox = OutreachEmailAddressFactory()
        self.outreach_record = OutreachRecordFactory(outreach_email =
                                                     self.inbox)
        self.other_record = OutreachRecordFactory(outreach_email =
                                                  self.other_company_inbox)
        self.role.activities.add(*self.activities)

    def test_inbox_list_api(self):
        """
            Verify that the inbox list API will properly return any inboxes
            for the current company.
        """
        response = self.client.get(reverse('api_get_nuo_inbox_list'))
        self.assertEqual(response.status_code, 200, msg="expected status 200, "
                                                        "got %s, may be roles "
                                                        "or perms issue" %
                         response.status_code)
        response_json = json.loads(response.content)

        self.assertEqual(len(response_json), 1, msg="assert only user's "
                                                    "company's inbox returned")

        return_msg = "error loading inbox api, expected {0}, got {1}"
        self.assertEqual(response_json[0]["pk"], self.inbox.pk,
                         msg=return_msg.format(response_json[0]["pk"], self.inbox.pk))
        self.assertEqual(response_json[0]["fields"]["email"], self.inbox.email,
                         msg=return_msg.format(response_json[0]["fields"]["email"],
                                               self.inbox.email))

    def test_non_staff_cannot_use_view(self):
        """
            Temporary test. Ensure user cannot access this view if they are not
            staff. Remove when launching NonUserOutreach module.
        """
        non_staff_user = UserFactory(is_staff=False, email="testuser@test.com")
        self.client.login_user(non_staff_user)
        response = self.client.get(reverse('api_get_nuo_inbox_list'), follow=False)
        self.assertEqual(response.status_code, 404, msg="ensure NUO inboxes "
                                                        "returns 404 for non "
                                                        "staff users")

    def test_user_requires_prm_access(self):
        """
        Verify that the has_access("prm") decorator works properly.

        """
        response = self.client.get(reverse('api_get_nuo_inbox_list'))
        self.assertEqual(response.status_code, 200, msg="assert view loaded "
                                                        "properly for prm "
                                                        "access user")

        non_company_user = UserFactory(email="testuser@test.com")
        self.client.login_user(non_company_user)
        response = self.client.get(reverse('api_get_nuo_inbox_list'))
        self.assertEqual(response.status_code,
                         404,
                         msg="assert NUO inboxes returns 404 for a user that "
                             "is not a company user for a member company")

    def test_add_new_inbox(self):
        """Tests that a user can create a new outreach inbox."""

        response = self.client.post(reverse('api_add_nuo_inbox'),
                                    {"email": "testemail"})
        data = json.loads(response.content)
        inbox = OutreachEmailAddress.objects.last()
        self.assertEqual(inbox.pk, data["pk"],
                         "Was expecting an inbox to be created with a pk of "
                         "%s, but the latest one has a pk of %s." % (
                             inbox.pk, data["pk"]))

    def test_remove_inbox(self):
        """Tests that a user can delete an existing outreach inbox."""

        inbox = OutreachEmailAddressFactory(email="testemail")
        response = self.client.post(reverse('api_delete_nuo_inbox'),
                                    {'id': inbox.pk})
        data = json.loads(response.content)
        self.assertEqual(data["status"], "success")
        self.assertFalse(
            OutreachEmailAddress.objects.filter(pk=inbox.pk).exists(),
            "Inbox %s should have been deleted, but wasn't" % inbox.pk)

    def test_update_inbox(self):
        """Tests that an inbox can be updated through the api."""

        inbox = OutreachEmailAddressFactory(email="testemail")
        response = self.client.post(reverse('api_update_nuo_inbox'),
                                    {'id': inbox.pk, 'email': 'newemail'})
        data = json.loads(response.content)
        self.assertEqual(data["status"],  "success")
        self.assertEqual(OutreachEmailAddress.objects.get(pk=inbox.pk).email,
                         'newemail')

    def test_records_list_api(self):
        """
            Verify that the outreach records list API will properly return any
            records for the current company.
        """
        response = self.client.get(reverse('api_get_nuo_records_list'))
        self.assertEqual(response.status_code, 200, msg="expected status 200, "
                                                        "got %s, may be roles "
                                                        "or perms issue" %
                         response.status_code)
        response_json = json.loads(response.content)

        self.assertEqual(len(response_json), 1, msg="assert only user's "
                                                    "company's record returned")

        return_msg = "error loading records api, expected {0}, got {1}"
        self.assertEqual(response_json[0]["from_email"],
                         self.outreach_record.from_email,
                         msg=return_msg.format(response_json[0]["from_email"],
                                               self.outreach_record.from_email))
        self.assertEqual(response_json[0]["outreach_email"],
                         self.inbox.email + "@my.jobs",
                         msg=return_msg.format(response_json[0]["outreach_email"],
                                               self.inbox.email + "@my.jobs"))

    def test_individual_record_api(self):
        """
            Test the record API given the logged in user is a member of the same
            company.
        """
        # test to ensure current company's record will return
        response = self.client.get(reverse('api_get_individual_nuo_record'),
                                   {"record_id": self.outreach_record.pk})
        self.assertEqual(response.status_code, 200, msg="expected status 200, "
                                                        "got %s, may be roles "
                                                        "or perms issue" %
                                                        response.status_code)
        response_json = json.loads(response.content)

        self.assertNotEqual(response_json, {}, msg="empty object was returned,"
                                                   "record information was "
                                                   "expected.")

        return_msg = "error loading record information, expected {0}, got {1}"
        self.assertEqual(response_json["from_email"],
                         self.outreach_record.from_email,
                         msg=return_msg.format(response_json["from_email"],
                                               self.outreach_record.from_email))
        self.assertEqual(response_json["outreach_email"],
                         self.inbox.email + "@my.jobs",
                         msg=return_msg.format(response_json["outreach_email"],
                                               self.inbox.email + "@my.jobs"))

        # test to ensure other company's record will not return
        response = self.client.get(reverse('api_get_individual_nuo_record'),
                                   {"record_id": self.other_record.pk})

        response_json = json.loads(response.content)

        self.assertEqual(response_json, {}, msg="record information was "
                                                "returned for a non-company "
                                                "record.")
