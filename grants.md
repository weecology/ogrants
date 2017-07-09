---
layout: default
title: Grants
---

<table>
  <tr>
	<th>Year</th>
	<th>Funder</th>
	<th>Title</th>
	<th>Author</th>
  </tr>
{% for grant in site.grants %}
  <tr>
    <td>{{ grant.year }}</td>
	<td>{{ grant.funder }}</td>
	<td><a href="{{ grant.link }}">{{ grant.title }}</a></td>
    <td>{{ grant.author }}</td>
  </tr>
{% endfor %}

