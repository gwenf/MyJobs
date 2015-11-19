from datetime import datetime

from unittest import TestCase

from myreports.datasources import (
    ContactsDataSource, ContactsFilter, ContactsDataSourceJsonDriver)
from myreports.report_configuration import (
    ReportConfiguration, ColumnConfiguration)

from myjobs.tests.setup import MyJobsBase
from myjobs.tests.factories import UserFactory
from mydashboard.tests.factories import CompanyFactory
from mypartners.tests.factories import (
    PartnerFactory, ContactFactory, LocationFactory, TagFactory)
from mypartners.models import Status


class TestContactsDataSource(MyJobsBase):
    def setUp(self):
        super(TestContactsDataSource, self).setUp()

        self.company = CompanyFactory(name='right')
        self.company.save()
        self.other_company = CompanyFactory(name='wrong')
        self.other_company.save()

        self.partner = PartnerFactory(
            owner=self.company)
        self.other_partner = PartnerFactory(
            owner=self.other_company)

        self.partner_a = PartnerFactory(owner=self.company, name="aaa")
        self.partner_b = PartnerFactory(owner=self.company, name="bbb")
        self.partner_unapp = PartnerFactory(
            owner=self.company,
            name="unapproved",
            approval_status__code=Status.UNPROCESSED)
        self.partner_archived = PartnerFactory(owner=self.company)

        self.east_tag = TagFactory.create(name='east')
        self.west_tag = TagFactory.create(name='west')
        self.bad_tag = TagFactory.create(name='bad')

        self.john_user = UserFactory(email="john@user.com")
        self.john = ContactFactory(
            partner=self.partner_a,
            name='john adams',
            user=self.john_user,
            email="john@user.com",
            last_action_time='2015-10-03')
        self.john.locations.add(
            LocationFactory.create(
                city="Indianapolis",
                state="IN"))
        self.john.locations.add(
            LocationFactory.create(
                city="Chicago",
                state="IL"))
        self.john.tags.add(self.east_tag)

        self.sue_user = UserFactory(email="sue@user.com")
        self.sue = ContactFactory(
            partner=self.partner_b,
            name='Sue Baxter',
            user=self.sue_user,
            email="sue@user.com",
            last_action_time='2015-09-30 13:23')
        self.sue.locations.add(
            LocationFactory.create(
                address_line_one="123",
                city="Los Angeles",
                state="CA"))
        self.sue.locations.add(
            LocationFactory.create(
                address_line_one="234",
                city="Los Angeles",
                state="CA"))
        self.sue.tags.add(self.west_tag)

        self.archived_partner_user = (
            UserFactory(email="archived_partner@user.com"))
        self.archived_partner = ContactFactory(
            partner=self.partner_archived,
            name='Archived Partner Contact',
            user=self.archived_partner_user,
            email="archived_partner@user.com",
            last_action_time='2015-09-30 13:23')
        self.archived_partner.locations.add(
            LocationFactory.create(
                address_line_one="123",
                city="Nowhere",
                state="NO"))
        self.archived_partner.locations.add(
            LocationFactory.create(
                address_line_one="234",
                city="Nowhere",
                state="NO"))
        self.archived_partner.tags.add(self.west_tag)

        self.archived_contact_user = (
            UserFactory(email="archived_contact@user.com"))
        self.archived_contact = ContactFactory(
            partner=self.partner_b,
            name='Archived Contact',
            user=self.archived_contact_user,
            email="archived_contact@user.com",
            last_action_time='2015-09-30 13:23')
        self.archived_contact.locations.add(
            LocationFactory.create(
                address_line_one="123",
                city="Nowhere",
                state="NO"))
        self.archived_contact.locations.add(
            LocationFactory.create(
                address_line_one="234",
                city="Nowhere",
                state="NO"))
        self.archived_contact.tags.add(self.west_tag)

        self.unapproved_partner_user = (
            UserFactory(email="unapproved_partner@user.com"))
        self.unapproved_partner_contact = ContactFactory(
            partner=self.partner_unapp,
            name='Unapproved Partner Contact',
            user=self.unapproved_partner_user,
            email="unapproved_partner@user.com",
            last_action_time='2015-09-30 13:23')
        self.unapproved_partner_contact.locations.add(
            LocationFactory.create(
                address_line_one="123",
                city="Nowhere",
                state="NO"))
        self.unapproved_partner_contact.locations.add(
            LocationFactory.create(
                address_line_one="234",
                city="Nowhere",
                state="NO"))
        self.unapproved_partner_contact.tags.add(self.west_tag)

        self.unapproved_contact_user = (
            UserFactory(email="unapproved_contact@user.com"))
        self.unapproved_contact = ContactFactory(
            partner=self.partner_b,
            name='Unapproved Contact',
            user=self.unapproved_contact_user,
            email="unapproved_contact@user.com",
            last_action_time='2015-09-30 13:23',
            approval_status__code=Status.UNPROCESSED)
        self.unapproved_contact.locations.add(
            LocationFactory.create(
                address_line_one="123",
                city="Nowhere",
                state="NO"))
        self.unapproved_contact.locations.add(
            LocationFactory.create(
                address_line_one="234",
                city="Nowhere",
                state="NO"))
        self.unapproved_contact.tags.add(self.west_tag)

        self.wrong_user = UserFactory(email="wrong@user.com")
        self.wrong = ContactFactory(
            partner=self.other_partner,
            name='wrong person',
            user=self.wrong_user,
            email="wrong@user.com",
            last_action_time='2015-09-03')
        self.wrong.locations.add(
            LocationFactory.create(
                city="Los Angeles",
                state="CA"))
        self.wrong.tags.add(self.east_tag)
        self.wrong.tags.add(self.west_tag)
        self.wrong.tags.add(self.bad_tag)

        self.partner_archived.archive()
        self.archived_contact.archive()

    def test_run_unfiltered(self):
        """Should reject contact from another company."""
        ds = ContactsDataSource()
        recs = ds.run(self.company, ContactsFilter(), [])
        names = set([r['name'] for r in recs])
        expected = {self.sue.name, self.john.name}
        self.assertEqual(expected, names)

    def test_filter_by_date_range(self):
        """Should show only contact with last_action_time in range."""
        ds = ContactsDataSource()
        recs = ds.run(
            self.company,
            ContactsFilter(
                date=[datetime(2015, 9, 1), datetime(2015, 9, 30)]),
            [])
        names = set([r['name'] for r in recs])
        expected = {self.sue.name}
        self.assertEqual(expected, names)

    def test_filter_by_date_before(self):
        """Should show only contact with last_action_time before date."""
        ds = ContactsDataSource()
        recs = ds.run(
            self.company,
            ContactsFilter(
                date=[None, datetime(2015, 9, 30)]),
            [])
        names = set([r['name'] for r in recs])
        expected = {self.sue.name}
        self.assertEqual(expected, names)

    def test_filter_by_date_after(self):
        """Should show only contact with last_action_time after date."""
        ds = ContactsDataSource()
        recs = ds.run(
            self.company,
            ContactsFilter(
                date=[datetime(2015, 10, 1), None]),
            [])
        names = set([r['name'] for r in recs])
        expected = {self.john.name}
        self.assertEqual(expected, names)

    def test_filter_by_tags(self):
        ds = ContactsDataSource()
        recs = ds.run(
            self.company,
            ContactsFilter(tags=['EaSt']),
            [])
        names = set([r['name'] for r in recs])
        expected = {self.john.name}
        self.assertEqual(expected, names)

    def test_filter_by_empty_things(self):
        ds = ContactsDataSource()
        recs = ds.run(
            self.company,
            ContactsFilter(
                partner=[],
                tags=[],
                locations={'city': '', 'state': ''}),
            [])
        names = set([r['name'] for r in recs])
        expected = {self.john.name, self.sue.name}
        self.assertEqual(expected, names)

    def test_filter_by_state(self):
        ds = ContactsDataSource()
        recs = ds.run(
            self.company,
            ContactsFilter(
                locations={
                    'state': 'CA'
                }),
            [])
        names = [r['name'] for r in recs]
        expected = [self.sue.name]
        self.assertEqual(expected, names)

    def test_filter_by_city(self):
        ds = ContactsDataSource()
        recs = ds.run(
            self.company,
            ContactsFilter(
                locations={
                    'city': 'Los Angeles'
                }),
            [])
        names = [r['name'] for r in recs]
        expected = [self.sue.name]
        self.assertEqual(expected, names)

    def test_help_city(self):
        ds = ContactsDataSource()
        recs = ds.help_city(
            self.company,
            ContactsFilter(locations={'city': "zz"}),
            "angel")
        actual = set([r['key'] for r in recs])
        self.assertEqual({'Los Angeles'}, actual)

    def test_help_state(self):
        ds = ContactsDataSource()
        recs = ds.help_state(
            self.company,
            ContactsFilter(locations={'state': "zz"}),
            "i")
        actual = set([r['key'] for r in recs])
        self.assertEqual({'IL', 'IN'}, actual)

    def test_help_tags(self):
        ds = ContactsDataSource()
        recs = ds.help_tags(self.company, ContactsFilter(), "E")
        actual = set([r['key'] for r in recs])
        self.assertEqual({'east', 'west'}, actual)

    def test_help_partner(self):
        ds = ContactsDataSource()
        recs = ds.help_partner(self.company, ContactsFilter(), "A")
        self.assertEqual(
            [{'key': self.partner_a.pk, 'display': 'aaa'}],
            recs)

    def test_order(self):
        ds = ContactsDataSource()
        recs = ds.run(
            self.company,
            ContactsFilter(),
            ["-name"])
        names = [r['name'] for r in recs]
        expected = [self.sue.name, self.john.name]
        self.assertEqual(expected, names)


class MockDataSource(object):
    def __init__(self):
        self.calls = []

    def help_city(self, company, filter, partial):
        self.calls.append(['help_city', company, filter, partial])
        return 'aaa'

    def run(self, company, filter, order):
        self.calls.append(['run', company, filter, order])
        return 'aaa'


class TestContactsDataSourceJsonDriver(TestCase):
    def setUp(self):
        super(TestContactsDataSourceJsonDriver, self).setUp()
        self.ds = MockDataSource()
        self.driver = ContactsDataSourceJsonDriver(self.ds)

    def test_help_cities(self):
        result = self.driver.help('company', '{}', 'city', 'zzz')
        self.assertEqual('aaa', result)
        self.assertEqual([
            ['help_city', 'company', ContactsFilter(), 'zzz']
            ], self.ds.calls)

    def test_run(self):
        result = self.driver.run('company', '{}', '["zzz"]')
        self.assertEqual('aaa', result)
        self.assertEqual([
            ['run', 'company', ContactsFilter(), ['zzz']]
            ], self.ds.calls)

    def test_empty_filter(self):
        result = self.driver.build_filter("{}")
        self.assertEquals(ContactsFilter(), result)

    def test_city_filter(self):
        result = self.driver.build_filter(
                '{"locations": {"city": "Indy"}}')
        self.assertEquals(ContactsFilter(locations={'city': 'Indy'}), result)

    def test_date_filters(self):
        spec = '{"date": ["2015-09-01", "2015-09-30"]}'
        result = self.driver.build_filter(spec)
        expected = ContactsFilter(
            date=[datetime(2015, 9, 1), datetime(2015, 9, 30)])
        self.assertEquals(expected, result)

    def test_order(self):
        self.assertEqual(['name'], self.driver.build_order('["name"]'))

    def test_encode_filter_interface(self):
        report_config = ReportConfiguration([
            ColumnConfiguration(
                column='name',
                format='text'),
            ColumnConfiguration(
                column='date',
                format='us_date',
                filter_interface='date_range',
                filter_display='Date'),
            ColumnConfiguration(
                column='locations',
                format='city_state_list',
                filter_interface='city_state',
                filter_display='Locations',
                help=True),
            ColumnConfiguration(
                column='tags',
                format='comma_sep',
                filter_interface='search_multiselect',
                filter_display='Tags',
                help=True),
            ColumnConfiguration(
                column='partner',
                format='text',
                filter_interface='search_multiselect',
                filter_display='Partners',
                help=True),
        ])

        self.assertEquals({
            'filters': [
                {
                    'display': 'Date',
                    'filter': 'date',
                    'interface_type': 'date_range',
                },
                {
                    'display': 'Locations',
                    'filter': 'locations',
                    'interface_type': 'city_state',
                },
                {
                    'display': 'Tags',
                    'filter': 'tags',
                    'interface_type': 'search_multiselect',
                },
                {
                    'display': 'Partners',
                    'filter': 'partner',
                    'interface_type': 'search_multiselect',
                },
            ],
            'help': {
                'partner': True,
                'tags': True,
                'locations': True,
            },
        }, self.driver.encode_filter_interface(report_config))


class TestContactsFilterCloning(TestCase):
    def test_clone_without_empty(self):
        filter = ContactsFilter()
        self.assertEqual(ContactsFilter(), filter.clone_without_city())
        self.assertEqual(ContactsFilter(), filter.clone_without_state())

    def test_clone_without_full(self):
        filter = ContactsFilter(
                tags=['C'],
                locations={'city': 'A', 'state': 'B'})
        expected_with_city = ContactsFilter(
                tags=['C'],
                locations={'city': 'A'})
        expected_with_state = ContactsFilter(
                tags=['C'],
                locations={'state': 'B'})
        self.assertEqual(expected_with_state, filter.clone_without_city())
        self.assertEqual(expected_with_city, filter.clone_without_state())
