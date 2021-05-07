# Pixelmon 8.1.2 Move Fixer

Currently, Pokémon that returned to Gen 8 in [the Isle of Armor](https://bulbapedia.bulbagarden.net/wiki/The_Isle_of_Armor#Returning_Pok%C3%A9mon) have broken movesets in Pixelmon. They cannot learn any move by TM, and the moves they do learn (by other means such as leveling up) are not up to date. This script scrapes Bulbapedia to resolve these issues.

## Installation
<details>
    <summary>Prerequisites</summary>

You need `git`, a recent version of Python 3, and `pip` installed. Then clone this repo and enter the directory with

```shell
git clone https://github.com/ColeFrench/fix_moves.git
cd fix_moves
```
</details>

```shell
pip install -r requirements.txt
```

## Usage

First you'll need to enable external config files. Open `/config/pixelmon/pixelmon.hocon`, and under `ExternalFiles`, change `useExternalJSONFilesStats` to `true`. Then, restart your server. You can now run the following command.

```shell
python fix_moves.py [/path/to/stats]
```

From the root of your server, `/path/to/stats` is `/pixelmon/stats`. If no directory is specified, then the current directory is used.

After you run the script, you can restart again and you'll be all set!

### Technical notes

* You can rollback changes by deleting the `stats` folder, and Pixelmon will generate a new one on start.
* Some moves are currently unimplemented. These consist of Eerie Spell, Flip Turn, Poltergeist, Steel Roller, and they are not added by the script. More unimplemented moves may exist, but these are the only ones for the Pokémon the script modifies.
