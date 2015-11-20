from seo.models import User

from seo.tests import factories
from seo.models import Company
from setup import DirectSEOBase


class SignalsTestCase(DirectSEOBase):
    def setUp(self):
        super(SignalsTestCase, self).setUp()
        self.prod_configuration = factories.ConfigurationFactory.build(status=2)
        self.staging_configuration = factories.ConfigurationFactory.build(status=1)
        self.prod_configuration.group.save()
        self.prod_configuration.save()
        self.staging_configuration.group.save()
        self.staging_configuration.save()

        self.company = factories.CompanyFactory.build(canonical_microsite='http://buckconsultants.jobs')
        self.company.save()
        self.site = factories.SeoSiteFactory.build(id=50)
        self.site.save()
        self.site.configurations.add(self.prod_configuration)
        self.site.configurations.add(self.staging_configuration)

    def test_remove_prod_config(self):
        company = Company.objects.get(id=self.company.id)
        self.assertEqual(company.canonical_microsite, 'http://' + self.site.domain)
        self.prod_configuration.delete()
        company = Company.objects.get(id=self.company.id)
        self.assertEqual(company.canonical_microsite, None)

    def test_delete_canonical_microsite(self):
        company = Company.objects.get(id=self.company.id)
        self.assertEqual(company.canonical_microsite, 'http://' + self.site.domain)
        self.site.delete()
        company = Company.objects.get(id=self.company.id)
        self.assertEqual(company.canonical_microsite, None)

    def test_move_canonical_microsite(self):
        company = Company.objects.get(id=self.company.id)
        self.assertEqual(company.canonical_microsite, 'http://' + self.site.domain)
        self.site.domain = 'nuckconsultants.jobs'
        self.site.save()
        company = Company.objects.get(id=self.company.id)
        self.assertEqual(company.canonical_microsite, 'http://nuckconsultants.jobs')


class AdminSignalsTestCase(SignalsTestCase):

        def setUp(self):
            super(AdminSignalsTestCase, self).setUp()
            self.password = 'imbatmancalifornia'
            self.user = User.objects.create_superuser(password=self.password,
                                                      email='bc@batyacht.com')
            self.user.save()

        def test_canonical_site_warning(self):
            self.client.login(email=self.user.email,
                              password=self.password)
            company = Company.objects.get(id=self.company.id)
            self.assertEqual(company.canonical_microsite, 'http://' + self.site.domain)
            response = self.client.post('/admin/seo/seosite/%s/delete/' %
                    self.site.id, {'post': 'yes'}, follow=True)
            company = Company.objects.get(id=self.company.id)
            self.assertEqual(company.canonical_microsite, None)
            #Ensure we're getting a message about the canonical microsite being
            #changed
            self.assertNotEqual(response.content.find(
                    'Canonical microsite for %s removed' % company.name), -1)
