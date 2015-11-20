from redirect.models import RedirectArchive


class ArchiveRouter(object):
    """
    A router to ensure that all requests for RedirectArchive objects
    go to the "archive" database defined in settings.DATABASES.

    """
    def db_for_read(self, model, **hints):
        """
        Attempts to read from RedirectArchive go to "archive".

        """
        if model == RedirectArchive:
            return 'archive'
        return None

    def db_for_write(self, model, **hints):
        """
        Attempts to write to RedirectArchive go to "archive".

        """
        if model == RedirectArchive:
            return 'archive'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        """
        Prevent relations to the RedirectArchive table, since it should
        be on it's own database. This may need to be changed if we
        ever decide to host other tables on the same database as
        RedirectArchive.

        """
        if type(obj1) == RedirectArchive or type(obj2) == RedirectArchive:
            return False
        return None

    def allow_migrate(self, db, app_label, **hints):
        """
        Make sure the RedirectArchive model only appears in the "archive"
        database.

        """
        is_archive = hints.get('model') == RedirectArchive
        if db == "archive":
            return app_label == 'redirect'
        elif is_archive:
            return False
        return None