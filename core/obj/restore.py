"""
#
#   RESTORE
#   This file contains the function for restoring links.
#   Used in the core.obj module and callable via core.obj.restore_by(...)
#
"""
import debug
import operator # operator.attrgetter needed for second depht access like invoice.company.name

def restore_by(link, ref, set, by=["uid"]):
    if ref and not(link):
        new_link = [o for o in set if all(operator.attrgetter(attr)(o) == ref[attr] for attr in by)]
        if len(new_link)>0:
            del ref
            return new_link[0]
        else:
            debug.log_warning("Cannot find object with the given attribute to restore by!")
    elif ref and link:
        debug.log_warning(f"Cannot restore: ref ({ref}) stored and the link ({link}) was already set.")
    else:
        debug.log_warning("Cannot restore: ref is None!")
