"""
Stegano hide/reveal with generators
"""

import argparse
import inspect
from typing import Iterator

from stegano import lsb
from stegano.lsb import generators


def hide(src_file_path: str, dst_file_path: str, generator, text: str) -> bool:
    """Hide text in the source image and save to a new file.

    :param src_file_path: Source file path
    :param dst_file_path: Destination file path
    :param generator: Generator
    :param text: Text to hide
    :return: True on success
    """
    try:
        secret = lsb.hide(image=src_file_path, message=text, generator=generator)
    except FileNotFoundError:
        print(f'File "{src_file_path}" does not exists.')
    except:
        print(f'Unknown exception while hiding data. Generator error?')
    else:
        secret.save(fp=dst_file_path)
        return True


def reveal(file_path: str, generator) -> bool:
    """Reveal hidden text in image

    :param file_path: File path
    :param generator: Generator
    :return: True on success
    """
    try:
        print(lsb.reveal(encoded_image=file_path, generator=generator))
    except FileNotFoundError:
        print(f'File "{file_path}" does not exists.')
    except:
        print(f'Impossible to detect hidden text. Are you sure the generator is valid?')
    else:
        return True


def inspect_lsb_generators():
    """Search for generators in stegano.lsb.generators module.

    :return: generators with no arguments required, generators with one argument required.
    """
    all_generators = dict(inspect.getmembers(generators, inspect.isfunction))
    _zero_parameter_gens = dict()
    _single_parameter_gens = dict()
    for name, func in all_generators.items():
        signature = inspect.signature(func)
        tmp = Iterator[int]
        if signature.return_annotation != tmp:
            continue
        params = signature.parameters
        if sum(v.default is inspect._empty for arg_name, v in params.items()) == 1:
            _single_parameter_gens[name] = func
        else:
            _zero_parameter_gens[name] = func
    return _zero_parameter_gens, _single_parameter_gens


if __name__ == '__main__':

    zero_parameter_gens, single_parameter_gens = inspect_lsb_generators()

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(help='commands', dest='command', required=True)

    generator_parser = argparse.ArgumentParser(add_help=False)
    generator_parser.add_argument('-g', '--generator', required=True, action='store', help='Generator',
                                  dest='generator', choices=zero_parameter_gens | single_parameter_gens)
    generator_parser.add_argument('-a', '--gen-argument', required=False, action='store', help='Generator argument',
                                  dest='gen_argument', type=int)

    hide_parser = subparsers.add_parser('hide', parents=[generator_parser])
    hide_parser.add_argument('-s', '--source', required=True, action='store', help='Source file')
    hide_parser.add_argument('-d', '--destination', required=True, action='store', help='Destination file')
    hide_parser.add_argument('text', action='store', help='Text to hide')

    reveal_parser = subparsers.add_parser('reveal', parents=[generator_parser])
    reveal_parser.add_argument(action='store', dest='file', help='File to analise')

    args = parser.parse_args()

    if args.generator in single_parameter_gens and args.gen_argument is None:
        print(f'Generator "{args.generator}" requires argument. (-a)')
        exit(1)

    gen_func = (zero_parameter_gens | single_parameter_gens)[args.generator]
    gen = gen_func() if args.generator in zero_parameter_gens else gen_func(args.gen_argument)

    ret = None
    match args.command:
        case 'hide':
            ret = hide(args.source, args.destination, gen, args.text)
        case 'reveal':
            ret = reveal(args.file, gen)

    if not ret:
        exit(1)
