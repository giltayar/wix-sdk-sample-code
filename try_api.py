from wixsamples.api.activities import ActivitiesApi


def main():
    activities_api = ActivitiesApi('app-id',
                                   'instance-guid',
                                   'secret-key')

    print activities_api.get_activity_types()


if __name__ == '__main__':
    main()
