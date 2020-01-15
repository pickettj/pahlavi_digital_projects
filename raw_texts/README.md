# Readme

- [OxGarage](https://oxgarage.tei-c.org/#): Convert MS Word document to XML (inter alia)

## Regex (of OxGarage normalized XMl document)

- Extra spaces: replace `<p>\s`
- Normalize folio numbers:
  - Find: `<hi rend="color\(FF0000\)">\[(K20_....)\]</hi>`
    - Remember escape characters for `( [`
  - Replace: `<pg fol="\1"/>`
- Break out into sections:
  - Find: `(<l>(\d{1,2}\.\d).+?)(<l>\d{1,2}\.\d)`
  - Replace: `<sec id="\2"> \1 </sec> \3`
  - (This gets half of them; probably a cleverer way to do it without two steps)
  - Find: `</sec>\s*(<l>(\d{1,2}\.\d).+?)<sec`
  - Replace: `</sec><sec id="\2">\1</sec><sec`
    - Leaves off the last instance.
