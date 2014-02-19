from django.contrib.contenttypes.models import ContentType
from django.core.files.storage import default_storage
from django.db import models

from myjobs.models import User
from mydashboard.models import Company


class Contact(models.Model):
    """
    Everything here is self explanatory except for one part. With the Contact object there is
    Contact.partner_set and .partners_set

    .partner_set = Foreign Key, Partner's Primary Contact
    .partners_set = m2m, all the partners this contact has associated to it
    """
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    name = models.CharField(max_length=255, verbose_name='Full Name',
                            blank=True)
    email = models.EmailField(max_length=255, verbose_name='Email', blank=True)
    phone = models.CharField(max_length=30, verbose_name='Phone', blank=True)
    label = models.CharField(max_length=60, verbose_name='Address Label',
                             blank=True)
    address_line_one = models.CharField(max_length=255,
                                        verbose_name='Address Line One',
                                        blank=True)
    address_line_two = models.CharField(max_length=255,
                                        verbose_name='Address Line Two',
                                        blank=True)
    city = models.CharField(max_length=255, verbose_name='City', blank=True)
    state = models.CharField(max_length=5, verbose_name='State/Region',
                             blank=True)
    country_code = models.CharField(max_length=3, verbose_name='Country',
                                    blank=True)
    postal_code = models.CharField(max_length=12, verbose_name='Postal Code',
                                   blank=True)
    notes = models.TextField(max_length=1000, verbose_name='Notes', blank=True)

    class Meta:
        verbose_name_plural = 'contacts'

    def __unicode__(self):
        if self.name:
            return self.name
        if self.email:
            return self.email
        return 'Contact object'

    def save(self, *args, **kwargs):
        """
        Checks to see if there is a User that is using self.email add said User
        to self.user
        """
        if not self.user:
            if self.email:
                try:
                    user = User.objects.get(email=self.email)
                except User.DoesNotExist:
                    pass
                else:
                    self.user = user
        super(Contact, self).save(*args, **kwargs)


class Partner(models.Model):
    """
    Object that this whole app is built around.
    """
    name = models.CharField(max_length=255,
                            verbose_name='Partner Organization')
    uri = models.URLField(verbose_name='Partner URL', blank=True)
    contacts = models.ManyToManyField(Contact, related_name="partners_set")
    primary_contact = models.ForeignKey(Contact, null=True,
                                        on_delete=models.SET_NULL)
    # owner is the Company that owns this partner.
    owner = models.ForeignKey(Company)

    def __unicode__(self):
        return self.name

    def add_contact(self, contact):
        self.contacts.add(contact)


class ContactRecord(models.Model):
    """
    Object for Communication Records
    """
    def get_file_name(self, filename):
        """
        Ensures that a file name is unique before uploading.

        inputs:
        :f: A file to be uploaded to default_storage.
        :path_addon: By default files are stored in /mypartners/ on S3. If
            path_addon is specified they will be uploaded to
            /mypartners/path_addon.
        :special_identifier: Any other special information that should be
            added to the file name.

        outputs:
        A string containing a filename that would be unique in default_storage.

        """
        path_addon = "mypartners/%s/%s" % (self.partner.owner,
                                           self.partner.name)
        file_ext = filename.split(".")[-1]
        name = filename.replace(".%s" % file_ext, "")
        name = "%s/%s" % (path_addon, name)

        file_counter = 1
        while default_storage.exists("%s.%s" % (name, file_ext)):
            name = "%s_%s" % (name, file_counter)
            file_counter += 1

        name = "%s.%s" % (name, file_ext)
        return name



    CONTACT_TYPE_CHOICES = (('email', 'Email'),
                            ('phone', 'Phone'),
                            ('facetoface', 'Face to Face'),
                            ('job', 'Job Followup'))
    created_on = models.DateTimeField(auto_now=True)
    partner = models.ForeignKey(Partner)
    contact_type = models.CharField(choices=CONTACT_TYPE_CHOICES,
                                    max_length=12,
                                    verbose_name="Contact Type")
    contact_name = models.CharField(max_length=255, verbose_name='Contact',
                                    blank=True)
    # contact type fields, fields required depending on contact_type. Enforced
    # on the form level.
    contact_email = models.CharField(max_length=255,
                                     verbose_name="Contact Email",
                                     blank=True)
    contact_phone = models.CharField(verbose_name="Contact Phone Number",
                                     max_length=30, blank=True)
    location = models.CharField(verbose_name="Meeting Location", max_length=255,
                                blank=True)
    length = models.TimeField(verbose_name="Meeting Length", blank=True,
                              null=True)
    subject = models.CharField(verbose_name="Subject or Topic", max_length=255,
                               blank=True)
    date_time = models.DateTimeField(verbose_name="Date & Time", blank=True)
    notes = models.TextField(max_length=1000,
                             verbose_name='Details, Notes or Transcripts',
                             blank=True)
    job_id = models.CharField(max_length=40, verbose_name='Job Number/ID',
                             blank=True)
    job_applications = models.CharField(max_length=6,
                                        verbose_name="Number of Applications",
                                        blank=True)
    job_interviews = models.CharField(max_length=6,
                                      verbose_name="Number of Interviews",
                                      blank=True)
    job_hires = models.CharField(max_length=6, verbose_name="Number of Hires",
                                 blank=True)
    attachment = models.FileField(upload_to=get_file_name,
                                  blank=True, null=True)

    def __unicode__(self):
        return "%s Contact Record - %s" % (self.contact_type, self.subject)

    def get_record_description(self):
        """
        Generates a human readable description of the contact
        record.

        """

        user = ContactLogEntry.objects.filter(object_id=self.pk)
        user = user.order_by('-action_time')[:1]
        if user:
            user = user[0].user.get_full_name()
        else:
            user = "An employee"

        if self.contact_type == 'facetoface':
            return "%s had a meeting with %s" % (user, self.contact_name)
        elif self.contact_type == 'phone':
            return "%s called %s" % (user, self.contact_phone)
        else:
            return "%s emailed %s" % (user, self.contact_email)

        attachment = self.cleaned_data['attachment']
        if attachment:
            path_addon = "%s/%s" % (self.partner.owner, self.partner.name)
            attachment.name = get_file_name(attachment, path_addon)
            self.cleaned_data['attachment'] = attachment

        print self.cleaned_data['attachment'].name

    def save(self, *args, **kwargs):
        super(ContactRecord, self).save(*args, **kwargs)
        



class ContactLogEntry(models.Model):
    action_flag = models.PositiveSmallIntegerField('action flag')
    action_time = models.DateTimeField('action time', auto_now=True)
    change_message = models.TextField('change message', blank=True)
    # A value that can meaningfully (email, name) identify the contact.
    contact_identifier = models.CharField(max_length=255)
    content_type = models.ForeignKey(ContentType, blank=True, null=True)
    object_id = models.TextField('object id', blank=True, null=True)
    object_repr = models.CharField('object repr', max_length=200)
    partner = models.ForeignKey(Partner, null=True, on_delete=models.SET_NULL)
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)

    def get_edited_object(self):
        """
        Returns the edited object represented by this log entry

        """
        try:
            return self.content_type.get_object_for_this_type(pk=self.object_id)
        except self.content_type.model_class().DoesNotExist:
            return None