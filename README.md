# Pixelmon 8.1.2 Move Fixer

Currently, Pokémon that returned to Gen 8 in [the Isle of Armor](https://bulbapedia.bulbagarden.net/wiki/The_Isle_of_Armor#Returning_Pok%C3%A9mon) have broken movesets in Pixelmon. They cannot learn any move by TM, and the moves they do learn are not up to date. This script scrapes Bulbapedia and resolves these issues.

## Installation

```shell
pip install -r requirements.txt
```

## Usage

First you'll need to enable external config files. Open `/config/pixelmon/pixelmon.hocon`, and under `ExternalFiles`, change `useExternalJSONFilesStats` to `true`. Then, restart your server. You can now run the following command.

```shell
python fix_moves.py [/pixelmon/stats]
```

Restart again and you're all set!
