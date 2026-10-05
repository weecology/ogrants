# Proposal: Multi-Author Support for ogrants

## Overview

This proposal outlines a plan to add proper multi-author support to ogrants, allowing each author to have their own ORCID, institution, and other metadata. The current system stores authors as a single concatenated string, which breaks ORCID linking and prevents proper attribution.

## Current Problem

When a grant has multiple authors, the current system requires:
```yaml
author: "Michelle Barker and Daniel S. Katz"
ORCID: "0000-0002-3623-172X and 0000-0001-5934-7525"
```

This causes issues:
1. The ORCID link in `grant.html` constructs `https://orcid.org/0000-0002-3623-172X and 0000-0001-5934-7525` - a broken URL
2. No way to associate each ORCID with the correct author
3. Each author can only have one shared institution
4. The `extract_name()` function in R produces incorrect filenames for multi-author entries

## Proposed Solution

### New Data Model

Change from a single `author` field to an `authors` array:

```yaml
# Old format (single author - still supported)
layout: grant
title: "My Grant"
author: "Jane Smith"
ORCID: "0000-0001-2345-6789"
institution: "University of Example"

# New format (multiple authors)
layout: grant
title: "Our Collaborative Grant"
authors:
  - name: Michelle Barker
    orcid: 0000-0002-3623-172X
    institution: Research Software Alliance
  - name: Daniel S. Katz
    orcid: 0000-0001-5934-7525
    institution: University of Illinois Urbana-Champaign
  - name: Third Author
    institution: Another University
    # orcid is optional
```

### Backward Compatibility

Templates will check for both formats:
- If `authors` array exists → use new multi-author display
- Else if `author` string exists → use legacy single-author display

This allows gradual migration without breaking existing grants.

---

## Implementation Plan

### Phase 1: Template Updates (Low Risk)

**File: `_layouts/grant.html`**

Replace the current author section (lines 8-13):
```liquid
<dt>Author</dt>
{% if page.ORCID %}
  <dd>{{ page.author }} (<a href="https://orcid.org/{{ page.ORCID }}">ORCID</a>)</dd>
{% else %}
  <dd>{{ page.author }}</dd>
{% endif %}
```

With:
```liquid
<dt>Author{% if page.authors.size > 1 %}s{% endif %}</dt>
{% if page.authors %}
  {% for author in page.authors %}
    <dd>
      {{ author.name }}
      {% if author.institution %} ({{ author.institution }}){% endif %}
      {% if author.orcid %} <a href="https://orcid.org/{{ author.orcid }}">[ORCID]</a>{% endif %}
    </dd>
  {% endfor %}
{% elsif page.author %}
  <!-- Legacy single-author format -->
  {% if page.ORCID %}
    <dd>{{ page.author }} (<a href="https://orcid.org/{{ page.ORCID }}">ORCID</a>)</dd>
  {% else %}
    <dd>{{ page.author }}</dd>
  {% endif %}
{% endif %}
```

**File: `grants-01-all.md` (and similar list pages)**

Update table display to handle both formats:
```liquid
{% if grant.authors %}
  {{ grant.authors | map: "name" | join: ", " }}
{% else %}
  {{ grant.author }}
{% endif %}
```

### Phase 2: Form Updates (Medium Complexity)

**File: `_includes/add_form.html`**

Add JavaScript for dynamic author fields:

```html
<div id="authors-container">
  <div class="author-entry" data-author-index="0">
    <h4>Author 1</h4>
    <input type="text" name="authors[0][name]" placeholder="Author name" required>
    <input type="text" name="authors[0][institution]" placeholder="Institution">
    <input type="text" name="authors[0][orcid]" placeholder="ORCID (optional)">
    <input type="text" name="authors[0][website]" placeholder="Website (optional)">
  </div>
</div>
<button type="button" id="add-author">+ Add Another Author</button>

<script>
let authorCount = 1;
document.getElementById('add-author').addEventListener('click', function() {
  const container = document.getElementById('authors-container');
  const newEntry = document.createElement('div');
  newEntry.className = 'author-entry';
  newEntry.innerHTML = `
    <h4>Author ${authorCount + 1}</h4>
    <input type="text" name="authors[${authorCount}][name]" placeholder="Author name" required>
    <input type="text" name="authors[${authorCount}][institution]" placeholder="Institution">
    <input type="text" name="authors[${authorCount}][orcid]" placeholder="ORCID (optional)">
    <input type="text" name="authors[${authorCount}][website]" placeholder="Website (optional)">
    <button type="button" class="remove-author">Remove</button>
  `;
  container.appendChild(newEntry);
  authorCount++;
});

document.addEventListener('click', function(e) {
  if (e.target.classList.contains('remove-author')) {
    e.target.parentElement.remove();
  }
});
</script>
```

### Phase 3: R Processing Updates

**File: `R/form-data-functions.R`**

Update `create_grant_data()` to handle authors array:

```r
create_grant_data <- function(dat, grant_file)
{
    # Build authors array
    authors <- list()
    if (!is.null(dat$authors)) {
        for (i in seq_along(dat$authors)) {
            author_entry <- list(name = dat$authors[[i]]$name)
            if (!is.null(dat$authors[[i]]$institution) && dat$authors[[i]]$institution != "") {
                author_entry$institution <- dat$authors[[i]]$institution
            }
            if (!is.null(dat$authors[[i]]$orcid) && dat$authors[[i]]$orcid != "") {
                author_entry$orcid <- dat$authors[[i]]$orcid
            }
            authors[[i]] <- author_entry
        }
    }

    grant_data <- list(
        layout = "grant",
        title = dat$title,
        authors = authors,
        year = dat$year,
        link = dat$link,
        funder = dat$funder,
        program = if (dat$program != "") dat$program else NULL,
        discipline = dat$discipline,
        status = tolower(dat$status)
    )

    grant_data
}
```

Update `extract_name()` to use first author for filename:

```r
extract_name <- function(dat)
{
    # For new format with authors array
    if (!is.null(dat$authors) && length(dat$authors) > 0) {
        author <- dat$authors[[1]]$name
    } else {
        # Legacy format
        author <- dat$author
    }

    # Extract first and last name from single author string
    parts <- strsplit(trimws(author), "\\s+")[[1]]
    first_name <- tolower(parts[1])
    last_name <- tolower(parts[length(parts)])

    paste0(last_name, "_", first_name)
}
```

Update `create_author_data()` to create files for each author:

```r
create_author_files <- function(dat)
{
    if (!is.null(dat$authors)) {
        for (author in dat$authors) {
            author_data <- data.frame(
                name = author$name,
                institution = if (!is.null(author$institution)) author$institution else "",
                orcid = if (!is.null(author$orcid)) author$orcid else "",
                website = if (!is.null(author$website)) author$website else ""
            )
            author_file <- create_author_filename_from_name(author$name)
            if (!file.exists(author_file)) {
                write_yaml_file(author_data, author_file)
            }
        }
    }
}
```

### Phase 4: Validation Updates

**File: `tests/validate_links.py`**

Minor update to handle both formats when reporting errors:

```python
def get_author_display(grant):
    """Get author name(s) for display in error messages"""
    if 'authors' in grant and grant['authors']:
        return ', '.join(a.get('name', 'Unknown') for a in grant['authors'])
    return grant.get('author', 'Unknown')
```

### Phase 5: Data Migration

Create a migration script to convert existing grants. This can be done incrementally.

**Migration Strategy Options:**

1. **All at once**: Run a script to convert all 303 grants
2. **On-demand**: Convert grants as they're edited
3. **Hybrid**: Convert programmatically where format is clear, manually review ambiguous cases

**Sample migration script (Python):**

```python
import os
import re
import yaml

def migrate_grant(filepath):
    with open(filepath, 'r') as f:
        content = f.read()

    # Parse YAML frontmatter
    match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not match:
        return False

    data = yaml.safe_load(match.group(1))

    # Skip if already migrated
    if 'authors' in data:
        return False

    # Skip if no author field
    if 'author' not in data:
        return False

    # Parse author string
    author_str = data['author']
    orcid_str = data.get('ORCID', '')
    institution = data.get('institution', '')

    # Split authors (handle "and" and comma separators)
    if ' and ' in author_str:
        author_names = [a.strip() for a in author_str.split(' and ')]
    elif ',' in author_str:
        author_names = [a.strip() for a in author_str.split(',')]
    else:
        author_names = [author_str]

    # Parse ORCIDs (try to match count with authors)
    orcids = []
    if orcid_str:
        # Handle various formats
        orcid_str = orcid_str.replace('https://orcid.org/', '')
        if ' and ' in orcid_str:
            orcids = [o.strip() for o in orcid_str.split(' and ')]
        elif ';' in orcid_str:
            orcids = [o.strip().rstrip(';') for o in orcid_str.split(';') if o.strip()]
        else:
            orcids = [orcid_str]

    # Build authors array
    authors = []
    for i, name in enumerate(author_names):
        author = {'name': name}
        if i == 0 and institution:
            author['institution'] = institution
        if i < len(orcids) and orcids[i]:
            author['orcid'] = orcids[i]
        authors.append(author)

    # Update data
    data['authors'] = authors
    del data['author']
    if 'ORCID' in data:
        del data['ORCID']
    # Keep institution at grant level for now, or remove if desired

    # Write back
    new_content = '---\n' + yaml.dump(data, default_flow_style=False, allow_unicode=True) + '---\n'

    with open(filepath, 'w') as f:
        f.write(new_content)

    return True
```

---

## Estimated Effort

| Phase | Description | Effort |
|-------|-------------|--------|
| 1 | Template updates | 1-2 hours |
| 2 | Form updates (HTML + JS) | 2-3 hours |
| 3 | R processing updates | 2-3 hours |
| 4 | Validation updates | 30 minutes |
| 5 | Migration script + review | 2-4 hours |
| **Total** | | **8-13 hours** |

## Risk Assessment

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Breaking existing grants | Low | Backward-compatible templates |
| Form submission issues | Medium | Test with Netlify Forms sandbox |
| ORCID format variations | Medium | Normalize during migration |
| Merge conflicts during migration | Low | Migrate in single PR |

## Testing Plan

1. Create test grant files with new format
2. Verify templates render correctly for both formats
3. Test form submission with multiple authors
4. Run link validation on migrated files
5. Visual review of grant list pages

## Questions for Maintainer

1. Should institution be per-author only, or also kept at grant level (for the submitting institution)?
2. Should we limit the number of authors in the form (e.g., max 10)?
3. Preference for migration approach (all at once vs. incremental)?
4. Should author files (`_authors/*.md`) also store ORCID? (Currently they don't)
5. Any preference on how to display multiple authors in the grants list table?

---

## Conclusion

Adding multi-author support is very feasible with the changes outlined above. The backward-compatible approach means existing grants continue to work while new submissions use the improved format. Migration can happen at whatever pace is comfortable.

I'm happy to submit a PR implementing any or all of these changes if you'd like to move forward.
