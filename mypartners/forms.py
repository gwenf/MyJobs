from django import forms
from django.core.exceptions import ValidationError
from django.forms.util import ErrorList
from django.utils.timezone import get_current_timezone_name
from django.utils.datastructures import SortedDict

import pytz

from postajob.location_data import states
from myprofile.forms import generate_custom_widgets
from mypartners.models import (Contact, Partner, ContactRecord, PRMAttachment,
                               Status, Tag, Location, OutreachRecord,
                               ADDITION, CHANGE, MAX_ATTACHMENT_MB)
from mypartners.helpers import (log_change, get_attachment_link,
                                prm_worthy, tag_get_or_create)
from mypartners.widgets import (MultipleFileField,
                                SplitDateTimeDropDownField, TimeDropDownField)
from universal.forms import NormalizedModelForm
from universal.helpers import autofocus_input


def init_tags(self):
    if self.instance.id and self.instance.tags:
        tag_names = ",".join([tag.name for tag in self.instance.tags.all()])
        self.initial['tags'] = tag_names
    self.fields['tags'] = forms.CharField(
        label='Tags', max_length=255, required=False,
        help_text='ie \'Disability\', \'veteran-outreach\', etc. Separate tags with a comma.',
        widget=forms.TextInput(attrs={
            'id': 'p-tags',
            'autocomplete': 'off'})
    )


class ContactForm(NormalizedModelForm):
    """
    Creates a new contact or edits an existing one.
    """

    # used to identify if location info is entered into a form
    __LOCATION_FIELDS = (
        'label', 'address_line_one', 'address_line_two',
        'city', 'state', 'postal_code')
    # similarly for partner information
    __PARTNER_FIELDS = ('partner-tags', 'partner_id', 'partnername')

    def __init__(self, *args, **kwargs):
        super(ContactForm, self).__init__(*args, **kwargs)
        self.fields['name'] = forms.CharField(
            label="Name", max_length=255, required=True,
            widget=forms.TextInput(attrs={'placeholder': 'Full Name',
                                          'id': 'id_contact-name'}))

        # add location fields to form if this is a new contact
        if not self.instance.name:
            notes = self.fields.pop('notes')
            self.fields.update(LocationForm().fields)
            self.fields['city'].required = False
            self.fields['state'].required = False
            # move notes field to the end
            self.fields['notes'] = notes

        init_tags(self)

        if self.instance.user:
            self.fields['email'].widget.attrs['readonly'] = True
            self.fields['email'].help_text = 'This email address is ' \
                                             'maintained by the owner ' \
                                             'of the My.jobs email account ' \
                                             'and cannot be changed.'
        autofocus_input(self, 'name')

    class Meta:
        form_name = "Contact Information"
        model = Contact
        exclude = ['user', 'partner', 'locations', 'library', 'archived_on',
                   'approval_status', 'last_action_time']
        widgets = generate_custom_widgets(model)
        widgets['notes'] = forms.Textarea(
            attrs={'rows': 5, 'cols': 24,
                   'placeholder': 'Notes About This Contact'})

    def clean_email(self):
        if self.instance.user:
            return self.instance.email
        return self.cleaned_data['email']

    def clean_tags(self):
        data = filter(bool, self.cleaned_data['tags'].split(','))
        tags = tag_get_or_create(self.data['company_id'], data)
        return tags

    def save(self, request, partner, commit=True):
        new_or_change = CHANGE if self.instance.pk else ADDITION
        partner = Partner.objects.get(id=self.data['partner'])
        self.instance.partner = partner
        self.instance.update_last_action_time(False)
        contact = None
        if not self.instance.pk:
            contact = Contact.objects.filter(
                partner=partner, name=self.instance.name,
                email=self.instance.email).first()

            if contact:
                contact.phone = contact.phone or self.instance.phone
                contact.notes = contact.notes or self.instance.notes
                contact.archived_on = None
                contact.save()

                self.instance = contact

        contact = contact or super(ContactForm, self).save(commit)

        if any(self.cleaned_data.get(field)
               for field in self.__LOCATION_FIELDS
               if self.cleaned_data.get(field)):
            location = Location.objects.create(**{
                field: self.cleaned_data[field]
                for field in self.__LOCATION_FIELDS})

            if location not in contact.locations.all():
                contact.locations.add(location)

        log_change(contact, self, request.user, partner, contact.name,
                   action_type=new_or_change,
                   impersonator=request.impersonator)

        return contact


class NewPartnerForm(NormalizedModelForm):

    # used to identify if location info is entered into a form
    __LOCATION_FIELDS = (
        'label', 'address_line_one', 'address_line_two',
        'city', 'state', 'postal_code')
    # similarly for partner information
    __CONTACT_FIELDS = ('phone', 'email', 'name', 'notes')

    def __init__(self, *args, **kwargs):
        """
        This form is used only to create a partner.

        Had to change self.fields into an OrderDict to preserve order then
        'append' to the new fields because new fields need to be first.

        """
        self.user = kwargs.pop('user', '')
        super(NewPartnerForm, self).__init__(*args, **kwargs)

        # add location fields to form if this is a new contact
        if not self.instance.name:
            notes = self.fields.pop('notes')
            self.fields.update(LocationForm().fields)
            self.fields['city'].required = False
            self.fields['state'].required = False
            # move notes field to the end
            self.fields['notes'] = notes

        for field in self.fields.itervalues():
            # primary contact information isn't required to create a partner
            field.required = False
        model_fields = SortedDict(self.fields)

        new_fields = {
            'partnername': forms.CharField(
                label="Partner Organization", max_length=255, required=True,
                help_text="Name of the Organization",
                widget=forms.TextInput(
                    attrs={'placeholder': 'Partner Organization',
                           'id': 'id_partner-partnername'})),
            'partnersource': forms.CharField(
                label="Source", max_length=255, required=False,
                help_text="Website, event, or other source where you found the partner",
                widget=forms.TextInput(
                    attrs={'placeholder': 'Source',
                           'id': 'id_partner-partnersource'})),
            'partnerurl': forms.URLField(
                label="URL", max_length=255, required=False,
                help_text="Full url. ie http://partnerorganization.org",
                widget=forms.TextInput(attrs={'placeholder': 'URL',
                                              'id': 'id_partner-partnerurl'})),
            'partner-tags': forms.CharField(
                label='Tags', max_length=255, required=False,
                help_text="ie 'Disability', 'veteran-outreach', etc. Separate tags with a comma.",
                widget=forms.TextInput(attrs={'id': 'p-tags',
                                              'placeholder': 'Tags'}))
        }

        ordered_fields = SortedDict(new_fields)
        ordered_fields.update(model_fields)
        self.fields = ordered_fields
        autofocus_input(self, 'partnername')

    class Meta:
        form_name = "Partner Information"
        model = Contact
        exclude = ['user', 'partner', 'tags', 'locations', 'library',
                   'approval_status', 'archived_on', 'last_action_time']
        widgets = generate_custom_widgets(model)
        widgets['notes'] = forms.Textarea(
            attrs={'rows': 5, 'cols': 24,
                   'placeholder': 'Notes About This Contact'})

    def save(self, commit=True):
        # self.instance is a Contact instance
        company_id = self.data['company_id']
        partner_url = self.data.get('partnerurl', '')
        partner_source = self.data.get('partnersource', '')

        status = Status.objects.create(approved_by=self.user)
        partner = Partner.objects.create(name=self.data['partnername'],
                                         uri=partner_url, owner_id=company_id,
                                         data_source=partner_source,
                                         approval_status=status)
        log_change(partner, self, self.user, partner, partner.name,
                   action_type=ADDITION)

        self.data = remove_partner_data(self.data,
                                        ['partnername', 'partnerurl',
                                         'csrfmiddlewaretoken', 'company',
                                         'company_id', 'ct'])

        create_contact = any(self.cleaned_data.get(field)
                             for field in self.__CONTACT_FIELDS
                             if self.cleaned_data.get(field))

        if create_contact:
            create_location = any(self.cleaned_data.get(field)
                                  for field in self.__LOCATION_FIELDS
                                  if self.cleaned_data.get(field))

            self.instance.partner = partner
            instance = super(NewPartnerForm, self).save(commit)
            partner.primary_contact = instance

            if create_location:
                location = Location.objects.create(**{
                    field: self.cleaned_data[field]
                    for field in self.__LOCATION_FIELDS})

                if location not in instance.locations.all():
                    instance.locations.add(location)

            # Tag creation
            tag_data = filter(bool,
                              self.cleaned_data['partner-tags'].split(','))
            tags = tag_get_or_create(company_id, tag_data)
            partner.tags = tags
            partner.save()
            self.instance.tags = tags
            log_change(instance, self, self.user, partner, instance.name,
                       action_type=ADDITION)

            return instance
        # No contact was created
        return None

    def get_field_sets(self):
        """
        NewPartnerForm is a combination Partner and Contact form. As
        self.fields has already been turned into an SortedDict in __init__,
        we can easily segment our form into fieldsets.
        """
        sections = self.fields.keys()[:4], self.fields.keys()[4:]
        field_sets = [
            [self[field] for field in section] for section in sections
        ]
        return field_sets


def remove_partner_data(dictionary, keys):
    new_dictionary = dict(dictionary)
    for key in keys:
        if key in dictionary.keys():
            del new_dictionary[key]
    return new_dictionary


class PartnerForm(NormalizedModelForm):
    """
    This form is used only to edit the partner form. (see prm/view/details)

    """
    def __init__(self, *args, **kwargs):
        super(PartnerForm, self).__init__(*args, **kwargs)
        contacts = Contact.objects.filter(partner=kwargs['instance'],
                                          archived_on__isnull=True)
        choices = [(contact.id, contact.name) for contact in contacts]

        if kwargs['instance'].primary_contact:
            for choice in choices:
                if choice[0] == kwargs['instance'].primary_contact_id:
                    choices.insert(0, choices.pop(choices.index(choice)))

            if not kwargs['instance'].primary_contact:
                choices.insert(0, ('', "No Primary Contact"))
            else:
                choices.append(('', "No Primary Contact"))
        else:
            choices.insert(0, ('', "No Primary Contact"))

        self.fields['primary_contact'] = forms.ChoiceField(
            label="Primary Contact", required=False,
            help_text='Denotes who the primary contact is for this organization.',
            initial=unicode(choices[0][0]),
            choices=choices)

        init_tags(self)
        autofocus_input(self, 'name')

    class Meta:
        form_name = "Partner Information"
        model = Partner
        fields = ['name', 'data_source', 'uri', 'tags']
        widgets = generate_custom_widgets(model)

    def clean_tags(self):
        data = filter(bool, self.cleaned_data['tags'].split(','))
        tags = tag_get_or_create(self.data['company_id'], data)
        return tags

    def save(self, request, commit=True):
        new_or_change = CHANGE if self.instance.pk else ADDITION
        self.instance.update_last_action_time(False)
        instance = super(PartnerForm, self).save(commit)
        # Explicity set the primary_contact for the partner and re-save.
        try:
            instance.primary_contact = Contact.objects.get(
                pk=self.data['primary_contact'], partner=self.instance)
        except (Contact.DoesNotExist, ValueError):
            instance.primary_contact = None
        instance.save()
        log_change(instance, self, request.user, instance, instance.name,
                   action_type=new_or_change,
                   impersonator=request.impersonator)
        return instance


class ContactRecordForm(NormalizedModelForm):
    date_time = SplitDateTimeDropDownField(label='Date & Time')
    length = TimeDropDownField()
    attachment = MultipleFileField(required=False,
                                   help_text="Max file size %sMB" %
                                             MAX_ATTACHMENT_MB)

    class Meta:
        model = ContactRecord
        form_name = "Communication Record"
        fields = ('contact_type', 'contact',
                  'contact_email', 'contact_phone', 'location',
                  'length', 'subject', 'date_time', 'job_id',
                  'job_applications', 'job_interviews', 'job_hires',
                  'tags', 'notes', 'attachment')

    def __init__(self, *args, **kwargs):
        partner = None
        if 'partner' in kwargs:
            partner = kwargs.pop('partner')
        super(ContactRecordForm, self).__init__(*args, **kwargs)
        self.fields['contact'].required = True
        if not hasattr(self.instance, 'contact'):
            self.fields['contact'].required = False

        instance = kwargs.get('instance')
        if partner:
            self.fields["contact"].queryset = Contact.objects.filter(
                partner=partner, archived_on__isnull=True)

        if not instance or instance.contact_type != 'pssemail':
            # Remove Partner Saved Search from the list of valid
            # contact type choices.
            contact_type_choices = self.fields["contact_type"].choices
            pssemail = ('pssemail', 'Partner Saved Search Email')
            if pssemail in contact_type_choices:
                contact_type_choices.remove(pssemail)
                self.fields["contact_type"].choices = contact_type_choices

        # If there are attachments create a checkbox option to delete them.
        if instance and partner:
            attachments = PRMAttachment.objects.filter(contact_record=instance)
            if attachments:
                choices = [(a.pk, get_attachment_link(partner.id, a.id,
                            a.attachment.name.split("/")[-1]))
                           for a in attachments]
                self.fields["attach_delete"] = forms.MultipleChoiceField(
                    required=False, choices=choices, label="Delete Files",
                    widget=forms.CheckboxSelectMultiple)
        init_tags(self)

        # mark contact type specific fields as required
        for field in ['contact_email', 'contact_phone', 'location', 'job_id']:
            self.fields[field].label += " *"
        autofocus_input(self, "notes" if self.instance.pk else "contact_type")

    def clean(self):
        contact_type = self.cleaned_data.get('contact_type', None)
        if contact_type == 'email' and not self.cleaned_data['contact_email']:
            self._errors['contact_email'] = ErrorList([""])
        elif contact_type == 'phone' and not self.cleaned_data['contact_phone']:
            self._errors['contact_phone'] = ErrorList([""])
        elif contact_type == 'meetingorevent' and not self.cleaned_data['location']:
            self._errors['location'] = ErrorList([""])
        elif contact_type == 'job' and not self.cleaned_data['job_id']:
            self._errors['job_id'] = ErrorList([""])

        return self.cleaned_data

    def clean_attachment(self):
        attachments = self.cleaned_data.get('attachment', None)
        for attachment in attachments:
            if attachment and attachment.size > (MAX_ATTACHMENT_MB << 20):
                raise ValidationError('File too large')
        return self.cleaned_data['attachment']

    def clean_date_time(self):
        """
        Converts date_time field from localized time zone to utc.

        """
        date_time = self.cleaned_data['date_time']
        user_tz = pytz.timezone(get_current_timezone_name())
        date_time = user_tz.localize(date_time)
        return date_time.astimezone(pytz.utc)

    def clean_tags(self):
        data = filter(bool, self.cleaned_data['tags'].split(','))
        tags = tag_get_or_create(self.data['company'], data)
        return tags

    def save(self, request, partner, commit=True):
        new_or_change = CHANGE if self.instance.pk else ADDITION
        self.instance.partner = partner
        self.instance.update_last_action_time(False)

        if new_or_change == ADDITION:
            self.instance.created_by = request.user
        instance = super(ContactRecordForm, self).save(commit)

        self.instance.tags = self.cleaned_data.get('tags')
        attachments = self.cleaned_data.get('attachment', None)
        prm_attachments = [PRMAttachment(attachment=attachment,
                                         contact_record=self.instance)
                           for attachment in attachments if attachment]

        PRMAttachment.objects.bulk_create(prm_attachments)
        PRMAttachment.objects.filter(
            pk__in=self.cleaned_data.get('attach_delete', [])).delete()

        if instance.contact:
            identifier = instance.contact.name
        else:
            identifier = {'email': instance.contact_email,
                          'phone': instance.contact_phone}.get(
                              instance.contact_type, 'unknown contact')
        log_change(instance, self, request.user, partner, identifier,
                   action_type=new_or_change,
                   impersonator=request.impersonator)

        return instance


class TagForm(NormalizedModelForm):
    def __init__(self, *args, **kwargs):
        super(TagForm, self).__init__(*args, **kwargs)

    def clean_name(self):
        new_tag_name = self.cleaned_data.get('name')
        try:
            already_exists = Tag.objects.get(company=self.instance.company_id,
                                             name__iexact=new_tag_name)
        except Tag.DoesNotExist:
            already_exists = False

        if already_exists and already_exists.id != self.instance.id:
            raise ValidationError("This tag already exists.")
        return new_tag_name

    class Meta:
        form_name = "Tag"
        model = Tag
        fields = ['name', 'hex_color']
        widgets = generate_custom_widgets(model)


class LocationForm(NormalizedModelForm):
    def __init__(self, *args, **kwargs):
        super(LocationForm, self).__init__(*args, **kwargs)
        autofocus_input(self, 'address_line_one')

    class Meta:
        form_name = "Location"
        model = Location
        exclude = ('country_code',)
        widgets = generate_custom_widgets(model)

    state_choices = sorted(states.items(), key=lambda s: s[1])
    state_choices.insert(0, ('', 'Select a State'))
    state = forms.ChoiceField(
        widget=forms.Select(), choices=state_choices, label='State')

    def save(self, request, commit=True):
        new_or_change = CHANGE if self.instance.pk else ADDITION

        instance = super(LocationForm, self).save(commit)
        for contact in instance.contacts.all():
            contact.update_last_action_time()

        _, partner, _ = prm_worthy(request)
        log_change(instance, self, request.user, partner, instance.label,
                   action_type=new_or_change)

        return instance


def set_tag_choices(field, company):
    field.choices = [
        (t.pk, t.name)
        for t in company.tag_set.all()
    ]

class NuoPartnerForm(NormalizedModelForm):
    """
    Form for adding partners via NUO.
    """
    class Meta:
        form_name = "Partner"
        model = Partner
        fields = ['name', 'data_source', 'uri', 'tags']
    tags = forms.MultipleChoiceField(required=False, label='Tags')

    def __init__(self, *args, **kwargs):
        company = kwargs.pop('company')
        super(NuoPartnerForm, self).__init__(*args, **kwargs)
        set_tag_choices(self.fields['tags'], company)


class NuoContactForm(NormalizedModelForm):
    """
    Form for adding contacts via NUO.
    """
    class Meta:
        form_name = "Contact"
        model = Contact
        fields = ['name', 'email', 'phone', 'tags', 'notes']
    tags = forms.MultipleChoiceField(required=False, label='Tags')

    def __init__(self, *args, **kwargs):
        company = kwargs.pop('company')
        super(NuoContactForm, self).__init__(*args, **kwargs)
        set_tag_choices(self.fields['tags'], company)


class NuoLocationForm(NormalizedModelForm):
    """
    Form for adding locations via NUO.
    """
    class Meta:
        form_name = "Location"
        model = Location
        fields = [
            'address_line_one',
            'address_line_two',
            'city',
            'state',
            'postal_code',
            'label',
        ]


class NuoCommunicationRecordForm(NormalizedModelForm):
    """
    Form for adding communication records via NUO.
    """
    class Meta:
        form_name = "Communication Record"
        model = ContactRecord
        fields = ('contact_type',
                  'contact_email', 'contact_phone', 'location',
                  'length', 'subject', 'date_time', 'job_id',
                  'job_applications', 'job_interviews', 'job_hires',
                  'tags', 'notes')
    tags = forms.MultipleChoiceField(required=False, label='Tags')

    def __init__(self, *args, **kwargs):
        company = kwargs.pop('company')
        super(NuoCommunicationRecordForm, self).__init__(*args, **kwargs)
        set_tag_choices(self.fields['tags'], company)


class NuoOutreachRecordForm(NormalizedModelForm):
    """
    Form for editing outreach records via NUO.
    """
    class Meta:
        form_name = "Outreach Record"
        model = OutreachRecord
        fields = ('current_workflow_state',)
