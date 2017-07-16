---
layout: default
title: Home
---

An increasing number of researchers are sharing their grant proposals
openly. They do this to open up science so that all stages of the process can
benefit from better interaction and communication and to provide examples for
younger scientists writing grants. This is a list of some of these proposals to
help you find them.



<table id='sTable'>
<tr>
<th nowrap onclick="sort(0)"> Year <i class="fa fa-sort" aria-hidden="true"></i> </th>
<th nowrap onclick="sort(1)"> Funder <i class="fa fa-sort" aria-hidden="true"></i></th>
<th nowrap onclick="sort(2)"> Title <i class="fa fa-sort" aria-hidden="true"></i></th>
<th nowrap onclick="sort(3)"> Funded <i class="fa fa-sort" aria-hidden="true"></i></th>
</tr>

{% for grant in site.grants %}
  <tr>
    <td>{{ grant.year }}</td>
	<td>{{ grant.funder }}</td>
	<td><a href="{{ grant.link }}">{{ grant.title }}</a> <small> by {{ grant.author }}</small></td>
	{% if grant.status == 'funded' %}
	  <td>Yes</td>
	{% else %}
	  <td>No</td>
	{% endif %}
  </tr>
{% endfor %}












<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">

<script>
// sortTable function from https://www.w3schools.com/howto/howto_js_sort_table.asp
function sort(n) {
  var table, rows, s, i, x, y, switchTrue, dir, switchcount = 0;
  table = document.getElementById("sTable");
  s = true;
  dir = "asc"; 
  while (s) {
    s = false;
    rows = table.getElementsByTagName("TR");
    for (i = 1; i < (rows.length - 1); i++) {
      switchTrue = false;
      x = rows[i].getElementsByTagName("TD")[n];
      y = rows[i + 1].getElementsByTagName("TD")[n];
      if (dir == "asc") {
        if (x.innerHTML.toLowerCase() > y.innerHTML.toLowerCase()) {
          switchTrue= true;
          break;
        }
      } else if (dir == "desc") {
        if (x.innerHTML.toLowerCase() < y.innerHTML.toLowerCase()) {
          switchTrue = true;
          break;
        }
      }
    }
    if (switchTrue) {
      rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
      s = true;
      switchcount ++; 
    } else {
  	  if (switchcount == 0 && dir == "asc") {
        dir = "desc";
        s = true;
      }
    }
  }
}
</script>

