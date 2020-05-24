# The Real Treasure was the Friends We Made Along the Way

Telegram bot to compute relative score for team-based games and to help balance the teams for yet another match.

<!--
[![Build Status](https://travis-ci.org/KrusnikViers/TgBotTemplate.svg)](https://travis-ci.org/KrusnikViers/TgBotTemplate)
[![Build status](https://ci.appveyor.com/api/projects/status/6uaw3t0aevq62ydp?svg=true)](https://ci.appveyor.com/project/KrusnikViers/tgbottemplate)
[![Coverage - Codecov](https://codecov.io/gh/KrusnikViers/TgBotTemplate/branch/master/graph/badge.svg)](https://codecov.io/gh/KrusnikViers/TgBotTemplate)
[![Maintainability](https://api.codeclimate.com/v1/badges/11bbbf9259251bdcada3/maintainability)](https://codeclimate.com/github/KrusnikViers/TgBotTemplate/maintainability)
-->

## Before the start
Every Telegram bot needs token from the @BotFather. When registering a token, keep in mind:
* For participating in groups, Group mode should be enabled;
* To see group message history, Group privacy mode should be disabled.

Options could be passed via configuration json file or command line (`-param_name=value`), configuration example is
in the `configuration.json.example` file. By default, bot will be looking for `configuration.json` file in the root
directory (same level with this README file). Telegram API token is the only required parameter to have bot started.
Parameter storage_directory should be skipped, if bot is running as a Docker container.

## How to run via Docker
```
docker run --restart always --name <instance name> -d \
 -v <path to configuration>:/instance/configuration.json \
 -v <path to the db directory>:/instance/storage \
 <docker image name>
```

## How to run as a developer

Project root directory should be added to `PYTHONPATH`. There are few scripts in `/scripts` directory, that are
useful for the development:
* `make_migrations.py`: autogenerate migrations from the updated models.
* `update_translations.py`: regenerate translations from the code.
* `run_tests.py`: launch python tests.
* `run_bot.py`: launch bot itself. Requires full configuration. 
