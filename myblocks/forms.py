from fsm.widget import FSM

from django import forms
from django.core.urlresolvers import reverse_lazy

from myblocks import models


class BlockForm(forms.ModelForm):
    class Meta:
        exclude = ('updated', )
        model = models.Block

    def __init__(self, *args, **kwargs):
        super(BlockForm, self).__init__(*args, **kwargs)
        self.fields['template'].initial = models.raw_base_template(self.Meta.model)
        self.fields['head'].initial = models.raw_base_head(self.Meta.model)


class ApplyLinkBlockForm(BlockForm):
    class Meta:
        model = models.ApplyLinkBlock


class BreadboxBlockForm(BlockForm):
    class Meta:
        model = models.BreadboxBlock


class ColumnBlockForm(forms.ModelForm):
    class Meta:
        exclude = ('updated', 'template', )
        model = models.ColumnBlock


class ContentBlockForm(BlockForm):
    class Meta:
        model = models.ContentBlock


class FacetBlurbBlockForm(BlockForm):
    class Meta:
        model = models.FacetBlurbBlock


class JobDetailBlockForm(BlockForm):
    class Meta:
        model = models.JobDetailBlock


class JobDetailBreadboxBlockForm(BlockForm):
    class Meta:
        model = models.JobDetailBreadboxBlock


class JobDetailHeaderBlockForm(BlockForm):
    class Meta:
        model = models.JobDetailHeaderBlock


class LoginBlockForm(BlockForm):
    class Meta:
        model = models.LoginBlock


class MoreButtonBlockForm(BlockForm):
    class Meta:
        model = models.MoreButtonBlock


class RegistrationBlockForm(BlockForm):
    class Meta:
        model = models.RegistrationBlock

class ToolsWidgetBlockForm(BlockForm):
    class Meta:
        model = models.ToolsWidgetBlock

class SavedSearchWidgetBlockForm(BlockForm):
    class Meta:
        model = models.SavedSearchWidgetBlock


class SavedSearchesListWidgetBlockForm(BlockForm):
    class Meta:
        model = models.SavedSearchesListWidgetBlock


class SearchBoxBlockForm(BlockForm):
    class Meta:
        model = models.SearchBoxBlock


class SearchFilterBlockForm(BlockForm):
    class Meta:
        model = models.SearchFilterBlock


class SearchResultBlockForm(BlockForm):
    class Meta:
        model = models.SearchResultBlock


class SearchResultHeaderBlockForm(BlockForm):
    class Meta:
        model = models.SearchResultBlock


class ShareBlockForm(BlockForm):
    class Meta:
        model = models.ShareBlock


class VeteranSearchBoxForm(BlockForm):
    class Meta:
        model = models.VeteranSearchBox


class PageForm(forms.ModelForm):
    class Meta:
        exclude = ('updated', )
        widgets = {
            'sites': FSM('Site', reverse_lazy('site_admin_fsm'), lazy=True),
        }
        model = models.Page

    def __init__(self, *args, **kwargs):
        super(PageForm, self).__init__(*args, **kwargs)
        self.fields['head'].initial = models.raw_base_head(self.Meta.model)
        # without this, we get two options for ''. Setting blank=False on the
        # model also gets rid of the second option, but means that the blank
        # opton can never be chosen
        doc_type = self.fields['doc_type']
        language_code = self.fields['language_code']
        doc_type.choices = doc_type.choices[1:]
        language_code.choices = language_code.choices[1:]


class RowForm(forms.ModelForm):
    class Meta:
        exclude = ('updated', )
        model = models.Row
