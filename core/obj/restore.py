"""
#
#   RESTORE
#   This file contains the function for restoring links.
#   Used in the core.obj module and callable via core.obj.restore_by(...)
#
"""
import debug
import operator  # operator.attrgetter needed for second depth access like invoice.company.name


def restore_by(link, ref, set, by=["uid"]):
    """Restore the pointer/link to an object.

    Usage:
        o.link = restore_by(o.link, o.link_ref, project.set)

    Args:
        link (TYPE): Link to the object
        ref (dict): Reference to the object
        set (list): List of objects to look in
        by (list, optional): Properties to use for lookup

    Returns:
        TYPE: Referenced object
    """
    if ref and not (link):
        new_link = [
            o
            for o in set
            if all(operator.attrgetter(attr)(o) == ref[attr] for attr in by)
        ]
        if len(new_link) == 1:
            # Found exactly one link, linking
            del ref
            return new_link[0]
        elif len(new_link) > 1:
            # Found more than one link, linking
            debug.log_warning("Link is not unique! Linking to first in list.")
            del ref
            return new_link[0]
        else:
            debug.log_warning(
                "Cannot find object with the given attribute to restore by!"
            )
            return None
    elif ref and link:
        # Link was already set, return itself to keep
        debug.log_warning(
            f"Cannot restore: ref ({ref}) stored and the link ({link}) was already set."
        )
        return link
    else:
        # Nothing to restore
        debug.log_warning("Cannot restore: ref is None!")
        return None
