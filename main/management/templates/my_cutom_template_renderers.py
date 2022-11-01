from django.conf import settings
import re

MOBILE_AGENT_RE=re.compile(r".*(iphone|mobile|androidtouch)",re.IGNORECASE)
def add_company_details(request):
    ret_dict = {
        "company_name": settings.COMPANY_NAME,
    }
    return ret_dict
