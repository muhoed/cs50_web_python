from django.core.mail.backends.filebased import EmailBackend
import os
import datetime
import re


class FileEmailBackend(EmailBackend):
    """
    Overrides standard Django file email backend to provide file name simplier
    for further automatic search and selection.
    """
    def _get_filename(self, email_messages):
        """Return a unique file name."""
        if self._fname is None:
            uid = os.path.split(os.path.split(os.path.split(email_messages[0].body)[0])[0])[1]
            timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
            fname = "%s_pwdreset_%s.log" % (uid, timestamp)
            self._fname = os.path.join(self.file_path, fname)
        return self._fname

    def open(self, email_messages):
        if self.stream is None:
            #added messages to call paramd
            self.stream = open(self._get_filename(email_messages), 'ab')
            return True
        return False

    def send_messages(self, email_messages):
        """Write all messages to the stream in a thread-safe way."""
        if not email_messages:
            return
        msg_count = 0
        with self._lock:
            try:
                #added messages to call paramd
                stream_created = self.open(email_messages)
                for message in email_messages:
                    self.write_message(message)
                    self.stream.flush()  # flush after each message
                    msg_count += 1
                if stream_created:
                    self.close()
            except Exception:
                if not self.fail_silently:
                    raise
        return msg_count
