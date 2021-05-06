"""
#
#   UID
#   Classes to uniquely identify objects. This is needed in order to restore pointers after loading a saved projects.
#   UID-objects additionally contain some meta-data.
#   The IdObject is parent of all classes in the obj-package.
#
"""
import debug

import uuid, collections
from datetime import datetime


class UID:

    """UID class object is like a nametag with some additional info like date created and modified.

    Attributes:
        class_name (str): Name of the class of the carryin object
        created_date (datetime.Date): Date the object was created
        edited_date (datetime.Date): Date the object was edited
        uid (uuid.UID): Unique identifier
    """

    def __init__(self, class_name, uid=None, created_date=None, edited_date=None):
        """Initialize UID.

        Args:
            class_name (str): Name of the class of the carryin object
            uid (uuid.UID, optional): Unique identifier
            created_date (datetime.Date, optional): Date the object was created
            edited_date (datetime.Date, optional): Date the object was edited
        """
        self.class_name = class_name
        self.uid = uid
        self.created_date = created_date
        self.edited_date = edited_date

        if uid is None:
            self.reset_uid()

    """
    #
    #   JSON FORMAT
    #
    #
    """

    def to_json(self):
        """This works like a JSON-encoder for the UID class.

        Returns:
            dict: A dict of the UID object
        """
        return {
            "UID": True,
            "class_name": self.class_name,
            "uid": str(self.uid),
            "created_date": self.created_date.isoformat(),
            "edited_date": self.edited_date.isoformat() if self.edited_date else None,
        }

    """
    #
    #   STRING LABELIZATION
    #   Used in the dialogs to display the UID data
    #
    """

    def labelize(self):
        """Create a string that can be used for the GUI.

        Returns:
            str: Label of the UID
        """
        dateformat = "%A, %d. %B %Y %H:%M"
        created_date = self.created_date.strftime(dateformat)
        edited_date = self.edited_date.strftime(dateformat) if self.edited_date else "-"
        return f"<UID(class_name: {self.class_name} | uid: {self.uid})> \n created: {created_date} \n edited: {edited_date}"

    """
    #
    #   REFRESH UID
    #   Get a new UID, in case of importing, so it is always unique
    #
    """

    def reset_uid(self):
        """Reset the UID."""
        created_date = datetime.now()
        edited_date = None
        self.uid = uuid.uuid4()
        self.created_date = created_date
        self.edited_date = edited_date

    """
    #
    #   __FUNCTIONS__
    #
    #
    """

    def __str__(self):
        return (
            "<UID"
            + str({"class_name": self.class_name, "uid": str(self.uid)})
            .replace("{", "(")
            .replace("}", ")")
            + ">"
        )

    def __eq__(self, other):
        """Define two UID objects to be the same, if the uid is the same"""
        if isinstance(other, UID):
            if (
                self.class_name == other.class_name
                and self.uid == other.uid
                and self.created_date == other.created_date
            ):
                if self.edited_date is not None and other.edited_date is not None:
                    if self.edited_date < other.edited_date:
                        print("left side uid is older!")
                        return True
                    elif self.edited_date > other.edited_date:
                        print("left side uid is newer!")
                        return True
                    else:
                        return True
                else:
                    return True
            else:
                return False


class IdObject:

    """Class of objects having an UID."""

    def __init__(self, o, uid=None, deleted=False):
        """Initialize IdObject.

        Args:
            uid (uid.UID, optional): The UID "nametag"
            deleted (bool, optional): True, if deleted

        Raises:
            Exception: If there is a type missmatch of the UID
        """
        # unique ID
        if uid is None:
            self._uid = UID(class_name=o.__class__.__name__)
        elif isinstance(uid, UID):
            self._uid = uid
        else:
            raise Exception("UID could not be restored!")

        self._deleted = deleted

    """
    #
    #   PROPERTIES
    #
    #
    """

    @property
    def uid(self):
        return self._uid

    @uid.setter
    def uid(self, input):
        """Prevent the change of the UID.

        Raises:
            Exception: Just den't
        """
        raise Exception("Cannot change the unique ID (uid)!")

    def uid_to_json(self):
        """Return the UID as a dict.

        Returns:
            dict: UID as dict
        """
        return self.uid.to_json()

    def edited(self):
        """Call this function upon editing the object to catch the timestamp."""
        self.uid.edited_date = datetime.now()

    """
    #   boolean properties
    """

    def is_deleted(self):
        """Check if deleted.

        Returns:
            bool: True, if deleted
        """
        return self._deleted

    def is_not_deleted(self):
        """Check if not deleted.

        Returns:
            bool: True, if not deleted
        """
        return not (self._deleted)

    def delete(self):
        """Delete object.

        Raises:
            Exception: Can't delete already deleted objects.
        """
        if self.is_not_deleted():
            self._deleted = True
            self.edited()
        else:
            raise Exception("Object was already deleted!")

    def undelete(self):
        """Restore if deleted.

        Raises:
            Exception: Can't restore not deleted objects
        """
        if self.deleted:
            self._deleted = False
            self.edited()
        else:
            raise Exception("Object is not deleted yet and hence cannot be undeleted!")
