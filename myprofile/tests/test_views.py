from bs4 import BeautifulSoup
import json

from django.core.urlresolvers import reverse

from myjobs.tests.setup import MyJobsBase
from myjobs.tests.test_views import TestClient
from myjobs.tests.factories import UserFactory
from myprofile.tests.factories import AddressFactory, PrimaryNameFactory, \
    SummaryFactory
from myprofile.models import Name


class MyProfileViewsTests(MyJobsBase):
    def setUp(self):
        super(MyProfileViewsTests, self).setUp()
        self.client = TestClient()
        self.client.login_user(self.user)
        self.name = PrimaryNameFactory(user=self.user)

    def test_edit_profile(self):
        """
        Going to the edit_profile view generates a list of existing profile
        items in the main content section and a list of profile sections that
        don't have data filled out in the sidebar.
        """
        resp = self.client.get(reverse('view_profile'))
        soup = BeautifulSoup(resp.content)
        item_id = self.name.id

        # The existing name object should be rendered on the main content
        # section
        self.assertIsNotNone(soup.find('div',
                                       id='name-' + str(item_id) + '-item'))
        # profile-section contains the name of a profile section that has no
        # information filled out yet and shows up in the sidebar
        self.assertTrue(soup.findAll('tr', {'class': 'profile-section'}))

    def test_edit_summary(self):
        """
        See test_edit_profile
        """
        summary = SummaryFactory(user=self.user)
        resp = self.client.get(reverse('view_profile'))
        soup = BeautifulSoup(resp.content)

        item = soup.find('div', id='summary-' + str(summary.id) + '-item')
        self.assertIsNotNone(item)

        link = item.find('a').attrs['href']
        resp = self.client.get(link)
        self.assertEqual(resp.status_code, 200)

    def test_handle_form_get_new(self):
        """
        Invoking the handle_form view without an id parameter returns an
        empty form with the correct form id
        """

        resp = self.client.get(reverse('handle_form'),
                               data={'module': 'Name'})
        self.assertTemplateUsed(resp, 'myprofile/profile_form.html')
        soup = BeautifulSoup(resp.content)
        self.assertEquals(soup.form.attrs['id'], 'profile-unit-form')
        with self.assertRaises(KeyError):
            soup.find('input', id='id_name-given_name').attrs['value']

    def test_handle_form_get_existing(self):
        """
        Invoking the handle_form view with and id paraemeter returns
        a form filled out with the corresponding profile/ID combination
        """

        resp = self.client.get(reverse('handle_form'),
                               data={'module': 'Name', 'id': self.name.id})
        self.assertTemplateUsed(resp, 'myprofile/profile_form.html')
        soup = BeautifulSoup(resp.content)
        self.assertEquals(soup.form.attrs['id'], 'profile-unit-form')
        self.assertEquals(soup.find('input', id='id_name-given_name')
                          .attrs['value'], 'Alice')
        self.assertEquals(soup.find('input', id='id_name-family_name')
                          .attrs['value'], 'Smith')
        self.assertEquals(soup.find('input', id='id_name-primary')
                          .attrs['checked'], 'checked')

    def test_handle_form_post_new_valid(self):
        """
        Invoking the handle_form view as a POST request for a new item
        creates that object in the database and returns the item snippet
        to be rendered on the page.
        """

        resp = self.client.post(reverse('handle_form'),
                                data={'module': 'Name', 'id': 'new',
                                      'given_name': 'Susy',
                                      'family_name': 'Smith'})
        self.assertRedirects(resp, reverse('view_profile'))
        self.assertEqual(Name.objects.filter(given_name='Susy',
                                             family_name='Smith').count(), 1)

    def test_handle_form_post_invalid(self):
        """
        Invoking the handle_form view as a POST request with an invalid
        form returns the list of form errors.
        """
        resp = self.client.post(reverse('handle_form'),
                                data={'module': 'Name', 'id': 'new',
                                      'given_name': 'Susy'},
                                HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        self.assertEqual(json.loads(resp.content),
                         {u'family_name': [u'This field is required.']})

    def test_handle_form_post_existing_valid(self):
        """
        Invoking the handle_form view as a POST request for an existing
        item updates that item and returns the update item snippet.
        """
        resp = self.client.post(reverse('handle_form'),
                                data={'module': 'Name', 'id': self.name.id,
                                      'given_name': 'Susy',
                                      'family_name': 'Smith'})
        self.assertRedirects(resp, reverse('view_profile'))
        self.assertEqual(Name.objects.filter(given_name='Susy',
                                             family_name='Smith').count(), 1)

    def test_handle_form_json_serialize_get(self):
        """When an ajax requests wants to GET json, serialize the form."""
        resp = self.client.get(reverse('handle_form'),
                               HTTP_ACCEPT='application/json',
                               data={'module': 'Name'})
        self.assertEquals(200, resp.status_code)
        self.assertIn('application/json', resp['content-type'])
        data = json.loads(resp.content)
        self.assertEquals(3, len(data['ordered_fields']))
        self.assertIsInstance(data['ordered_fields'], list)
        self.assertEquals(3, len(data['fields']))
        self.assertIsInstance(data['fields'], dict)
        self.assertIsInstance(data['fields']['family_name'], dict)
        self.assertIsInstance(data['fields']['given_name'], dict)
        self.assertIsInstance(data['fields']['primary'], dict)
        self.assertEquals(3, len(data['data']))
        self.assertIsInstance(data['data'], dict)

    def test_handle_form_redirect_summary(self):
        """
        When a user has a summary already if they try to make a new summary
        handle form should redirect the user to edit the summary they already
        have. User is only allowed one summary per account.
        """
        summary_instance = SummaryFactory(user=self.user)
        summary_instance.save()
        resp = self.client.get(reverse('handle_form'),
                               data={'module': 'Summary'})
        self.assertRedirects(resp, reverse(
            'handle_form')+'?id=%s&module=Summary' % summary_instance.id)

    def test_delete_item(self):
        """
        Invoking the delete_item view deletes the item and returns
        the 'Deleted!' HttpResponse
        """

        resp = self.client.post(reverse('delete_item')+'?item='+str(self.name.id))

        self.assertEqual(resp.content, '')
        self.assertEqual(Name.objects.filter(id=self.name.id).count(), 0)

    def test_add_duplicate_primary_email(self):
        """
        Attempting to add a secondary email with a value equal to the user's
        current primary email results in an error.

        Due to how the instance is constructed, this validation is form-level
        rather than model-level.
        """
        resp = self.client.post(reverse('handle_form'),
                                data={'module': 'SecondaryEmail',
                                      'id': 'new',
                                      'email': self.user.email},
                                HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(json.loads(resp.content),
                         {u'email': [u'This email is already registered.']})

    def test_default_country_changes(self):
        """
        The displayed country when editing an address should update to reflect
        the chosen country.
        """
        resp = self.client.get(reverse('handle_form'),
                               data={'module': 'Address'})
        content = BeautifulSoup(resp.content)

        selected = content.find('option', attrs={'selected': True})
        self.assertEqual(selected.attrs['value'], 'USA')

        address = AddressFactory(user=self.user, country_code='AFG')

        resp = self.client.get(reverse('handle_form'),
                               data={'module': 'Address',
                                     'id': address.id})
        content = BeautifulSoup(resp.content)
        selected = content.find('option', attrs={'selected': True})
        self.assertEqual(selected.attrs['value'], 'AFG')
