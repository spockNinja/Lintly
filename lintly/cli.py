import logging
import logging.config
import sys

import click

from .builds import LintlyBuild
from .ci import find_ci_provider
from .config import Config
from .constants import FAIL_ON_ANY, FAIL_ON_NEW
from .exceptions import NotPullRequestException
from .parsers import PARSERS


logger = logging.getLogger(__name__)


@click.command()
@click.option('--api-key',
              envvar='LINTLY_API_KEY',
              help='The GitHub API key to use for commenting on PRs')
@click.option('--repo',
              envvar='LINTLY_REPO',
              help='The GitHub repo name in the format {owner}/{repo}')
@click.option('--pr',
              envvar='LINTLY_PR',
              help='The pull request number for this build')
@click.option('--commit-sha',
              envvar='LINTLY_COMMIT_SHA',
              help='The commit Lintly is running against.')
@click.option('--format',
              envvar='LINTLY_FORMAT',
              type=click.Choice(list(PARSERS.keys())),
              default='unix',
              help='The linting output format Lintly should expect to receive')
@click.option('--site-url',
              envvar='LINTLY_SITE_URL',
              default='github.com',
              help='The GitHub URL to use. Defaults to github.com. Override this if you use GitHub Enterprise.')
@click.option('--fail-on',
              envvar='LINTLY_FAIL_ON',
              type=click.Choice([FAIL_ON_ANY, FAIL_ON_NEW]),
              default=FAIL_ON_ANY,
              help='Whether Lintly should fail if any violations are detected or only if new violations are detected.')
@click.option('--post-status/--no-post-status',
              default=True,
              help='Used to determine if Lintly should post a PR status to GitHub.')
@click.option('--log',
              is_flag=True,
              help='Send Lintly debug logs to the console.')
def main(**options):
    """Slurp up linter output and send it to a GitHub PR review."""
    configure_logging(log_all=options.get('log'))

    stdin_stream = click.get_text_stream('stdin')
    stdin_text = stdin_stream.read()

    click.echo(stdin_text)

    ci = find_ci_provider()
    config = Config(options, ci=ci)

    build = LintlyBuild(config, stdin_text)
    try:
        build.execute()
    except NotPullRequestException:
        logger.info('Not a PR. Lintly is exiting.')
        sys.exit(0)

    # Exit with the number of files that have violations
    sys.exit(len(build.violations))


def configure_logging(log_all=False):
    log_level = 'DEBUG' if log_all else 'WARNING'
    logging.config.dictConfig({
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                'format': 'Lintly: %(asctime)s [%(levelname)s] %(name)s: %(message)s'
            },
        },
        'handlers': {
            'default': {
                'level': log_level,
                'class': 'logging.StreamHandler',
                'formatter': 'standard'
            },
        },
        'loggers': {
            'lintly': {
                'handlers': ['default'],
                'level': log_level,
                'propagate': True
            }
        }
    })
