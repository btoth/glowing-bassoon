from sjabloontje import TemplateParser

template = TemplateParser().parse("""
{{name}}'s inventory:
{{ for (title, copies) in inventory }}
 * {{if copies > 1}}{{ copies }} copies of{{else}}A single copy of{{endif}} {{title}}
{{ endfor }}
""")

print(template.dumps(name = "btoth", inventory = [("Orwell's 1984", 2), ("the Lord of the Rings", 2)]))