from django.core import mail
from django.core.exceptions import MultipleObjectsReturned
from django.core.urlresolvers import reverse
from django.db import IntegrityError
from django.middleware.transaction import transaction

from myjobs.tests.setup import MyJobsBase
from myjobs.models import User
from myjobs.tests.factories import UserFactory
from myprofile.models import ProfileUnits, Name, SecondaryEmail, Education, \
    Address, Telephone, EmploymentHistory, MilitaryService, Website, License, \
    Summary, VolunteerHistory
from myprofile.tests.factories import PrimaryNameFactory, \
    NewPrimaryNameFactory, SecondaryEmailFactory, NewNameFactory, \
    MilitaryServiceFactory, LicenseFactory, WebsiteFactory, SummaryFactory, \
    VolunteerHistoryFactory
from registration.models import ActivationProfile
from datetime import date


class MyProfileTests(MyJobsBase):
    user_info = {'password1': 'complicated_password',
                 'email': 'alice@example.com'}

    def setUp(self):
        super(MyProfileTests, self).setUp()
        self.user = UserFactory()

    def test_primary_name_save(self):
        """
        Saving a primary name when one already exists replaces it with
        the new primary name.
        """

        initial_name = PrimaryNameFactory(user=self.user)

        self.assertTrue(initial_name.primary)
        new_name = NewPrimaryNameFactory(user=self.user)
        initial_name = Name.objects.get(given_name='Alice')
        self.assertTrue(new_name.primary)
        self.assertFalse(initial_name.primary)

    def test_primary_name_save_multiuser(self):
        """
        Saving primary names when multiple users are present accurately
        sets and retrieves the correct name
        """
        self.user_2 = UserFactory(email='foo@example.com')
        user_2_initial_name = PrimaryNameFactory(user=self.user_2)
        user_2_new_name = NewPrimaryNameFactory(user=self.user_2)

        initial_name = PrimaryNameFactory(user=self.user)
        new_name = NewPrimaryNameFactory(user=self.user)

        user_2_initial_name = Name.objects.get(given_name='Alice',
                                               user=self.user_2)
        user_2_new_name = Name.objects.get(given_name='Alicia',
                                           user=self.user_2)
        initial_name = Name.objects.get(given_name='Alice', user=self.user)

        self.assertTrue(new_name.primary)
        self.assertFalse(initial_name.primary)
        self.assertTrue(user_2_new_name.primary)
        self.assertFalse(user_2_initial_name.primary)

        with self.assertRaises(MultipleObjectsReturned):
            Name.objects.get(primary=True)
            Name.objects.get(primary=False)
            Name.objects.get(given_name='Alice')
            Name.objects.get(given_name='Alicia')
        Name.objects.get(primary=True, user=self.user_2)

    def test_email_activation_creation(self):
        """
        Creating a new secondary email creates a corresponding unactivated
        ActivationProfile.
        """

        secondary_email = SecondaryEmailFactory(user=self.user)
        activation = ActivationProfile.objects.get(email=secondary_email.email)
        self.assertEqual(secondary_email.email, activation.email)

    def test_send_activation(self):
        """
        The send_activation method in SecondaryEmail should send an
        activation link to the email address
        """

        secondary_email = SecondaryEmailFactory(user=self.user)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [secondary_email.email])
        self.assertTrue('secondary email' in mail.outbox[0].body)

    def test_verify(self):
        """
        Clicking the activation link sets the ActivationProfile object to
        activated and sets the SecondaryEmail object to verified.
        """

        secondary_email = SecondaryEmailFactory(user=self.user)
        activation = ActivationProfile.objects.get(user=self.user,
                                                   email=secondary_email.email)
        response = self.client.get(reverse('registration_activate',
                                           args=[activation.activation_key]) +
                                   '?verify=%s' % self.user.user_guid)
        secondary_email = SecondaryEmail.objects.get(user=self.user,
                                                     email=secondary_email.email)
        activation = ActivationProfile.objects.get(user=self.user,
                                                   email=secondary_email.email)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(secondary_email.verified)

    def test_set_primary_email(self):
        """
        Calling the set_as_primary method in the SecondaryEmail removes it from
        SecondaryEmail, replaces the current address on the User model, and
        adds the replaced address to the SecondaryEmail table.

        """
        old_primary = self.user.email
        secondary_email = SecondaryEmailFactory(user=self.user)
        new_primary = secondary_email.email

        for email in [old_primary, new_primary]:
            # Emails must be verified to make them primary.
            activation = ActivationProfile.objects.get_or_create(user=self.user,
                                                                 email=email)[0]
            ActivationProfile.objects.activate_user(activation.activation_key)

        secondary_email = SecondaryEmail.objects.get(email=new_primary)
        secondary_email.set_as_primary()

        with self.assertRaises(SecondaryEmail.DoesNotExist):
            SecondaryEmail.objects.get(email=new_primary)
        old_email = SecondaryEmail.objects.get(email=old_primary)
        self.assertTrue(old_email.verified)
        user = User.objects.get(email=new_primary)

    def test_duplicate_same_primary_name(self):
        """
        Makes sure that one can not create duplicate primary names.
        """
        primary_name1 = PrimaryNameFactory(user=self.user)
        primary_name2 = PrimaryNameFactory(user=self.user)

        num_results = self.user.profileunits_set.filter(
            content_type__model='name').count()
        self.assertEqual(num_results, 1)

    def test_different_primary_name(self):
        primary_name1 = PrimaryNameFactory(user=self.user)
        primary_name2 = NewPrimaryNameFactory(user=self.user)

        primary_name_count = Name.objects.filter(user=self.user,
                                                 primary=True).count()
        non_primary_name_count = Name.objects.filter(user=self.user,
                                                     primary=False).count()

        self.assertEqual(primary_name_count, 1)
        self.assertEqual(non_primary_name_count, 1)

    def test_non_primary_name_to_primary(self):
        name = NewNameFactory(user=self.user)
        primary_name1 = PrimaryNameFactory(user=self.user)

        primary_name_count = Name.objects.filter(user=self.user,
                                                 primary=True).count()
        non_primary_name_count = Name.objects.filter(user=self.user,
                                                     primary=False).count()

        self.assertEqual(primary_name_count, 1)
        self.assertEqual(non_primary_name_count, 0)

    def test_primary_name_to_non_primary(self):
        primary_name = PrimaryNameFactory(user=self.user)
        primary_name.primary = False
        primary_name.save()

        primary_name_count = Name.objects.filter(user=self.user,
                                                 primary=True).count()
        non_primary_name_count = Name.objects.filter(user=self.user,
                                                     primary=False).count()

        self.assertEqual(primary_name_count, 0)
        self.assertEqual(non_primary_name_count, 1)

    def test_duplicate_name(self):
        """
        Makes sure that duplicate names is not saving.
        """
        name1 = NewNameFactory(user=self.user)
        name2 = NewNameFactory(user=self.user)

        num_results = Name.objects.filter(user=self.user).count()
        self.assertEqual(num_results, 1)

    def test_unverified_primary_email(self):
        """
        Only verified emails can be set as the primary email
        """

        old_primary = self.user.email
        secondary_email = SecondaryEmailFactory(user=self.user)
        primary = secondary_email.set_as_primary()

        with self.assertRaises(SecondaryEmail.DoesNotExist):
            SecondaryEmail.objects.get(email=old_primary)
        self.assertFalse(primary)
        user = User.objects.get(email=old_primary)
        self.assertEqual(user.email, old_primary)

    def test_maintain_verification_state(self):
        """
        For security reasons, the state of verification of the user email
        should be the same as it is when it is transferred into SecondaryEmail
        """

        old_primary = self.user.email
        self.user.is_active = False
        self.user.save()
        secondary_email = SecondaryEmailFactory(user=self.user)
        activation = ActivationProfile.objects.get(user=self.user,
                                                   email=secondary_email.email)
        ActivationProfile.objects.activate_user(activation.activation_key)
        secondary_email = SecondaryEmail.objects.get(user=self.user,
                                                     email=secondary_email.email)
        new_primary = secondary_email.email
        secondary_email.set_as_primary()

        old_email = SecondaryEmail.objects.get(email=old_primary)
        self.assertFalse(old_email.verified)
        user = User.objects.get(email=new_primary)

    def test_same_secondary_email(self):
        """
        All emails are unique. If an email is used as a user's primary email or
        another secondary email, it may not be used as a secondary email again.
        """
        secondary_email = SecondaryEmailFactory(user=self.user)
        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                new_secondary_email = SecondaryEmailFactory(user=self.user)
        new_secondary_email = SecondaryEmailFactory(user=self.user,
                                                    email='email@example.com')

    def test_delete_secondary_email(self):
        """
        Deleting a secondary email should also delete its activation profile
        """
        self.assertEqual(ActivationProfile.objects.count(), 0)
        secondary_email = SecondaryEmailFactory(user=self.user)
        self.assertEqual(ActivationProfile.objects.count(), 1)
        secondary_email.delete()
        self.assertEqual(ActivationProfile.objects.count(), 0)

    def test_add_military_service(self):
        military_service = MilitaryServiceFactory(user=self.user)
        military_service.save()

        ms_object = ProfileUnits.objects.filter(
            content_type__model="military service").count()
        self.assertEqual(ms_object, 1)

    def test_add_license(self):
        license_form = LicenseFactory(user=self.user)
        license_form.save()

        ms_object = ProfileUnits.objects.filter(
            content_type__model="license").count()
        self.assertEqual(ms_object, 1)

    def test_add_website(self):
        website_instance = WebsiteFactory(user=self.user)
        website_instance.save()

        ms_object = ProfileUnits.objects.filter(
            content_type__model="website").count()
        self.assertEqual(ms_object, 1)

    def test_add_summary(self):
        summary_instance = SummaryFactory(user=self.user)
        summary_instance.save()

        ms_object = ProfileUnits.objects.filter(
            content_type__model="summary").count()
        self.assertEqual(ms_object, 1)

    def test_add_volunteer_history(self):
        vh_instance = VolunteerHistoryFactory(user=self.user)
        vh_instance.save()

        ms_object = ProfileUnits.objects.filter(
            content_type__model="volunteer history").count()
        self.assertEqual(ms_object, 1)


class ProfileSuggestionTests(MyJobsBase):
    user_info = {'password1': 'complicated_password',
                 'email': 'alice@example.com'}

    def setUp(self):
        super(ProfileSuggestionTests, self).setUp()

        self.maxDiff = None
        self.user = UserFactory()

    def test_suggestion_when_name_blank(self):
        suggestions = Name.get_suggestion(self.user)

        self.assertEqual(len(suggestions), 1)
        suggestion = suggestions[0]
        self.assertEqual(suggestion['msg'], "Please add your name.")
        self.assertEqual(suggestion['priority'], 5)

    def test_suggestion_when_name_provided(self):
        Name.objects.create(user=self.user,
                            given_name="First name",
                            family_name="Last name")
        suggestions = Name.get_suggestion(self.user)

        self.assertEqual(len(suggestions), 0)

    def test_suggestion_when_education_blank(self):
        expected = [{
                    'priority': 5,
                    'msg': 'Would you like to provide information' +
                                   ' about your education?',
                    'url': reverse('handle_form') + '?module=Education&id=new',
                    'module': 'Education'}]
        actual = Education.get_suggestion(self.user)

        # Sort lists to ensure indentical order
        self.assertEqual(actual, expected)

    def test_suggestion_when_education_entered(self):
        Education.objects.create(organization_name="Org",
                                 degree_date=date.today(),
                                 education_level_code=3,
                                 degree_major="Gen Ed",
                                 user=self.user)
        expected = []
        actual = Education.get_suggestion(self.user)

        self.assertEqual(actual, expected)

    def test_suggestion_when_address_blank(self):

        suggestions = Address.get_suggestion(self.user)

        self.assertEqual(len(suggestions), 1)
        suggestion = suggestions[0]
        self.assertEqual(suggestion['msg'],
                         "Would you like to provide your address?")
        self.assertEqual(suggestion['priority'], 5)

    def test_suggestion_when_address_provided(self):
        Address.objects.create(user=self.user,
                               address_line_one="12345 Test Ave")
        suggestions = Address.get_suggestion(self.user)

        self.assertEqual(len(suggestions), 1)
        suggestion = suggestions[0]
        self.assertEqual(suggestion['msg'],
                         "Do you need to update your address from 12345 Test" +
                         " Ave?")
        self.assertEqual(suggestion['priority'], 1)

    def test_suggestion_when_phone_blank(self):
        expected = [{'msg': 'Would you like to add a telephone?',
                    'priority': 5,
                    'module': 'Telephone',
                    'url': reverse('handle_form') + '?module=Telephone&id=new'
                    }]

        actual = Telephone.get_suggestion(self.user)

        # Sort lists to ensure identical order
        self.assertEqual(actual, expected)

    def test_suggestion_when_phone_entered(self):
        phone = Telephone(user=self.user)
        phone.use_code = 'mobile'
        phone.save()

        # Get the actual results
        actual = Telephone.get_suggestion(self.user)

        self.assertEqual(actual, [])

    def test_suggestion_when_never_employed(self):
        suggestions = EmploymentHistory.get_suggestion(self.user)

        self.assertEqual(len(suggestions), 1)
        suggestion = suggestions[0]
        self.assertEqual(suggestion['msg'],
                         "Would you like to add your employment history?")
        self.assertEqual(suggestion['priority'], 5)

    def test_suggestion_when_currently_employed(self):
        EmploymentHistory.objects.create(user=self.user,
                                         position_title="Title",
                                         organization_name="Organization",
                                         start_date=date.today(),
                                         current_indicator=True)
        suggestions = EmploymentHistory.get_suggestion(self.user)

        self.assertEqual(len(suggestions), 1)
        suggestion = suggestions[0]
        self.assertEqual(suggestion['msg'],
                         "Are you still employed with Organization?")
        self.assertEqual(suggestion['priority'], 0)

    def test_suggestion_when_no_employer_is_marked_current(self):
        EmploymentHistory.objects.create(user=self.user,
                                         position_title="Title",
                                         organization_name="Organization",
                                         start_date=date.today())
        suggestions = EmploymentHistory.get_suggestion(self.user)

        self.assertEqual(len(suggestions), 1)
        suggestion = suggestions[0]
        self.assertEqual(suggestion['msg'],
                         "Have you worked anywhere since being employed" +
                            " with Organization?")
        self.assertEqual(suggestion['priority'], 1)

    def test_suggestion_when_secondary_email_provided(self):
        SecondaryEmail.objects.create(user=self.user,
                                      email="test@test.com")
        suggestions = SecondaryEmail.get_suggestion(self.user)

        self.assertEqual(len(suggestions), 0)

    def test_suggestion_when_military_service_blank(self):
        suggestions = MilitaryService.get_suggestion(self.user)

        self.assertEqual(len(suggestions), 1)
        suggestion = suggestions[0]
        self.assertEqual(suggestion['msg'],
                         "Have you served in the armed forces?")
        self.assertEqual(suggestion['priority'], 3)

    def test_suggestion_when_military_service_provided(self):
        MilitaryService.objects.create(user=self.user,
                                       branch="Army")
        suggestions = MilitaryService.get_suggestion(self.user)

        self.assertEqual(len(suggestions), 0)

    def test_suggestion_when_website_blank(self):
        suggestions = Website.get_suggestion(self.user)

        self.assertEqual(len(suggestions), 1)
        suggestion = suggestions[0]
        self.assertEqual(suggestion['msg'],
                         "Do you have a personal website or online portfolio?")
        self.assertEqual(suggestion['priority'], 3)

    def test_suggestion_when_website_provided(self):
        Website.objects.create(user=self.user,
                               uri='http://example.com')
        suggestions = Website.get_suggestion(self.user)

        self.assertEqual(len(suggestions), 0)

    def test_suggestion_when_license_blank(self):
        suggestions = License.get_suggestion(self.user)

        self.assertEqual(len(suggestions), 1)
        suggestion = suggestions[0]
        self.assertEqual(suggestion['msg'],
                         'Would you like to add and professional licenses or' +
                         ' certifications?')
        self.assertEqual(suggestion['priority'], 3)

    def test_suggestion_when_license_provided(self):
        License.objects.create(user=self.user,
                               license_name="Name",
                               license_type="Type")
        suggestions = License.get_suggestion(self.user)

        self.assertEqual(len(suggestions), 0)

    def test_suggestion_when_summary_blank(self):
        suggestions = Summary.get_suggestion(self.user)

        self.assertEqual(len(suggestions), 1)
        suggestion = suggestions[0]
        self.assertEqual(suggestion['msg'],
                         "Would you like to add a summary of your career?")
        self.assertEqual(suggestion['priority'], 5)

    def test_suggestion_when_summary_provided(self):
        Summary.objects.create(user=self.user,
                               headline="Headline")
        suggestions = Summary.get_suggestion(self.user)

        self.assertEqual(len(suggestions), 0)

    def test_suggestion_when_volunteer_history_blank(self):
        suggestions = VolunteerHistory.get_suggestion(self.user)

        self.assertEqual(len(suggestions), 1)
        suggestion = suggestions[0]
        self.assertEqual(suggestion['msg'],
                         "Do you have any relevant volunteer experience you" +
                          " would like to include?")
        self.assertEqual(suggestion['priority'], 3)

    def test_suggestion_when_volunteer_history_provided(self):
        VolunteerHistory.objects.create(user=self.user,
                                        position_title="Title",
                                        organization_name="Organization",
                                        start_date=date.today())
        suggestions = VolunteerHistory.get_suggestion(self.user)

        self.assertEqual(len(suggestions), 0)
