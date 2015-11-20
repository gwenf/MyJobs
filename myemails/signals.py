from django.contrib.auth.models import ContentType
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

from myemails.models import EmailTask, Event


def event_receiver(signal, content_type, type_):
    def event_receiver_decorator(fn):
        sender = ContentType.objects.get(model=content_type).model_class()
        dispatch_uid = '%s_%s_%s' % (fn.__name__, content_type, type_)
        wrapper = receiver(signal, sender=sender, dispatch_uid=dispatch_uid)
        return wrapper(fn)
    return event_receiver_decorator


# I don't really like doing it this way (get from database pre save, set
# attribute, get again post save), but we need to be able to 1) determine what
# was changed and 2) only send an email if the save is successful. - TP
@event_receiver(pre_save, 'invoice', 'created')
@event_receiver(pre_save, 'purchasedproduct', 'created')
def pre_add_invoice(sender, instance, **kwargs):
    """
    Determines if an invoice has been added to the provided instance.

    Inputs:
    :sender: Which event type is being saved
    :instance: Specific instance being saved
    """
    invoice_added = hasattr(instance, 'invoice')
    if instance.pk:
        original = sender.objects.get(pk=instance.pk)
        invoice_added = not hasattr(original, 'invoice') and invoice_added
    instance.invoice_added = invoice_added


@event_receiver(post_save, 'invoice', 'created')
@event_receiver(post_save, 'purchasedproduct', 'created')
def post_add_invoice(sender, instance, **kwargs):
    """
    Schedules tasks for the instance if pre_add_invoice determined that an
    invoice was added.

    Inputs:
    :sender: Which event type is being saved
    :instance: Specific instance being saved
    """
    if instance.invoice_added:
        content_type = ContentType.objects.get(model='invoice')
        events = Event.objects.filter(model=content_type,
                                      owner=instance.product.owner)
        for event in events:
            EmailTask.objects.create(act_on=instance.invoice,
                                     related_event=event).schedule()
