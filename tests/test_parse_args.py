import os

import pytest

from awsprofile import parse_args


@pytest.fixture(autouse=True)
def setup_environment():
    for environment_variable in ['AWS_CACHE']:
        try:
            del os.environ[environment_variable]
        except KeyError:
            pass


@pytest.mark.parametrize("command_line", ['aws-profile', 'aws-profile -p default', 'aws-profile --profile default'])
def test_empty_command_prints_help(command_line, capsys, mocker):
    """When no command is provided ensure the usage is printed and SystemExit is raised"""
    mocker.patch('sys.argv', command_line.split(' '))
    with pytest.raises(SystemExit):
        parse_args()
    out, err = capsys.readouterr()
    assert out.startswith('usage')


@pytest.mark.parametrize("command_line,expected_profile,expected_region,expected_commands",
                         [("aws-profile command", None, None, ["command"]),
                          ("aws-profile command -a argument", None, None, ["command", "-a", "argument"]),
                          ("aws-profile -p test-profile-name command", 'test-profile-name', None, ["command"]),
                          ("aws-profile -p test-profile-name command -a argument", 'test-profile-name', None,
                           ["command", "-a", "argument"]),
                          ("aws-profile --profile long-test-profile-name command", 'long-test-profile-name', None,
                           ["command"]),
                          (
                                  "aws-profile --profile long-test-profile-name command -a argument",
                                  'long-test-profile-name', None, ["command", "-a", "argument"]),
                          ("aws-profile -p test-profile-name -r test-region command", 'test-profile-name', "test-region", ["command"])
                          ]
                         )
def test_profile_is_set_as_expected(command_line, expected_profile, expected_region, expected_commands, mocker):
    """It should return the correct value for the profile, the option from the command line if present or None"""
    mocker.patch('sys.argv', command_line.split(' '))
    result = parse_args()
    assert (expected_profile, expected_region, expected_commands, 'true') == result


@pytest.mark.parametrize("envvar,expected", [
    ("anything", "true"),
    ("true", "true"),
    ("True", "true"),
     ("tRue", "true"),
     ("TRUE", "true"),
     ("false", "false"),
     ("FALSE", "false"),
     ("fAlse", "false"),
     ("False", "false")
])
def test_cache_envar_set_to_anything_other_than_false_or_FALSE(envvar, expected, mocker):
    """With AWS_CACHE env var set to anything other than false (case insensitive) it should return the string 'true'"""
    mocker.patch('sys.argv', ['aws-profile', 'test-command-name'])
    os.environ['AWS_CACHE'] = envvar
    result = parse_args()
    assert (None, None, ['test-command-name'], expected) == result
