---
layout: page
title: Add a grant
---

Adding a grant to this site requires two (or three) things:

### 1. Post the grant online

This site doesn't host grants, it just provides links to them. We
recommend [Zenodo](https://zenodo.org/) and [Figshare](https://figshare.com/) as
good options for posting grants because they are archival and so shouldn't
result in broken links anytime in the near future.

### 2. Add information about the grant

Information for each grant is stored as YAML with fields for each key
piece of information. E.g.,

```
---
layout: grant
title: Moore Investigator in Data Driven Discovery
author: Ethan P. White
ORCID: 0000-0001-6728-7745
year: 2014
link: https://doi.org/10.6084/m9.figshare.1189330
funder: Moore Foundation
program: Data Driven Discovery Investigators
discipline: data science
status: funded
---
```

The items to the right of the `:` on each line should be changed to match the
grant you want to add. To get this added to the site there are three options:

1. Submit a pull request that adds the above information to a file named
   `lastname_firstname_year.md` in the `_grants` folder of
   the [GitHub repository]({{ site.github.repo }}). The `lastname` and
   `firstname` should be those for the lead PI. In the case of multiple grants
   by the same PI for the same year append letters in order to the date, e.g.,
   `white_ethan_2026a.md`.
2. [Open an issue](https://github.com/weecology/ogrants/issues/new) and paste
   the filled out YAML into that issue.
3. [Email us](mailto:ogrants@weecology.org) the information.

### 3. Add information about the author

If you want you can also add information about the author in the form:

```
---
name: Ethan P. White
ORCID: 0000-0001-6728-7745
institution: University of Florida
website: http://ethanwhite.org
twitter: ethanwhite
---
```

This can be submitted along with the grant information if you're using an issue
or email. If you're submitting a pull request it should be placed in a file
named `lastname_firstname.md` in the `_authors` directory.
