---
layout: page
title: Add a grant
---

## Simple

Fill out the form below.
You can either post your grant elsewhere (we recommend [Zenodo](https://zenodo.org/)) and provide a link to the file or upload a pdf of the grant using the button at the bottom of the form.

New grants are artisanally hand processed so it might take a little while for them to show up on the site.

{% include add_form.html %}

## Submit Directly To GitHub

If you're familiar with GitHub you can skip the form and submit a pull request to directly add your grant to the site (or open an issue with the necessary information).

### Grant information

Information for each grant is stored as YAML with fields for each key piece of information.

```markdown
---
layout: grant
title: "Moore Investigator in Data Driven Discovery"
author: "Ethan P. White"
ORCID: 0000-0001-6728-7745
year: 2014
link: [https://doi.org/10.6084/m9.figshare.1189330]
link_name: [Proposal]
funder: "Moore Foundation"
program: "Data Driven Discovery Investigators"
discipline: data science
status: funded
---
```

The items to the right of the `:` on each line should be changed to match the grant you want to add.
Items in `[]` can be comma delimited lists to allow multiple documents to be included.

You can submit a pull request that adds the above information to a file named `lastname_firstname_year.md` in the `_grants` folder of the [GitHub repository]({{ site.github.repo }}).
The `lastname` and `firstname` should be those for the lead PI.
In the case of multiple grants by the same PI for the same year append letters in order to the date,
e.g. `white_ethan_2026a.md`.

Or just [open an issue](https://github.com/weecology/ogrants/issues/new) and paste the filled out YAML into that issue.

### Author information

If you want you can also add information about the author in the form:

```markdown
---
name: Ethan P. White
ORCID: 0000-0001-6728-7745
institution: University of Florida
website: http://ethanwhite.org
twitter: ethanwhite
---
```

This can be submitted along with the grant information if you're using an issue.
If you're submitting a pull request it should be placed in a file named `lastname_firstname.md` in the `_authors` directory.
