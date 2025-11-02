# Jekyll Module to create category archive pages
#
# Shigeya Suzuki, November 2013
# Copyright notice (MIT License) attached at the end of this file
#

#
# This code is based on the following works:
#   https://gist.github.com/ilkka/707909
#   https://gist.github.com/ilkka/707020
#   https://gist.github.com/nlindley/6409459
#

#
# Archive will be written as #{archive_path}/#{category_name}/index.html
# archive_path can be configured in 'path' key in 'category_archive' of
# site configuration file. 'path' is default null.
#

module Jekyll

  # Generator class invoked from Jekyll
  class CategoryArchiveGenerator < Generator
    def generate(site)
      posts_group_by_category(site).each do |category, list|
        site.pages << CategoryArchivePage.new(site, archive_base(site), category, list)
      end
    end

    def posts_group_by_category(site)
      category_map = {}
      site.posts.each {|p| p.categories.each {|c| (category_map[c] ||= []) << p } }
      category_map
    end

    def archive_base(site)
      site.config['category_archive'] && site.config['category_archive']['path'] || ''
    end
  end

  # Actual page instances
  class CategoryArchivePage < Page
    ATTRIBUTES_FOR_LIQUID = %w[
      category,
      content
    ]

    def initialize(site, dir, category, posts)
      @site = site
      @dir = dir
      @category = category
      @category_dir_name = @category # require sanitize here
      @layout =  site.config['category_archive'] && site.config['category_archive']['layout'] || 'category_archive'
      self.ext = '.html'
      self.basename = 'index'
      self.content = <<-EOS
<!-- Working -->
{% for post in page.posts limit:1 %}
  {% if post.image.feature %}<div class="image-wrap">
    <img src="{{ site.url }}/images/{{ post.image.feature }}" alt="{{ post.title }} feature image" itemprop="primaryImageOfPage">
    {% if post.image.credit %}
      <span class="image-credit">Photo Credit: 
        <a href="{{ post.image.creditlink }}">{{ post.image.credit }}</a>
      </span>
    {% endif %}
  </div><!-- /.image-wrap -->
  {% endif %}
{% endfor %}

<div class="article-author-side">
  {% include _author-bio.html %}
</div>
<div id="index" itemprop="mainContentOfPage" itemscope itemtype="http://schema.org/Blog">
  <h1 itemprop="name">Archive for {{ page.category }}</h1>

{% for post in page.posts %}  
    <article itemscope itemtype="http://schema.org/BlogPosting" itemprop="blogPost">
      <h2 itemprop="headline">
        <a href="{{ site.url }}{{ post.url }}" rel="bookmark" title="{{ post.title }}">{{ post.title }}</a>
      </h2>
      <p itemprop="text">{% if post.description %}{{ post.description }}{% else %}{{ post.content | strip_html | strip_newlines | truncate: 120 }}{% endif %}</p>
    </article>
{% endfor %}

      EOS
      self.data = {
          'layout' => @layout,
          'type' => 'archive',
          'title' => "Category archive for #{@category}",
          'posts' => posts
      }
    end

    def render(layouts, site_payload)
      payload = {
          'page' => self.to_liquid,
          'paginator' => pager.to_liquid
      }.deep_merge(site_payload)
      do_layout(payload, layouts)
    end

    def to_liquid(attr = nil)
      self.data.deep_merge({
                               'content' => self.content,
                               'category' => @category
                           })
    end

    def destination(dest)
      File.join('/', dest, @dir, @category_dir_name, 'index.html')
    end

  end
end

# The MIT License (MIT)
#
# Copyright (c) 2013 Shigeya Suzuki
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
