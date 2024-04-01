from typing import Union
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
    self.func = func
    return self

  def __add__(self, other: "Parser"):
    return Sequence(self, other)
  
  def __or__(self, other: "Parser"):
    return Choice(self, other)
  
  def repeat(self, lower: int, upper: int):
    return Repeat(self, lower, upper)

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
    if self.upper and len(result) > self.upper:
      raise ParserException(f"Expected at most {self.upper} repetitions, got {len(result)}")
    return self.func(result), s

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

class Empty(Parser):
  def __init__(self):
    super().__init__()

  def parse(self, s: str):
    return (None, s)

class Terminal(Parser):
  def __init__(self, value: str):
    super().__init__()
    self.value = value

  def parse(self, s: str):
    if s.startswith(self.value):
      return (self.func(self.value), s[len(self.value):])
    else:
      raise ParserException(f"Expected \"{self.value}\", got \"{s[:len(self.value)]}\"")

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

class Forward(Parser):
  def __init__(self):
    super().__init__()
    self.parser = Empty()

  def define(self, parser: Parser):
    self.parser = parser

  def parse(self, s: str):
    return self.parser.parse(s)
