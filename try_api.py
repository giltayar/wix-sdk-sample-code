import sys
from wixsamples.api.activities import ActivitiesApi


def main():
    activities_api = ActivitiesApi(*sys.argv[1:])

    print activities_api.get_activity_types()


if __name__ == '__main__':
    main()
