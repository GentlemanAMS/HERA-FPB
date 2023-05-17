import importlib
import asyncio
import logging

from tap import Tap

from fpb_tools import subparsers, get_logger, CmdFailedError, HandlerTy


class Args(Tap):
    debug: bool = False  # whether to enable debug logging

    def configure(self):
        self.add_subparsers(dest="cmd", required=True)
        for flag, subparser in subparsers.items():
            self.add_subparser(flag, subparser, help=subparser.__doc__)  # noqa


async def async_main():
    args = Args(underscores_to_dashes=True).parse_args()

    # set up logger
    logging.basicConfig(
        format="%(levelname)s %(asctime)s %(message)s",
        level=logging.DEBUG if args.debug else logging.INFO,
    )
    logger = get_logger()

    # get command handler

    package, func = args.cmd.split(".")  # noqa
    handler: HandlerTy = getattr(importlib.import_module(f"fpb_tools.{package}"), func)

    # call command handler
    kwargs = args.as_dict()
    del kwargs["cmd"]
    if "debug" in kwargs:
        del kwargs["debug"]
    try:
        await handler(**kwargs, logger=logger)
    except CmdFailedError as e:
        exit(f"Error: {e.args[0]}")


def main():
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
