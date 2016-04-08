from myjobs.tests.setup import MyJobsBase
from mypartners.tests.factories import PartnerFactory

from myreports.tests.factories import (
    UserTypeFactory, ReportingTypeFactory, UserReportingTypesFactory,
    ReportTypeFactory, ReportingTypeReportTypesFactory, DataTypeFactory,
    ReportTypeDataTypesFactory, PresentationTypeFactory,
    ReportPresentationFactory, ConfigurationFactory,
    ConfigurationColumnFactory)

from myreports.models import (
    UserType, ReportingType, UserReportingTypes, ReportType,
    ReportingTypeReportTypes, DataType, ReportTypeDataTypes,
    PresentationType, ReportPresentation, Configuration,
    ConfigurationColumn)


class MyReportsTestCase(MyJobsBase):
    """
    Base class for all MyReports Tests. Identical to `django.test.TestCase`
    except that it provides a MyJobs TestClient instance and a logged in user.
    """
    def setUp(self):
        super(MyReportsTestCase, self).setUp()
        self.role.activities = self.activities
        self.partner = PartnerFactory(name='Test Partner', owner=self.company)
        self.dynamic_models = create_full_fixture()


def create_full_fixture():
    """This fixture fills out all the dynamic reporting tables.

    Its purpose is to support unit and UI testing.

    WARNING: existing data is deleted from the tables to preserve stable ids
    and test behavior.

    It covers:
        * Standard known reports.
        * All known forms of inactive records for every table.
        * UI and "active_..." manager methods should never return or show
          an inactive record. So UI should never see "Dead" or "Maybe Dead"
          items.

    returns:
        a dictionary of references to models important for testing
    """

    # For each model create one or more plausible active records.
    # - If a reference to this record isn't needed, don't make a variable for
    #   it.
    # - Otherwise, the variable name is short but named like:
    #   modelabbreviation_purpose
    # Also create an inactive record.
    # - If a variable is needed, name the variable "..._dead".
    # Also, create an active version of the record meant to be linked via an
    # inactive through record.
    # - If a variable is needed, name the variable "..._maybe_dead".

    # Delete all
    UserType.objects.all().delete()
    ut_emp_dead = UserTypeFactory.create(
        id=1, user_type="EMPLOYER", is_active=False)
    ut_emp = UserTypeFactory.create(id=2, user_type="EMPLOYER")
    ut_staff = UserTypeFactory.create(id=3, user_type="STAFF")

    ReportingType.objects.all().delete()
    rit_prm = ReportingTypeFactory.create(
        id=1,
        reporting_type="prm",
        description="PRM Reports")
    rit_comp = ReportingTypeFactory.create(
        id=2,
        reporting_type="compliance",
        description="Compliance Reports")
    rit_dead = ReportingTypeFactory.create(
        id=3,
        reporting_type="Dead",
        description="Dead Reports",
        is_active=False)
    rit_maybe_dead = ReportingTypeFactory.create(
        id=4,
        reporting_type="Maybe Dead",
        description="Maybe Dead Reports",
        is_active=False)
    rit_wrong = ReportingTypeFactory.create(
        id=5,
        reporting_type="Wrong UT",
        description="Wrong UserType")

    UserReportingTypes.objects.all().delete()
    UserReportingTypesFactory.create(
        user_type=ut_emp, reporting_type=rit_prm)
    UserReportingTypesFactory.create(
        user_type=ut_emp, reporting_type=rit_comp)
    UserReportingTypesFactory.create(
        user_type=ut_emp, reporting_type=rit_dead)
    UserReportingTypesFactory.create(
        user_type=ut_emp, reporting_type=rit_maybe_dead, is_active=False)
    UserReportingTypesFactory.create(
        user_type=ut_emp_dead, reporting_type=rit_wrong)
    UserReportingTypesFactory.create(
        user_type=ut_staff, reporting_type=rit_comp)

    ReportType.objects.all().delete()
    rt_partners = ReportTypeFactory(
        id=1,
        report_type="partners",
        description="Partners Report",
        datasource="partners")
    rt_con = ReportTypeFactory(
        id=2,
        report_type="contacts",
        description="Contacts Report",
        datasource="contacts")
    rt_comm = ReportTypeFactory(
        id=3,
        report_type="communication-records",
        description="Communication Records Report",
        datasource="comm_records")
    rt_state = ReportTypeFactory(
        id=4,
        report_type="state",
        description="State Report")
    rt_screen = ReportTypeFactory(
        id=5,
        report_type="screenshots",
        description="Screenshots Report")
    rt_dead = ReportTypeFactory(
        id=6,
        report_type="Dead",
        description="Dead Report",
        is_active=False)
    rt_maybe_dead = ReportTypeFactory(
        id=7,
        report_type="Maybe Dead",
        description="Maybe Dead Report")

    ReportingTypeReportTypes.objects.all().delete()
    ReportingTypeReportTypesFactory.create(
        report_type=rt_partners, reporting_type=rit_prm)
    ReportingTypeReportTypesFactory.create(
        report_type=rt_con, reporting_type=rit_prm)
    ReportingTypeReportTypesFactory.create(
        report_type=rt_comm, reporting_type=rit_prm)
    ReportingTypeReportTypesFactory.create(
        report_type=rt_dead, reporting_type=rit_prm)
    ReportingTypeReportTypesFactory.create(
        report_type=rt_maybe_dead, reporting_type=rit_prm,
        is_active=False)
    ReportingTypeReportTypesFactory.create(
        report_type=rt_state, reporting_type=rit_comp)
    ReportingTypeReportTypesFactory.create(
        report_type=rt_screen, reporting_type=rit_comp)
    ReportingTypeReportTypesFactory.create(
        report_type=rt_dead, reporting_type=rit_comp)
    ReportingTypeReportTypesFactory.create(
        report_type=rt_maybe_dead, reporting_type=rit_prm,
        is_active=False)

    DataType.objects.all().delete()
    dt_dead = DataTypeFactory.create(
        id=1,
        data_type="",
        description="Dead",
        is_active=False)
    dt_maybe_dead = DataTypeFactory.create(
        id=2,
        data_type="",
        description="Maybe Dead")
    dt_unagg = DataTypeFactory.create(
        id=3,
        data_type="unaggregated",
        description="Unaggregated")
    dt_count_comm_per_month_per_partner = DataTypeFactory.create(
        id=4,
        data_type="count_comm_rec_per_month",
        description="Number of Communication Records per Month per Partner")

    PresentationType.objects.all().delete()
    pre_dead = PresentationTypeFactory.create(
        id=1, description="Inactive", is_active=False)
    pre_maybe_dead = PresentationTypeFactory.create(
        id=2, description="Maybe Inactive")
    pre_csv = PresentationTypeFactory.create(
        id=3, presentation_type="csv", description="Unformatted CSV")
    pre_xlsx = PresentationTypeFactory.create(
        id=4, presentation_type="xlsx", description="Excel xlsx")
    pre_json = PresentationTypeFactory.create(
        id=5,
        is_active=False,
        presentation_type="json_pass",
        description="JSON Passthrough")

    Configuration.objects.all().delete()
    con_dead = ConfigurationFactory.create(
        id=1, name="Inactive", is_active=False)
    ConfigurationFactory.create(
        id=2, name="Maybe Inactive")
    con_con = ConfigurationFactory.create(
        id=3, name="Contact Basic Report")
    con_part = ConfigurationFactory.create(
        id=4, name="Partner Basic Report")
    con_comm = ConfigurationFactory.create(
        id=5, name="Communication Records Basic Report")
    con_comm_count = ConfigurationFactory.create(
        id=6, name="Partners Comm Record Count Per Month Report")

    ConfigurationColumn.objects.all().delete()
    ConfigurationColumnFactory.create(
        id=1,
        column_name="dead",
        output_format="text",
        configuration=con_con,
        multi_value_expansion=False,
        is_active=False)
    ConfigurationColumnFactory.create(
        id=3,
        column_name="name",
        order=100,
        output_format="text",
        configuration=con_con,
        multi_value_expansion=False)
    ConfigurationColumnFactory.create(
        id=4,
        column_name="partner",
        order=101,
        output_format="text",
        filter_interface_type='search_multiselect',
        filter_interface_display='Partners',
        configuration=con_con,
        multi_value_expansion=False,
        has_help=True)
    ConfigurationColumnFactory.create(
        id=5,
        column_name="email",
        order=102,
        output_format="text",
        configuration=con_con,
        multi_value_expansion=False)
    ConfigurationColumnFactory.create(
        id=6,
        column_name="phone",
        order=103,
        output_format="text",
        configuration=con_con,
        multi_value_expansion=False)
    ConfigurationColumnFactory.create(
        id=7,
        column_name="date",
        order=104,
        configuration=con_con,
        output_format="us_date",
        filter_interface_type='date_range',
        filter_interface_display='Date',
        multi_value_expansion=False)
    ConfigurationColumnFactory.create(
        id=8,
        column_name="notes",
        order=105,
        output_format="text",
        configuration=con_con,
        multi_value_expansion=False)
    ConfigurationColumnFactory.create(
        id=9,
        column_name="locations",
        order=106,
        output_format="city_state_list",
        filter_interface_type='city_state',
        filter_interface_display='Location',
        configuration=con_con,
        multi_value_expansion=False,
        has_help=True)
    ConfigurationColumnFactory.create(
        id=10,
        column_name="tags",
        order=107,
        output_format="tags_list",
        filter_interface_type='tags',
        filter_interface_display='Tags',
        configuration=con_con,
        multi_value_expansion=False,
        has_help=True)

    ConfigurationColumnFactory.create(
        id=30,
        column_name="data_source",
        order=103,
        output_format="text",
        filter_interface_type='search_select',
        filter_interface_display='Data Source',
        configuration=con_part,
        multi_value_expansion=False)
    ConfigurationColumnFactory.create(
        id=31,
        column_name="name",
        order=104,
        output_format="text",
        configuration=con_part,
        multi_value_expansion=False)
    ConfigurationColumnFactory.create(
        id=32,
        column_name="date",
        order=105,
        configuration=con_part,
        output_format="us_date",
        filter_interface_type='date_range',
        filter_interface_display='Date',
        multi_value_expansion=False)
    ConfigurationColumnFactory.create(
        id=33,
        column_name="primary_contact",
        order=106,
        output_format="text",
        configuration=con_part,
        multi_value_expansion=False)
    ConfigurationColumnFactory.create(
        id=34,
        column_name="tags",
        order=107,
        output_format="tags_list",
        filter_interface_type='tags',
        filter_interface_display='Tags',
        configuration=con_part,
        multi_value_expansion=False,
        has_help=True)
    ConfigurationColumnFactory.create(
        id=35,
        column_name="uri",
        order=108,
        output_format="text",
        filter_interface_type='search_select',
        filter_interface_display='URL',
        configuration=con_part,
        multi_value_expansion=False)

    ConfigurationColumnFactory.create(
        id=60,
        column_name="contact",
        order=123,
        output_format="text",
        filter_interface_type='search_multiselect',
        filter_interface_display='Contacts',
        configuration=con_comm,
        multi_value_expansion=False,
        has_help=True)
    ConfigurationColumnFactory.create(
        id=61,
        column_name="contact_email",
        order=104,
        output_format="text",
        configuration=con_comm,
        multi_value_expansion=False)
    ConfigurationColumnFactory.create(
        id=62,
        column_name="contact_phone",
        order=105,
        configuration=con_comm,
        output_format="text",
        multi_value_expansion=False)
    ConfigurationColumnFactory.create(
        id=63,
        column_name="communication_type",
        order=109,
        filter_interface_type='search_select',
        filter_interface_display='Communication Type',
        configuration=con_comm,
        output_format="text",
        multi_value_expansion=False)
    ConfigurationColumnFactory.create(
        id=64,
        column_name="created_on",
        order=107,
        configuration=con_comm,
        output_format="us_date",
        multi_value_expansion=False)
    ConfigurationColumnFactory.create(
        id=65,
        column_name="created_by",
        order=108,
        configuration=con_comm,
        output_format="text",
        multi_value_expansion=False)
    ConfigurationColumnFactory.create(
        id=66,
        column_name="date_time",
        order=106,
        configuration=con_comm,
        output_format="us_date",
        filter_interface_type='date_range',
        filter_interface_display='Date',
        multi_value_expansion=False)
    ConfigurationColumnFactory.create(
        id=67,
        column_name="job_applications",
        order=110,
        output_format="text",
        configuration=con_comm,
        multi_value_expansion=False)
    ConfigurationColumnFactory.create(
        id=68,
        column_name="job_applications",
        order=111,
        output_format="text",
        configuration=con_comm,
        multi_value_expansion=False)
    ConfigurationColumnFactory.create(
        id=69,
        column_name="job_hires",
        order=112,
        output_format="text",
        configuration=con_comm,
        multi_value_expansion=False)
    ConfigurationColumnFactory.create(
        id=70,
        column_name="job_id",
        order=113,
        output_format="text",
        configuration=con_comm,
        multi_value_expansion=False)
    ConfigurationColumnFactory.create(
        id=71,
        column_name="job_interviews",
        order=114,
        output_format="text",
        configuration=con_comm,
        multi_value_expansion=False)
    ConfigurationColumnFactory.create(
        id=72,
        column_name="last_action_time",
        order=115,
        output_format="us_date",
        configuration=con_comm,
        multi_value_expansion=False)
    ConfigurationColumnFactory.create(
        id=73,
        column_name="length",
        order=116,
        output_format="text",
        configuration=con_comm,
        multi_value_expansion=False)
    ConfigurationColumnFactory.create(
        id=74,
        column_name="location",
        order=117,
        output_format="text",
        configuration=con_comm,
        multi_value_expansion=False)
    ConfigurationColumnFactory.create(
        id=75,
        column_name="notes",
        order=118,
        output_format="text",
        configuration=con_comm,
        multi_value_expansion=False)
    ConfigurationColumnFactory.create(
        id=76,
        column_name="partner",
        order=122,
        output_format="text",
        filter_interface_type='search_multiselect',
        filter_interface_display='Partners',
        configuration=con_comm,
        multi_value_expansion=False,
        has_help=True)
    ConfigurationColumnFactory.create(
        id=77,
        column_name="subject",
        order=120,
        output_format="text",
        configuration=con_comm,
        multi_value_expansion=False)
    ConfigurationColumnFactory.create(
        id=78,
        column_name="tags",
        order=121,
        output_format="tags_list",
        filter_interface_type='tags',
        filter_interface_display='Tags',
        configuration=con_comm,
        multi_value_expansion=False,
        has_help=True)
    ConfigurationColumnFactory.create(
        id=79,
        order=102,
        filter_interface_type='city_state',
        filter_interface_display='Contact Location',
        filter_only=True,
        configuration=con_comm,
        multi_value_expansion=False,
        has_help=True)

    ConfigurationColumnFactory.create(
        id=100,
        column_name="data_source",
        order=103,
        output_format="text",
        filter_interface_type='search_select',
        filter_interface_display='Data Source',
        configuration=con_comm_count,
        multi_value_expansion=False)
    ConfigurationColumnFactory.create(
        id=101,
        column_name="name",
        order=104,
        output_format="text",
        configuration=con_comm_count,
        multi_value_expansion=False)
    ConfigurationColumnFactory.create(
        id=102,
        column_name="date",
        order=105,
        configuration=con_comm_count,
        output_format="us_date",
        filter_interface_type='date_range',
        filter_interface_display='Date',
        multi_value_expansion=False)
    ConfigurationColumnFactory.create(
        id=103,
        column_name="primary_contact",
        order=106,
        output_format="text",
        configuration=con_comm_count,
        multi_value_expansion=False)
    ConfigurationColumnFactory.create(
        id=104,
        column_name="tags",
        order=107,
        output_format="tags_list",
        filter_interface_type='tags',
        filter_interface_display='Tags',
        configuration=con_comm_count,
        multi_value_expansion=False,
        has_help=True)
    ConfigurationColumnFactory.create(
        id=105,
        column_name="uri",
        order=108,
        output_format="text",
        filter_interface_type='search_select',
        filter_interface_display='URL',
        configuration=con_comm_count,
        multi_value_expansion=False)
    ConfigurationColumnFactory.create(
        id=106,
        column_name="year",
        order=109,
        output_format="text",
        configuration=con_comm_count,
        multi_value_expansion=False)
    ConfigurationColumnFactory.create(
        id=108,
        column_name="month",
        order=110,
        output_format="text",
        configuration=con_comm_count,
        multi_value_expansion=False)
    ConfigurationColumnFactory.create(
        id=109,
        column_name="comm_rec_count",
        order=111,
        output_format="text",
        configuration=con_comm_count,
        multi_value_expansion=False)

    ReportTypeDataTypes.objects.all().delete()
    ReportTypeDataTypesFactory.create(
        id=1, report_type=rt_con, data_type=dt_dead,  configuration=con_con)
    ReportTypeDataTypesFactory.create(
        id=2, report_type=rt_con, data_type=dt_maybe_dead, is_active=False,
        configuration=con_con)
    ReportTypeDataTypesFactory.create(
        id=3, report_type=rt_con, data_type=dt_maybe_dead, is_active=False,
        configuration=con_dead)
    rtdt_con_unagg = ReportTypeDataTypesFactory.create(
        id=4, report_type=rt_con, data_type=dt_unagg, configuration=con_con)
    rtdt_part_unagg = ReportTypeDataTypesFactory.create(
        id=5, report_type=rt_partners, data_type=dt_unagg,
        configuration=con_part)
    rtdt_comm_unagg = ReportTypeDataTypesFactory.create(
        id=6, report_type=rt_comm, data_type=dt_unagg, configuration=con_comm)
    rtdt_comm_count_pmpp = ReportTypeDataTypesFactory.create(
        id=7, report_type=rt_partners, configuration=con_comm_count,
        data_type=dt_count_comm_per_month_per_partner)
    ReportTypeDataTypesFactory.create(
        id=8, report_type=rt_con, data_type=dt_unagg, is_active=False,
        configuration=con_dead)

    ReportPresentation.objects.all().delete()
    ReportPresentationFactory.create(
        id=1, presentation_type=pre_maybe_dead,
        display_name="Dead", report_data=rtdt_con_unagg, is_active=False)
    ReportPresentationFactory.create(
        id=2, presentation_type=pre_dead,
        display_name="Dead Presentation",
        report_data=rtdt_con_unagg, is_active=True)
    rtpt_con = ReportPresentationFactory.create(
        id=3, presentation_type=pre_csv,
        display_name="Contact CSV",
        report_data=rtdt_con_unagg, is_active=True)
    ReportPresentationFactory.create(
        id=5, presentation_type=pre_csv,
        display_name="Partner CSV",
        report_data=rtdt_part_unagg, is_active=True)
    ReportPresentationFactory.create(
        id=6, presentation_type=pre_csv,
        display_name="Communication Record CSV",
        report_data=rtdt_comm_unagg, is_active=True)
    rtpt_xlsx = ReportPresentationFactory.create(
        id=7, presentation_type=pre_xlsx,
        display_name="Contact Excel Spreadsheet",
        report_data=rtdt_con_unagg, is_active=True)
    ReportPresentationFactory.create(
        id=8, presentation_type=pre_xlsx,
        display_name="Partner Excel Spreadsheet",
        report_data=rtdt_part_unagg, is_active=True)
    ReportPresentationFactory.create(
        id=9, presentation_type=pre_xlsx,
        display_name="Communication Record Excel Spreadsheet",
        report_data=rtdt_comm_unagg, is_active=True)
    ReportPresentationFactory.create(
        id=10, presentation_type=pre_json,
        display_name="Partner JSON Passthrough",
        report_data=rtdt_part_unagg, is_active=True)
    ReportPresentationFactory.create(
        id=11, presentation_type=pre_json,
        display_name="Contact JSON Passthrough",
        report_data=rtdt_con_unagg, is_active=True)
    ReportPresentationFactory.create(
        id=12, presentation_type=pre_json,
        display_name="Communication Record JSON Passthrough",
        report_data=rtdt_comm_unagg, is_active=True)
    ReportPresentationFactory.create(
        id=13, presentation_type=pre_csv,
        display_name="Communication Record Count CSV",
        report_data=rtdt_comm_count_pmpp, is_active=True)
    ReportPresentationFactory.create(
        id=14, presentation_type=pre_json,
        display_name="Communication Record Count JSON Passthrough",
        report_data=rtdt_comm_count_pmpp, is_active=True)

    return {
        'user_type': {
            'dead': ut_emp_dead,
            'employee': ut_emp,
            'staff': ut_staff,
        },
        'reporting_type': {
            'prm': rit_prm,
            'compliance': rit_comp,
            'dead': rit_dead,
            'maybe_dead': rit_maybe_dead,
            'wrong': rit_wrong,
        },
        'report_type': {
            'partners': rt_partners,
            'contacts': rt_con,
            'communication_records': rt_comm,
            'state': rt_state,
            'screenshots': rt_screen,
            'dead': rt_dead,
            'maybe_dead': rt_maybe_dead,
        },
        'data_type': {
            'dead': dt_dead,
            'maybe_dead': dt_maybe_dead,
            'unaggregated': dt_unagg,
            'count_comm_per_month_per_partner':
                dt_count_comm_per_month_per_partner,
        },
        'presentation_type': {
            'dead': pre_dead,
            'maybe_dead': pre_maybe_dead,
            'csv': pre_csv,
            'xlsx': pre_xlsx,
            'json': pre_json,
        },
        'configuration': {
            'dead': con_dead,
            'contacts': con_con,
            'partners': con_part,
            'communication_records': con_comm,
            'communication_records_count': con_comm_count,
        },
        'report_type/data_type': {
            'contacts/unaggregated': rtdt_con_unagg,
            'partners/unaggregated': rtdt_part_unagg,
            'communication_records/unaggregated': rtdt_comm_unagg,
            'communication_records_count/unaggregated':
                rtdt_comm_count_pmpp,
        },
        'report_type/presentation_type': {
            'contacts/csv': rtpt_con,
            'contacts/xlsx': rtpt_xlsx,
        },
    }
