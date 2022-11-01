from django.core.management.base import BaseCommand, CommandError
from time import ctime

# from django.conf import settings
from overwatcher import settings  # as sets
from sys import exit
import re, netifaces


# settings.__dict__.items()
def change_values_settings(replacable_dict={}):
    conf = "\n\n\n"
    for a in replacable_dict:
        b = replacable_dict[a]
        if str(type(b)) == "<class 'str'>":
            conf += a + ' = "' + b + '"' + "\n"
        else:
            conf += a + " = " + str(b) + "\n"
    open(settings.BASE_DIR / "overwatcher/settings.py", "a").write(conf)


class Command(BaseCommand):
    help = "Initializes the Website for each organization"

    def handle(self, *args, **options):
        x = input("Enter the Company/Organization Name:")
        if x == "":
            print("Can't be empty!")
            exit(1)
        saved_data = {"COMPANY_NAME": x}
        x = input("Enter the main domain(all subdomains included):")
        h = ["localhost", "127.0.0.1"]
        for inter in netifaces.interfaces():
            try:
                h.append(netifaces.ifaddresses(inter)[netifaces.AF_INET][0]["addr"])
            except KeyError:
                pass
        if x != "":
            h.append("*." + x)
            h.append(x)
        saved_data["ALLOWED_HOSTS"] = h
        print(
            "Activating E-mail will allow the notification feature and E-mail Validation. A tutorial is given in the link below(Configured for gmail):"
        )
        print(
            "https://www.nucleustechnologies.com/supportcenter/kb/how-to-create-an-app-password-for-gmail"
        )
        x = input("Enable E-mail(yes/no)[default:no]:")
        if x == "":
            x = "no"
        if x.lower() == "yes":
            email_enabled = True
        elif x.lower() == "no":
            email_enabled = False
        else:
            print("Invalid option!")
            exit(1)
        saved_data["EMAIL_VERIFICATION"] = email_enabled
        if email_enabled:
            x = input("Enter E-mail support:")
            if len(
                re.findall("[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", x)
            ) != 1 or len(
                re.findall("[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", x)[0]
            ) != len(
                x
            ):
                print("Invalid input!")
                exit(1)
            saved_data["EMAIL_HOST_USER"] = x
            x = input("Enter app password:")
            saved_data["EMAIL_HOST_PASSWORD"] = x
        change_values_settings(saved_data)
