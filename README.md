# file-organizer

[![tests](https://github.com/SamruddhBorker/file-organizer/actions/workflows/tests.yml/badge.svg)](https://github.com/SamruddhBorker/file-organizer/actions/workflows/tests.yml)
 
Sorts a messy folder (Downloads, Desktop) into `Images`, `Videos`, `Audio`,
`Documents`, `Archives`, `Code`, `Installers` and `Other`.

- **Dry run by default**: it only prints the plan until you pass `--apply`
- **Undo**: every `--apply` writes `.organizer_log.json`; `--undo` reverses it
- Never overwrites: name collisions become `file (1).ext`
- Python 3.9+, standard library only

```bash
python organize.py ~/Downloads             # preview
python organize.py ~/Downloads --apply     # do it
python organize.py ~/Downloads --apply --by-date   # nest in YYYY-MM
python organize.py ~/Downloads --undo      # revert last run
```

Only top-level files are touched; subfolders and dotfiles are left alone.

## Tests

```bash
python -m unittest -v
```

## License

MIT
