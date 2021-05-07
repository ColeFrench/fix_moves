#!/usr/bin/env python3

import aiohttp
import asyncio
from bs4 import BeautifulSoup
import json
import os.path
import sys

UNIMPLEMENTED = ('Eerie Spell', 'Flip Turn', 'Poltergeist', 'Steel Roller')


async def get_pokemons(session):
    pokemons = []
    async with session.get(
            'https://bulbapedia.bulbagarden.net/wiki/The_Isle_of_Armor'
    ) as response:
        data = await response.read()
        soup = BeautifulSoup(data, 'lxml')
        for sibling in soup.find(id='Returning_Pokémon').parent.next_siblings:
            if sibling.name == 'table':
                for link in sibling.select('td:nth-child(4) a'):
                    pokemons.append(link.string.replace('-', ''))

                return pokemons


def get_tables(desc, soup):
    heading = soup.find(id=desc).parent

    form = '-1'
    tables = {}

    for sibling in heading.next_siblings:
        if sibling.name and sibling.name.startswith('h') and len(
                sibling.name) == 2:
            if int(sibling.name[1:]) <= int(heading.name[1:]) or list(
                    sibling.children)[0]['id'].startswith('By_'):
                break
            else:
                mapping = {'Alolan': '1', 'Galarian': '2'}
                key = list(sibling.children)[0].string.split()[0]

                if key in mapping:
                    form = mapping[key]
                else:
                    form = str(int(form) + 1)
        elif sibling.name == 'table':
            tables['0' if form == '-1' else form] = sibling.find(
                'table', class_='sortable')

    return tables


async def get_moves(pokemon, session, queue):
    try:
        move_data = {}
        async with session.get(
                f'https://bulbapedia.bulbagarden.net/wiki/{pokemon}'
        ) as response:
            data = await response.read()
            soup = BeautifulSoup(data, 'lxml')

            tables = get_tables('By_leveling_up', soup)
            for form, table in tables.items():
                levels = []
                for level_container in table.select(
                        'tbody > tr > td:nth-of-type(1)'):
                    maybe_level = list(level_container.children)[1]
                    if maybe_level.name == 'span':
                        level = '0'
                    else:
                        level = maybe_level.strip()

                    levels.append(level)

                moves = []
                for move_container in table.select(
                        'tbody > tr > td:nth-of-type(2) a > span'):
                    move = move_container.string
                    moves.append(move)

                for level, move in zip(levels, moves):
                    if move in UNIMPLEMENTED: continue
                    if form == '0':
                        move_data.setdefault('form', '0')
                        move_data.setdefault('levelUpMoves', {})
                        move_data['levelUpMoves'].setdefault(level, [])
                        move_data['levelUpMoves'][level].append(move)
                    else:
                        move_data.setdefault('forms', {})
                        move_data['forms'].setdefault(form, {})
                        move_data['forms'][form].setdefault('form', form)
                        move_data['forms'][form].setdefault('levelUpMoves', {})
                        move_data['forms'][form]['levelUpMoves'].setdefault(
                            level, [])
                        move_data['forms'][form]['levelUpMoves'][level].append(
                            move)

            tables = get_tables('By_TM/TR', soup)
            for form, table in tables.items():
                for disc_container in table.select(
                        'tbody > tr > td:nth-of-type(2) a > span'):
                    disc = disc_container.string
                    if disc.startswith('TM'):
                        tm = int(disc[2:])

                        if form == '0':
                            move_data.setdefault('tmMoves8', [])
                            move_data['tmMoves8'].append(tm)
                        else:
                            move_data['forms'][form].setdefault('tmMoves8', [])
                            move_data['forms'][form]['tmMoves8'].append(tm)
                    elif disc.startswith('TR'):
                        tr = int(disc[2:])

                        if form == '0':
                            move_data.setdefault('trMoves', [])
                            move_data['trMoves'].append(tr)
                        else:
                            move_data['forms'][form].setdefault('trMoves', [])
                            move_data['forms'][form]['trMoves'].append(tr)

            tables = get_tables('By_breeding', soup)
            for form, table in tables.items():
                for move_container in table.select(
                        'tbody > tr > td:nth-of-type(2) a > span'):
                    move = move_container.string
                    if move in UNIMPLEMENTED: continue
                    if form == '0':
                        move_data.setdefault('eggMoves', [])
                        move_data['eggMoves'].append(move)
                    else:
                        move_data['forms'][form].setdefault('eggMoves', [])
                        move_data['forms'][form]['eggMoves'].append(move)

            tables = get_tables('By_tutoring', soup)
            for form, table in tables.items():
                maybe_td = table.select('tbody > tr > td:nth-of-type(1)')
                if maybe_td:
                    for move_container in maybe_td[0].select('a > span'):
                        move = move_container.string
                        if move in UNIMPLEMENTED: continue
                        if form == '0':
                            move_data.setdefault('tutorMoves', [])
                            move_data['tutorMoves'].append(move)
                        else:
                            move_data['forms'][form].setdefault(
                                'tutorMoves', [])
                            move_data['forms'][form]['tutorMoves'].append(move)

            await queue.put((pokemon, move_data))
            print(f"Fetched data for {pokemon}.")
    except:
        print(f"Error fetching data for {pokemon}.")
        raise


async def produce(queue):
    async with aiohttp.ClientSession() as session:
        pokemons = await get_pokemons(session)
        await asyncio.gather(*(get_moves(pokemon, session, queue)
                               for pokemon in pokemons))


async def consume(queue):
    while True:
        pokemon, move_data = await queue.get()

        filename = f'{pokemon}.json'
        if len(sys.argv) == 2:
            path = os.path.normpath(f'{sys.argv[1]}/{filename}')
        else:
            path = filename

        try:
            with open(path) as file:
                config = json.load(file)

            config = {**config, **move_data}

            with open(path, 'w') as file:
                json.dump(config, file, indent=2)

            print(f"Updated moves in {filename}.")
        except FileNotFoundError:
            print(f"Could not find {filename}.")

        queue.task_done()


async def main():
    queue = asyncio.Queue()
    consume_task = asyncio.create_task(consume(queue))
    await produce(queue)
    await queue.join()
    consume_task.cancel()


if __name__ == '__main__':
    asyncio.run(main())
