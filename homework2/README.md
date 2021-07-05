# mygrep

## Description

Приложение эмулирует базовое поведение утилиты `grep`.

## Usage

```bash
mygrep path substring
```
Где `path` - путь, в котором нужно искать файлы, содержащие строку `substring`.

### Example

```bash
╭─sakost@sakost-pc ~ (venv)  
╰─$ mygrep --help
usage: mygrep [-h] path substring

positional arguments:
  path        path where to search substring occurrence
  substring   string to search

optional arguments:
  -h, --help  show this help message and exit
╭─sakost@sakost-pc ~ (venv) 
╰─$ mygrep . mygrep
README.md line=10: mygrep path substring
README.md line=24: Затем можно установить `mygrep` в `PATH` командой `make install`.
setup.py line=6: name='mygrep',
setup.py line=13: entry_points={'console_scripts': ['mygrep = myapp.app:run']},
```

## Installation

Данная команда создаст новое окружение и установит все необходимые библиотеки: `make venv`.

Затем можно установить `mygrep` в `PATH` командой `make install`.

## Run tests

```bash
make test
```

## Author

sakost a.k.a. Konstantin Sazhenov
