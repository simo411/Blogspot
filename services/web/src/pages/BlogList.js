import React from 'react';
import { Link } from 'react-router-dom';

const CATEGORIES = ['Today', 'Yesterday', 'Previous 7 days', 'Previous 30 days', 'Older'];

const truncateText = (text, maxLength = 200) =>
  text.length <= maxLength ? text : text.slice(0, maxLength) + '...';

// The API sends naive UTC timestamps (MySQL DATETIME); mark them as UTC so the
// browser converts to the reader's local time.
const parseDate = (value) => new Date(/Z|[+-]\d\d:\d\d$/.test(value) ? value : `${value}Z`);

const startOfDay = (d) => new Date(d.getFullYear(), d.getMonth(), d.getDate());

// Whole days between the post and today, in the reader's timezone.
// (v1 mutated one shared Date inside the filter, so the 7/30-day buckets drifted.)
const categoryFor = (date, today) => {
  const days = Math.round((today - startOfDay(date)) / 86_400_000);
  if (days <= 0) return 'Today';
  if (days === 1) return 'Yesterday';
  if (days <= 7) return 'Previous 7 days';
  if (days <= 30) return 'Previous 30 days';
  return 'Older';
};

const BlogList = ({ blogs }) => {
  const today = startOfDay(new Date());
  const grouped = {};
  blogs.forEach((blog) => {
    const category = categoryFor(parseDate(blog.created_at), today);
    (grouped[category] = grouped[category] || []).push(blog);
  });

  return (
    <div className="blog-list">
      {CATEGORIES.filter((c) => grouped[c]).map((category) => (
        <div key={category}>
          <h3>{category}</h3>
          {grouped[category].map((blog) => (
            <div className="blog-preview" key={blog.id}>
              <Link to={`/blogs/${blog.id}`}>
                <h2>{blog.title}</h2>
                <p>{truncateText(blog.body)}</p>
                <div className="date">
                  by {blog.author.name} on {parseDate(blog.created_at).toLocaleDateString()}
                </div>
              </Link>
              <div className="author-info">
                <div className="user-circle" title={blog.author.name}>
                  {blog.author.avatar ? (
                    <img
                      src={`${process.env.PUBLIC_URL}/images/${blog.author.avatar}-user.jpg`}
                      alt={blog.author.name}
                    />
                  ) : (
                    <b>{blog.author.name.charAt(0).toUpperCase()}</b>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      ))}
    </div>
  );
};

export default BlogList;
