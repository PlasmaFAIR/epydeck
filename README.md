# epydeck

An EPOCH input file ("deck") reader/writer.

Plain numbers and bools are converted directly, everything else is
represented as a string. Note that floating point numbers may have
their exact form changed.

Reads from file into a standard Python `dict`. Repeated blocks, such
as `species`, have an extra level of nesting using the block `name`.
Repeated keys, such as `number_density`, are represented as a single
key with a list of values. For example, the following input deck:

```text
begin:constant
  lambda = 1.06 * micron
  omega = 2 * pi * c / lambda
  den_cone = 4.0 * critical(omega)
  th = 1 * micron / 2.0
  ri = abs(x - 5*micron) - sqrt(2.0) * th
  ro = abs(x - 5*micron) + sqrt(2.0) * th
  xi = 3*micron - th
  xo = 3*micron + th
  r = sqrt(y^2 + z^2)
end:constant

begin:species
  name = proton
  charge = 1.0
  mass = 1836.2
  fraction = 0.5
  number_density = if((r gt ri) and (r lt ro), den_cone, 0.0)
  number_density = if((x gt xi) and (x lt xo) and (r lt ri), \
                      den_cone, number_density(proton))
  number_density = if(x gt xo, 0.0, number_density(proton))
end:species

begin:species
  name = electron
  charge = -1.0
  mass = 1.0
  fraction = 0.5
  number_density = number_density(proton)
end:species
```

is represented by the following `dict`:

```python
{
  'constant': {
    'lambda': '1.06 * micron',
    'omega': '2 * pi * c / lambda',
    'den_cone': '4.0 * critical(omega)',
    'th': '1 * micron / 2.0',
    'ri': 'abs(x - 5*micron) - sqrt(2.0) * th',
    'ro': 'abs(x - 5*micron) + sqrt(2.0) * th',
    'xi': '3*micron - th',
    'xo': '3*micron + th',
    'r': 'sqrt(y^2 + z^2)',
  },
  'species': {
    'proton': {
      'name': 'proton',
      'charge': 1.0,
      'mass': 1836.2,
      'fraction': 0.5,
      'number_density': [
        'if((r gt ri) and (r lt ro), den_cone, 0.0)',
        'if((x gt xi) and (x lt xo) and (r lt ri), den_cone, number_density(proton))',
        'if(x gt xo, 0.0, number_density(proton))'
      ]
    },
    'electron': {
      'name': 'electron',
      'charge': -1.0,
      'mass': 1.0,
      'fraction': 0.5,
      'number_density': 'number_density(proton)'
    }
  }
}
```

## Installation

Currently just on Github, so either install from a local clone:

```bash
$ git clone git@github.com:PlasmaFAIR/epydeck.git
$ cd epydeck
$ pip install .
```

or directly from Github:

```bash
$ pip install git@github.com:PlasmaFAIR/epydeck.git
```

## Example

The interface follows the standard Python
[`json`](https://docs.python.org/3/library/json.html) module:

- `epydeck.load` to read from a `file` object
- `epydeck.loads` to read from an existing string
- `epydeck.dump` to write to a `file` object
- `epydeck.dumps` to write to a string

```python
import epydeck

# Read from a file with `epydeck.load`
with open(filename) as f:
    deck = epydeck.load(f)

print(deck.keys())
# dict_keys(['control', 'boundaries', 'constant', 'species', 'laser', 'output_global', 'output', 'dist_fn'])

# Modify the deck as a usual python dict:
deck["species"]["proton"]["charge"] = 2.0

# Write to file
with open(filename, "w") as f:
    epydeck.dump(deck, f)

print(epydeck.dumps(deck))
# ...
# begin:species
#   name = proton
#   charge = 2.0
#   mass = 1836.2
#   fraction = 0.5
#   number_density = if((r gt ri) and (r lt ro), den_cone, 0.0)
#   number_density = if((x gt xi) and (x lt xo) and (r lt ri), den_cone, number_density(proton))
#   number_density = if(x gt xo, 0.0, number_density(proton))
# end:species
# ...
```
