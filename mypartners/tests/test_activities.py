"""
These tests ensure that activity-level permissiosn are working properly.

Unlike the `myjobs.tests.test_views` module, this one is not concerned with
ensuring that views are behaving correctly in the general sense, but rather
that functionality that should be guarded by certain activities are only
available when those activities are present for a user.

As such, these tests assume that the settings.ENABLE_ROLES is True.
"""


from django.core.urlresolvers import reverse
from django.test.utils import override_settings

from myjobs.decorators import MissingActivity
from myjobs.tests.factories import (AppAccessFactory, RoleFactory, UserFactory,
                                    ActivityFactory)
from myjobs.tests.setup import MyJobsBase
from myjobs.tests.test_views import TestClient
from seo.tests.factories import CompanyFactory


@override_settings(ROLES_ENABLED=True)
class TestViewLevelActivities(MyJobsBase):
    """Test views wrapped with activities."""

    def setUp(self):
        super(TestViewLevelActivities, self).setUp()

        self.app_access = AppAccessFactory()
        self.activities = [
            ActivityFactory(name=activity, app_access=self.app_access)
            for activity in [
                "create communication record", "create contact",
                "create partner saved search", "create partner", "create tag",
                "delete tag", "delete partner", "read contact",
                "read communication record", "read partner saved search",
                "read partner", "read tag", "update communication record",
                "update contact", "update partner", "update tag"]]
        self.company = CompanyFactory(app_access=[self.app_access])
        # this role will be populated by activities on a test-by-test basis
        self.role = RoleFactory(company=self.company)
        self.user = UserFactory(roles=[self.role], is_staff=True)

        # login the user so that we don't get redirected to the login page
        self.client = TestClient()
        self.client.login_user(self.user)

    def assertRequires(self, view_name, *activities, **kwargs):
        """
        Asserst that the given view is only accessible when a user has a role
        with the given activities.
        """

        url = reverse(view_name, kwargs=kwargs.get('kwargs'))
        method = kwargs.get("method", "get").lower()

        response = getattr(self.client, method)(path=url)
        self.assertEqual(type(response), MissingActivity)

        self.role.activities = [activity for activity in self.activities
                                if activity.name in activities]

        response = getattr(self.client, method)(path=url)
        self.assertNotEqual(type(response), MissingActivity)

        self.role.activities.clear()

    def test_prm(self):
        """
        /prm/view requires "read partner".
        """

        self.assertRequires("prm", "read partner")

    def test_partner_library(self):
        """
        /prm/partner-library requires "create partner".
        """

        self.assertRequires("partner_library", "read partner")

    def test_create_partner_from_library(self):
        """
        /prm/view/partner-library/add requires "create partner".
        """

        self.assertRequires("create_partner_from_library", "create partner")

    def test_partner_overview(self):
        """
        /prm/view/overview requires "read partner".
        """

        self.assertRequires("partner_overview", "read partner")

    def test_partner_tagging(self):
        """
        /prm/view/tagging requires "create tag".
        """

        self.assertRequires("partner_tagging", "read tag")

    def test_edit_partner_tag(self):
        """
        /prm/view/tagging/edit requires "update tag".
        """

        self.assertRequires("edit_partner_tag", "update tag")

    def test_partner_details(self):
        """
        /prm/view/details requires "read partner"
        """

        self.assertRequires("partner_details", "update partner")

    def test_tag_color(self):
        """
        /prm/view/records/get-tag-color requires "read tag"
        """

        self.assertRequires("tag_color", "read tag")

    def test_tag_names(self):
        """
        /prm/view/records/get-tags requires "read tag"
        """

        self.assertRequires("tag_names", "read tag")

    def test_partner_get_records(self):
        """
        /prm/view/records/retrieve_records requires "read communication record"
        """

        self.assertRequires("partner_get_records", "read communication record")

    def test_report_view(self):
        """
        /prm/view/reports/details requires "read communication record"
        """

        self.assertRequires("report_view", "read communication record")

    def test_partner_records(self):
        """
        /prm/view/records requires "read communication record"
        """

        self.assertRequires("report_view", "read communication record")

    def test_partner_edit_record(self):
        """
        /prm/view/records/edit requires "create communication record" and
        "update communication record"
        """

        self.assertRequires(
            "partner_edit_record", "create communication record",
            "update communication record")

    def test_get_contact_information(self):
        """
        /prm/view/records/contact_info requires "read contact"
        """

        self.assertRequires("get_contact_information", "read contact")

    def test_record_view(self):
        """
        /prm/view/records/'details requires "read communication record"
        """

        self.assertRequires("record_view", "read communication record")

    def test_add_tags(self):
        """
        /prm/view/tagging/add requires "add tag"
        """

        self.assertRequires("add_tags", "create tag")

    def test_delete_partner_tag(self):
        """
        /prm/view/tagging/delete requires "delete tag"
        """

        self.assertRequires("delete_partner_tag", "delete tag")

    def test_create_partner(self):
        """
        /prm/view/edit requires "create partner"
        """

        self.assertRequires("create_partner", "create partner")

    def test_save_init_partner_form(self):
        """
        /prm/view/save requres "create partner"
        """

        self.assertRequires("save_init_partner_form", "create partner")

    def test_delete_prm_item(self):
        """
        /prm/view/details/delete requires "delete partner"
        """

        self.assertRequires("delete_prm_item", "delete partner")

    def test_save_item(self):
        """
        /prm/view/details/save requires "update partner"
        """

        self.assertRequires("save_item", "update partner")

    def test_edit_location(self):
        """
        /prm/view/locations/edit requires "update contact"
        """

        self.assertRequires("edit_location", "update contact")

    def test_delete_location(self):
        """
        /prm/view/locations/save requires "update contact"
        """

        self.assertRequires("edit_location", "update contact")

    def test_partner_searches(self):
        """
        /prm/view/searches requires "read partner saved searche
        """

        self.assertRequires("partner_searches", "read partner saved search")

    def test_partner_edit_search(self):
        """
        /prm/searches/edit requires "create partner saved search"
        """

        self.assertRequires(
            "partner_edit_search", "create partner saved search")

    def test_partner_get_referrals(self):
        """
        /prm/view/records/retreive_referrals requires
        "read communication record".
        """

        self.assertRequires(
            "partner_get_referrals", "read communication record")

    def test_get_records(self):
        """
        /prm/view/records/update requires "read communication record"
        """
        self.assertRequires(
            "get_records", "read communication record")

    def test_verify_contact(self):
        """
        /prm/view/searches/vierify-contact requires "read contact"
        """

        self.assertRequires("verify_contact", "read contact")

    def test_partner_savedsearch_save(self):
        """
        /prm/view/searches/save requires "create partner saved search"
        """

        self.assertRequires(
            "partner_savedsearch_save", "create partner saved search")

    def test_partner_view_full_feed(self):
        """
        /prm/view/searches/feed requires "read partner saved search"
        """

        self.assertRequires(
            "partner_view_full_feed", "read partner saved search")

    def test_partner_get_uploaded_file(self):
        """
        /prm/download requires "read communication record"
        """

        self.assertRequires("get_uploaded_file", "read communication record")

    def test_prm_report_records(self):
        """
        /prm/view/reports/details/records requires "read communication record"
        """

        self.assertRequires("prm_report_records", "read communication record")

    def test_manage_outreach_main(self):
        """
        /prm/view/nonuseroutreach requires "create contact",
        "create partner", and "create communication record"
        """

        self.assertRequires(
            "nuo_main", "create partner", "create contact",
            "create communication record")

    def test_process_email(self):
        """
        /prm/email requires "create partner", "create contact", and
        "create communication record"
        """

        self.assertRequires(
            "process_email", "create partner", "create contact",
            "create communication record")
