import io

class TemplateParser:
  def __init__(self, **kwargs):
    self.stack = []
    
    self.opening_bracket = kwargs.get("opening_bracket", "{{")
    self.closing_bracket = kwargs.get("closing_bracket", "}}")
  
  def parse(self, text):
    opening_bracket = self.opening_bracket
    closing_bracket = self.closing_bracket
    
    self.stack.append(Template())
    line_no     = 1
    idx         = 0
    newline_idx = 0
    
    while True:
      idx1 = text.find(opening_bracket, idx)
      idx2 = text.find(closing_bracket, idx1)
      
      # update line number
      while True:
        next_newline = text.find("\n", newline_idx)
        if next_newline > idx1 or next_newline == -1:
          break
        
        line_no += 1
        newline_idx = next_newline + 1
    
      
      if idx1 == -1:
        # There's no remaining opening bracket
        self.append_literal(text[idx:])
        break
      
      self.append_literal(text[idx:idx1])
      
      directive_text = text[idx1 + len(opening_bracket): idx2].strip()
      self.append_directive(directive_text, line_no, idx1 - newline_idx)
      idx = idx2 + len(closing_bracket)
    
    root = self.stack.pop()
    
    if isinstance(root, (IfDirective, ElseDirective)):
      raise ValueError(f"'if' directive not closed by an 'endif' at {root.line}{root.col}")
      
    if isinstance(root, ForDirective):
      raise ValueError(f"'for' directive not closed by an 'endfor' at {root.line}{root.col}")
    
    return root
  
  def append_directive(self, text, line, col):
    if text.startswith("#"):
      # This is a comment, we don't need to do anything about it
      return
    
    if text.startswith("if "):
      return self.append_if(text, line, col)
      
    if text.startswith("ifdef "):
      return self.append_ifdef(text, line, col)
      
    if text.startswith("ifndef "):
      return self.append_ifndef(text, line, col)
    
    if text.startswith("elif "):
      return self.append_elif(text, line, col)
    
    if text.startswith("for "):
      return self.append_for(text, line, col)
      
    if text == "else":
      return self.append_else(line, col)
    
    if text == "endif":
      return self.append_endif(line, col)
    
    if text == "endfor":
      return self.append_endfor(line, col)
    
    return self.append_expression(text, line, col)
  
  def append_literal(self, text):
    # Remove newline charactes (windows or linux) from the end of the literal if they are there.
    if text.endswith('\n'):
      text = text[:-1]
    elif text.endswith('\r\n'):
      text = text[:-2]
    self.stack[-1].children.append(Literal(text))
    
  def append_expression(self, text, line, col):
    self.stack[-1].children.append(Expression(text, line, col))
    
  def append_if(self, text, line, col):
    tag = IfDirective(text, line, col)
    self.stack[-1].children.append(tag)
    self.stack.append(tag)  
    
  def append_ifdef(self, text, line, col):
    tag = IfdefDirective(text, line, col)
    self.stack[-1].children.append(tag)
    self.stack.append(tag)
    
  def append_ifndef(self, text, line, col):
    tag = IfdefDirective(text, line, col)
    self.stack[-1].children.append(tag)
    self.stack.append(tag.elseBranch)
    
  def append_for(self, text, line, col):
    tag = ForDirective(text, line, col)
    self.stack[-1].children.append(tag)
    self.stack.append(tag)
    
  def append_elif(self, text, line, col):
    head = self.stack.pop()
    if not isinstance(head, IfDirective):
      raise ValueError(f"No matching 'if' directive for 'elif' directive at {line}:{col}")
    
    tag = IfDirective(text, line, col)
    head.elseBranch.children.append(tag)
    self.stack.append(tag)
  
  def append_else(self, line, col):
    head = self.stack.pop()
    
    if not isinstance(head, (IfDirective, IfdefDirective)):
      raise ValueError(f"No matching 'if' or 'ifdef' directive for 'else' directive at {line}:{col}")
    
    tag = head.elseBranch
    self.stack.append(tag)
  
  def append_endif(self, line, col):
    head = self.stack.pop()
    if not isinstance(head, (IfDirective, ElseDirective, IfdefDirective)):
      raise ValueError(f"No matching 'if' or 'ifdef' directive for 'endif' directive at {line}:{col}")
  
  def append_endfor(self, line, col):
    head = self.stack.pop()
    if not isinstance(head, ForDirective):
      raise ValueError(f"No matching 'for' directive for 'endfor' directive at {line}:{col}")
  

class Template:
  def __init__(self):
    self.children = []
  
  def dumps(self, **context):
    with io.StringIO() as oup:
      self.dump(oup, **context)
      return oup.getvalue()
    
  
  def dump(self, output, **context):
    for child in self.children:
      child.evaluate(output, context)


class Literal:
  def __init__(self, text):
    self.text = text
  
  def evaluate(self, output, context):
    output.write(self.text)


class Expression:
  def __init__(self, expression, line, col):
    self.expression = expression
    self.line = line
    self.col = col
  
  def evaluate(self, output, context):
    value = str(eval(self.expression, context))
    output.write(value)


class IfdefDirective:
  def __init__(self, arg, line, col):
    self.children   = []
    self.elseBranch = ElseDirective()
    
    if arg.startswith("ifdef "):
      self.arg = arg[6:].strip()
    elif arg.startswith("ifndef "):
      self.arg = arg[7:].strip()
    else:
      raise ValueError(f"Error parsing ifdef/ifndef directive at {line}{col}")
  
  def evaluate(self, output, context):
    if self.arg in context:
      for child in self.children:
        child.evaluate(output, context)
    else:
      self.elseBranch.evaluate(output, context)


class IfDirective:
  def __init__(self, condition, line, col):
    self.children   = []
    self.elseBranch = ElseDirective()
    
    if condition.startswith("if "):
      self.condition = condition[3:].strip()
    elif condition.startswith("elif "):
      # Parent is an else branch, this is the only child
      self.condition = condition[5:].strip()
    else:
      raise ValueError(f"Error parsing if/elif directive at {line}{col}")
  
  def evaluate(self, output, context):
    result = bool( eval(self.condition, context) )
    
    if result:
      for child in self.children:
        child.evaluate(output, context)
    else:
      self.elseBranch.evaluate(output, context)


class ElseDirective:
  def __init__(self):
    self.children = []

  def evaluate(self, output, context):
    for child in self.children:
      child.evaluate(output, context)


class ForDirective:
  def __init__(self, expr, line, col):
    self.children = []
    self.generator = ForDirective.compute_generator(expr, line, col)
  
  @staticmethod
  def compute_generator(expr, line, col):
    if not expr.startswith("for "):
      raise ValueError("Failed parsing 'for' directive at {line}:{col}")
    
    args, right = expr[4:].split(" in ")
    args = map(lambda s: s.strip(" ()"), args.split(","))
    args = ", ".join([f'"{arg}": {arg}' for arg in args])
    return f"[{{{args}}} {expr}]"
    
  def evaluate(self, output, context):
    results = eval(self.generator, context)
    for k, result in enumerate(results):
      for child in self.children:
        child.evaluate(output, {** context, ** result})

