import factory
from factory import fuzzy
import string
import pytz

from datetime import datetime
from django.contrib.contenttypes.models import ContentType

from seo.tests.factories import CompanyFactory


class StatusFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'mypartners.Status'

    # Approved
    code = 1


class PartnerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'mypartners.Partner'

    name = 'Company'
    uri = 'www.my.jobs'

    owner = factory.SubFactory(CompanyFactory)
    approval_status = factory.SubFactory(StatusFactory)


class ContactFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'mypartners.Contact'

    name = 'foo bar'
    email = 'fake@email.com'
    phone = '84104391'

    partner = factory.SubFactory(PartnerFactory)
    approval_status = factory.SubFactory(StatusFactory)

    @factory.post_generation
    def locations(self, create, extracted, **kwargs):
        if not create:
            return

        locations = extracted or []
        self.locations.add(*locations)


class ContactRecordFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'mypartners.ContactRecord'

    contact_type = 'email'
    contact_email = 'example@email.com'
    subject = 'Test Subject'
    notes = 'Some notes go here.'
    date_time = datetime.now()

    contact = factory.SubFactory(ContactFactory, name='example-contact',
                                 partner=factory.SelfAttribute('..partner'))
    partner = factory.SubFactory(PartnerFactory)
    approval_status = factory.SubFactory(StatusFactory)

    @factory.post_generation
    def tags(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for tag in extracted:
                self.tags.add(tag)


class ContactLogEntryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'mypartners.ContactLogEntry'

    action_flag = 1
    contact_identifier = "Example Contact Log"
    content_type = factory.LazyAttribute(
                       lambda a: ContentType.objects.get(name='contact'))


class TagFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'mypartners.Tag'

    name = "foo"
    company = factory.SubFactory(CompanyFactory)


class LocationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "mypartners.Location"

    label = "Home"
    address_line_one = factory.Sequence(lambda n: "%d Fake St" % n)
    city = fuzzy.FuzzyText()
    state = fuzzy.FuzzyText(length=2, chars=string.ascii_uppercase)
    postal_code = fuzzy.FuzzyInteger(10000, 99999)


class PRMAttachmentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "mypartners.PRMAttachment"

    attachment = factory.django.FileField(
        filename='attachment.dat', data=b'This is an attachment.')

    contact_record = factory.SubFactory(ContactRecordFactory)


class OutreachEmailAddressFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "mypartners.OutreachEmailAddress"

    company = factory.SubFactory(CompanyFactory)
    email = fuzzy.FuzzyText()

class OutreachWorkflowStateFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "mypartners.OutreachWorkflowState"

    state = fuzzy.FuzzyText()

class OutreachRecordFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "mypartners.OutreachRecord"

    date_added = fuzzy.FuzzyDateTime(datetime.now(tz=pytz.utc))
    outreach_email = factory.SubFactory(OutreachEmailAddressFactory)
    from_email = fuzzy.FuzzyText()
    email_body = fuzzy.FuzzyText()
    current_workflow_state = factory.SubFactory(OutreachWorkflowStateFactory)
