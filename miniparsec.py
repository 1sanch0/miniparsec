from typing import Union
import copy
import re

class ParserException(Exception):
  pass

class Parser:
  def __init__(self, f: Union["Parser", None] = None):
    self.__f = f
    self.func = lambda x: x

  def parse(self, s: str):
    return self.__f.parse(s)
  
  def __call__(self, s: str):
    return self.parse(s)
  
  def do(self, func: callable):
    p = copy.copy(self)
    p.func = func
    return p

  def __repr__(self):
    return f"Parser({self.__f})"

  def __add__(self, other: "Parser"):
    return Sequence(self, other)
  
  def __or__(self, other: "Parser"):
    return Choice(self, other)
  
  def repeat(self, lower: int, upper: int):
    return Repeat(self, lower, upper)
  
  def optional(self):
    return Repeat(self, 0, 1)

class Repeat(Parser):
  def __init__(self, parser: Parser, lower: int = 0, upper: int = None):
    super().__init__()
    self.parser = parser
    self.lower = lower
    self.upper = upper

  def parse(self, s: str):
    result = []
    while True:
      try:
        value, s = self.parser.parse(s)
        result.append(value)
      except:
        break
    if len(result) < self.lower:
      raise ParserException(f"Expected at least {self.lower} repetitions, got {len(result)}")
    if self.upper is not None and len(result) > self.upper:
      raise ParserException(f"Expected at most {self.upper} repetitions, got {len(result)}")
    return self.func(result), s
  
  def __repr__(self):
    return f"Repeat({self.parser}, {self.lower}, {self.upper})"

class Choice(Parser):
  def __init__(self, *parsers: Parser):
    super().__init__()
    self.parsers = parsers

  def parse(self, s: str):
    for parser in self.parsers:
      try:
        value, s = parser.parse(s)
        return self.func(value), s
      except ParserException:
        pass
      except Exception as e:
        raise e
    raise ParserException(f"None of the parsers matched {s}")
  
  def __repr__(self):
    return f"Choice({', '.join(map(str, self.parsers))})"

class Empty(Parser):
  def __init__(self):
    super().__init__()

  def parse(self, s: str):
    return (None, s)
  
  def __repr__(self):
    return "Empty()"

class Terminal(Parser):
  def __init__(self, value: str):
    super().__init__()
    self.value = value

  def parse(self, s: str):
    if s.startswith(self.value):
      return (self.func(self.value), s[len(self.value):])
    else:
      raise ParserException(f"Expected \"{self.value}\", got \"{s[:len(self.value)]}\"")
  
  def __repr__(self):
    return f"Terminal({self.value})"

class Regex(Parser):
  def __init__(self, regex: str):
    super().__init__()
    self.regex = regex

  def parse(self, s: str):
    match = re.match(self.regex, s)
    if match:
      return self.func(match.group(0)), s[len(match.group(0)):]
    else:
      raise ParserException(f"Expected \"{self.regex}\", got \"{s[:len(self.regex)]}\"")
  
  def __repr__(self):
    return f"Regex({self.regex})"

class Sequence(Parser):
  def __init__(self, *parsers: Parser):
    super().__init__()
    self.parsers = parsers

  def parse(self, s: str):
    result = []
    for parser in self.parsers:
      value, s = parser.parse(s)
      result.append(value)
    return self.func(result), s
  
  def __repr__(self):
    return f"Sequence({', '.join(map(str, self.parsers))})"

class Forward(Parser):
  def __init__(self):
    super().__init__()
    self.parser = Empty()

  def define(self, parser: Parser):
    self.parser = parser

  def parse(self, s: str):
    return self.parser.parse(s)
  
  def __repr__(self):
    return "Forward()"
