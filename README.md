# Sjabloontje
Minimalistic template engine for Python.

## Example

```
template = TemplateParser().parse("""
{{name}}'s inventory:
{{ for (title, copies) in inventory }}
 * {{if copies > 1}}{{ copies }} copies of{{else}}A single copy of{{endif}} {{title}}
{{ endfor }}
""")

print(template.dumps(name = "btoth", inventory = [("Orwell's 1984", 2), ("the Lord of the Rings", 2)]))
```

Which will result in:
```
btoth's inventory:
 * 2 copies of Orwell's 1983
 * A single copy of the Lord of the Rings
```

## Directives

All directives are surrounded by double curly braces (or whatever kind of parentheses you prefer). Cuurently we have the following directives:
  * Expressions: If the directive doesn't start with a keyword (like the rest of them), the directive will be evaluated as a python expression using the variables provided as a context.
  * `for` and `endfor`: The part of the template between the 'for' and the 'endfor' directive will be evaluated in a loop, just as it was in a plain Python for loop.
  * `if`, `elif`, `else`, `endif`: Evaluate the part of the template conditionally.
  * `ifdef`, `ifndef`, `else`, `endif`: Evaluate the part of the template conditional on if a parameter is defined.

## Filters, pipes, and othe stuff like that

None. You can pass in any kinds of objects (including functions) into the context, so basically you can have any python code executed as part of your template. Internally I'm using python's `eval` function, so you can go wild by using all sorts of generator expressions. 

## Dependencies
None.
