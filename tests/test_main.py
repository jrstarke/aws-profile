import os

import pytest

import awsprofile


@pytest.mark.parametrize('exit_code', [a for a in range(0, 256)])
def test_returns_correct_exit_code(exit_code, mocker):
    """The function exits with the same exit code as the command executed within the valid exit code ranges of 0 - 255 AND the correct AWS related environment variables are set"""
    mock_parse_args = mocker.patch('awsprofile.parse_args')
    mock_parse_args.return_value = ('profile-from-aws-profile-envvar', None, ['test-command-name'], 'true')
    mock_subprocess_call = mocker.patch('awsprofile.subprocess.call')
    mock_subprocess_call.return_value = exit_code
    mocker.patch.object(awsprofile.botocore.session.Session, 'get_credentials')
    awsprofile.botocore.session.Session.get_credentials.return_value = mocker.Mock(
        access_key='FAKE_ACCESS_{}'.format(exit_code), secret_key='FAKE_SECRET_{}'.format(exit_code),
        token='FAKE_TOKEN_{}'.format(exit_code))
    mocker.patch.object(awsprofile.botocore.session.Session, 'get_scoped_config')
    awsprofile.botocore.session.Session.get_scoped_config.return_value = {}
    mock_put_env = mocker.patch('awsprofile.os.putenv')
    with pytest.raises(SystemExit) as system_exit:
        awsprofile.main()
    assert system_exit.value.code == exit_code
    assert mock_put_env.call_count == 4
    assert mock_put_env.call_args_list == [mocker.call('AWS_PROFILE', 'profile-from-aws-profile-envvar'),
                                           mocker.call('AWS_ACCESS_KEY_ID', 'FAKE_ACCESS_{}'.format(exit_code)),
                                           mocker.call('AWS_SECRET_ACCESS_KEY', 'FAKE_SECRET_{}'.format(exit_code)),
                                           mocker.call('AWS_SESSION_TOKEN', 'FAKE_TOKEN_{}'.format(exit_code))]


def test_the_region_is_set(mocker):
    """When the region is set in the config the REGION related environment variables should be set"""
    mock_parse_args = mocker.patch('awsprofile.parse_args')
    mock_parse_args.return_value = ('profile-from-aws-profile-envvar', "test-region", ['test-command-name'], 'true')
    mock_subprocess_call = mocker.patch('awsprofile.subprocess.call')
    mock_subprocess_call.return_value = 0
    mocker.patch.object(awsprofile.botocore.session.Session, 'get_credentials')
    awsprofile.botocore.session.Session.get_credentials.return_value = mocker.Mock(
        access_key='FAKE_ACCESS', secret_key='FAKE_SECRET',
        token='FAKE_TOKEN')
    mocker.patch.object(awsprofile.botocore.session.Session, 'get_scoped_config')
    awsprofile.botocore.session.Session.get_scoped_config.return_value = {'region': 'test-region'}
    mock_put_env = mocker.patch('awsprofile.os.putenv')
    with pytest.raises(SystemExit):
        awsprofile.main()
    assert mock_put_env.call_count == 6
    assert mock_put_env.call_args_list == [mocker.call('AWS_PROFILE', 'profile-from-aws-profile-envvar'),
                                           mocker.call('AWS_DEFAULT_REGION', 'test-region'),
                                           mocker.call('AWS_REGION', 'test-region'),
                                           mocker.call('AWS_ACCESS_KEY_ID', 'FAKE_ACCESS'),
                                           mocker.call('AWS_SECRET_ACCESS_KEY', 'FAKE_SECRET'),
                                           mocker.call('AWS_SESSION_TOKEN', 'FAKE_TOKEN')]


def test_cache_called(mocker):
    """"When the AWS_CACHE environment variable is true the credentials should be cached"""
    mock_parse_args = mocker.patch('awsprofile.parse_args')
    mock_parse_args.return_value = ('profile-from-aws-profile-envvar', "test-region", ['test-command-name'], 'true')
    mock_parse_configure_cache = mocker.patch('awsprofile.configure_cache')
    mock_subprocess_call = mocker.patch('awsprofile.subprocess.call')
    mock_subprocess_call.return_value = 0
    mocker.patch.object(awsprofile.botocore.session.Session, 'get_credentials')
    awsprofile.botocore.session.Session.get_credentials.return_value = mocker.Mock(
        access_key='FAKE_ACCESS', secret_key='FAKE_SECRET',
        token='FAKE_TOKEN')
    mocker.patch.object(awsprofile.botocore.session.Session, 'get_scoped_config')
    awsprofile.botocore.session.Session.get_scoped_config.return_value = {'region': 'test-region'}
    mocker.patch('awsprofile.os.putenv')
    with pytest.raises(SystemExit):
        awsprofile.main()
    assert mock_parse_configure_cache.call_count == 1


def test_cache_not_called(mocker):
    """"When the AWS_CACHE environment variable is false the credentials should be cached"""
    mock_parse_args = mocker.patch('awsprofile.parse_args')
    mock_parse_args.return_value = ('profile-from-aws-profile-envvar', "test-region", ['test-command-name'], 'false')
    mock_parse_configure_cache = mocker.patch('awsprofile.configure_cache')
    mock_subprocess_call = mocker.patch('awsprofile.subprocess.call')
    mock_subprocess_call.return_value = 0
    mocker.patch.object(awsprofile.botocore.session.Session, 'get_credentials')
    awsprofile.botocore.session.Session.get_credentials.return_value = mocker.Mock(
        access_key='FAKE_ACCESS', secret_key='FAKE_SECRET',
        token='FAKE_TOKEN')
    mocker.patch.object(awsprofile.botocore.session.Session, 'get_scoped_config')
    awsprofile.botocore.session.Session.get_scoped_config.return_value = {'region': 'test-region'}
    mocker.patch('awsprofile.os.putenv')
    with pytest.raises(SystemExit):
        awsprofile.main()
    assert mock_parse_configure_cache.call_count == 0


@pytest.mark.parametrize('token_type,expected_env_variable', [('security', 'AWS_SECURITY_TOKEN'), ('session', 'AWS_SESSION_TOKEN')])
def test_token_type_set_correctly(token_type, expected_env_variable, mocker):
    """"The AWS_TOKEN_TYPE environment variable cause the correct environment variable to be set"""
    os.environ['AWS_TOKEN_TYPE'] = token_type
    mock_parse_args = mocker.patch('awsprofile.parse_args')
    mock_parse_args.return_value = ('profile-from-aws-profile-envvar', "test-region", ['test-command-name'], 'false')
    mocker.patch('awsprofile.configure_cache')
    mock_subprocess_call = mocker.patch('awsprofile.subprocess.call')
    mock_subprocess_call.return_value = 0
    mocker.patch.object(awsprofile.botocore.session.Session, 'get_credentials')
    awsprofile.botocore.session.Session.get_credentials.return_value = mocker.Mock(
        access_key='FAKE_ACCESS', secret_key='FAKE_SECRET',
        token='FAKE_TOKEN')
    mocker.patch.object(awsprofile.botocore.session.Session, 'get_scoped_config')
    awsprofile.botocore.session.Session.get_scoped_config.return_value = {'region': 'test-region'}
    mock_put_env = mocker.patch('awsprofile.os.putenv')
    with pytest.raises(SystemExit):
        awsprofile.main()
    assert mock_put_env.call_count == 6
    assert mock_put_env.call_args_list == [mocker.call('AWS_PROFILE', 'profile-from-aws-profile-envvar'),
                                           mocker.call('AWS_DEFAULT_REGION', 'test-region'),
                                           mocker.call('AWS_REGION', 'test-region'),
                                           mocker.call('AWS_ACCESS_KEY_ID', 'FAKE_ACCESS'),
                                           mocker.call('AWS_SECRET_ACCESS_KEY', 'FAKE_SECRET'),
                                           mocker.call(expected_env_variable, 'FAKE_TOKEN')]
