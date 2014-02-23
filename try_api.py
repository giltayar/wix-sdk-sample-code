from wixsamples.api.activities import ActivitiesApi
import sys


def main():
    activities_api = ActivitiesApi("API KEY",
                                   "INSTANCE KEY"
                                   "SECRET KEY")

    print '!', activities_api.get_activity_types(), '!'


if __name__ == '__main__':
    main()
