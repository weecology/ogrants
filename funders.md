---
layout: page
title: Grants by Funder
---

{% comment %}
Code adapted from
https://codinfox.github.io/dev/2015/03/06/use-tags-and-categories-in-your-jekyll-based-github-pages/
{% endcomment %}

{% comment %}
=========================================
Collect and sort funders and display tags
=========================================
{% endcomment %}

{% assign funders = "" %}
{% for grant in site.grants %}
    {% assign funder = grant.funder | join:'|' | append:'|' %}
	{% unless funders contains funder %}
        {% assign funders = funders | append:funder %}
	{% endunless %}
{% endfor %}
{% assign funders = funders | split:'|' | sort %}

<p>
{% for funder in funders %}
	<a href="#{{ funder | slugify }}" class="post-tag">{{ funder }}</a>
{% endfor %}
</p>


{% comment %}
=========================
List all grants by funder
=========================
{% endcomment %}

<p>
{% for funder in funders %}
	<h3 id="{{ funder | slugify }}">{{ funder }}</h3>
	<ul>
	 {% for grant in site.grants %}
		 {% if grant.funder == funder %}
		 <li>
		 <a href="{{ grant.url }}">
		 {{ grant.title }}
		 </a>
 		 <small>{{ grant.author }}, {{ grant.year }}, <em>{{ grant.status }}</em></small>
		 </li>
		 {% endif %}
	 {% endfor %}
	</ul>
{% endfor %}
</p>
