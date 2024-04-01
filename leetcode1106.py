from miniparsec import *

spaces0 = Regex(r"\s*")
comma = Terminal(',')

t = Terminal('t').do(lambda _: True)
f = Terminal('f').do(lambda _: False)

expr = Forward()
expr.define(
  Choice(
    t,
    f,
    Sequence(
      Terminal('!'),
      Terminal('('),
      expr,
      Terminal(')')
    ).do(lambda x: not x[2]),
    Sequence(
      Terminal('&'),
      Terminal('('),
      spaces0,
      Sequence(expr, spaces0, comma, spaces0).do(lambda x: x[0]).repeat(0, None).do(lambda x: all(x)),
      expr,
      Terminal(')')
    ).do(lambda x: x[3] and x[4]),
    Sequence(
      Terminal('|'),
      Terminal('('),
      spaces0,
      Sequence(expr, spaces0, comma, spaces0).do(lambda x: x[0]).repeat(0, None).do(lambda x: any(x)),
      expr,
      Terminal(')')
    ).do(lambda x: x[3] or x[4])
  )
)

print(expr('t')) # True
print(expr('!(t)')) # False
print(expr('&(t, f)')) # False
print(expr('|(t, f)')) # True
print(expr('&(  t, f  , f)')) # False
print(expr('!(&(f,t))')) # True
print(expr("&(|(f))")) # False
print(expr("!(&(f,t))")) # True
