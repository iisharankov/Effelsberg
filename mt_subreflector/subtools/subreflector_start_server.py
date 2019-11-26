from subtools.subreflector_program import start_server


def main(*args, **kwargs):

    # import argparse

    # parse arguments
    USETESTSERVER = True
    start_server(USETESTSERVER)


if __name__ == '__main__':

    main()
