---
layout: page
title: Grants by Program
---

{% comment %}
Code adapted from
https://codinfox.github.io/dev/2015/03/06/use-tags-and-categories-in-your-jekyll-based-github-pages/
{% endcomment %}

{% comment %}
=========================================
Collect and sort programs and display tags
=========================================
{% endcomment %}

{% assign programs = "" %}
{% for grant in site.grants %}
    {% assign program = grant.funder | append: ' - ' %}
    {% if grant.program != nil %}
        {% assign program = program | append: grant.program | join:'|' | append:'|' %}
    {% else %}
        {% assign program = program | append: '(N/A)' | join:'|' | append:'|' %}
    {% endif %}
	{% unless programs contains program %}
        {% assign programs = programs | append:program %}
	{% endunless %}
{% endfor %}
{% assign programs = programs | split:'|' | sort %}

<p>
{% for program in programs %}
	<a href="#{{ program | slugify }}" class="post-tag">{{ program }}</a>
{% endfor %}
</p>


{% comment %}
=========================
List all grants by program
=========================
{% endcomment %}

<p>
{% for program in programs %}
	<h3 id="{{ program | slugify }}">{{ program }}</h3>
	<ul>
	 {% for grant in site.grants %}
         {% assign myprogram = grant.funder | append: ' - ' %}
         {% if grant.program != nil %}
            {% assign myprogram = myprogram | append: grant.program %}
         {% else %}
            {% assign myprogram = myprogram | append: '(N/A)' %}
         {% endif %}
		 {% if myprogram == program %}
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
