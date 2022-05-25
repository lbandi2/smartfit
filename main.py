from definitions import Sede
from utils import make_dir

locations = "https://smartfit.com.co/gimnasios"

base_url = "https://smartfit.com.co/gimnasios/exito-country"
base_filename = "web_page.html"
classes_filename = "classes.html"

def main():
    make_dir("data")
    a = Sede(base_url, base_filename, classes_filename, language='en')
    print(a.name)
    print(a.working_hours)
    print(a.address)
    print(a.features)
    print(a.assistance)
    print(a.classes_today)
    print(a.classes_tomorrow)

if __name__ == '__main__':
    main()
