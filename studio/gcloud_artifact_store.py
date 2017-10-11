import logging
import time
import calendar

from google.cloud import storage
from .tartifact_store import TartifactStore

logging.basicConfig()


class GCloudArtifactStore(TartifactStore):
    def __init__(self, config, verbose=10, measure_timestamp_diff=False):
        self.logger = logging.getLogger('GCloudArtifactStore')
        self.logger.setLevel(verbose)

        self.config = config

        super(GCloudArtifactStore, self).__init__(measure_timestamp_diff)

    def _get_bucket_obj(self):
        try:
            bucket = self.get_client().get_bucket(self.config['bucket'])
        except BaseException as e:
            self.logger.exception(e)
            bucket = self.get_client().create_bucket(self.config['bucket'])

        return bucket

    def get_client(self):
        if 'credentials' in self.config.keys():
            return storage.Client \
                .from_service_account_json(self.config['serviceAccount'])
        else:
            return storage.Client()

    def _upload_file(self, key, local_path):
        self._get_bucket_obj().blob(key).upload_from_filename(local_path)

    def _download_file(self, key, local_path):
        self._get_bucket_obj().get_blob(key).download_to_filename(local_path)

    def _delete_file(self, key):
        blob = self._get_bucket_obj().get_blob(key)
        if blob:
            blob.delete()

    def _get_file_url(self, key, method='GET'):
        expiration = int(time.time() + 100000)
        return self._get_bucket_obj().blob(key).generate_signed_url(
            expiration,
            method=method)

    def _get_file_timestamp(self, key):
        blob = self._get_bucket_obj().get_blob(key)
        if blob is None:
            return None
        time_updated = blob.updated
        if time_updated:
            timestamp = calendar.timegm(time_updated.timetuple())
            return timestamp
        else:
            return None

    def grant_write(self, key, user):
        blob = self._get_bucket_obj().get_blob(key)
        if not blob:
            blob = self._get_bucket_obj().blob(key)
            blob.upload_from_string("dummy")

        acl = blob.acl
        if user:
            acl.user(user).grant_owner()
        else:
            acl.all().grant_owner()

        acl.save()

    def get_qualified_location(self, key):
        return 'gs://' + self.get_bucket() + '/' + key

    def get_bucket(self):
        return self._get_bucket_obj().name
