import { useHistory, useParams } from "react-router-dom";
import useFetch from "../useFetch";
import { AuthContext } from '../context/AuthContext';
import React, { useContext, useState } from "react";
import { api } from "../api";

const replaceNewlinesWithBreaks = (text) => {
  return text.split("\n").map((paragraph, index) => (
    <React.Fragment key={index}>
      {index > 0 && <br />}
      {paragraph}
    </React.Fragment>
  ));
};

const BlogDetails = () => {
  const { id } = useParams();
  const { data: blog, error, isPending } = useFetch((opts) => api.getBlog(id, opts), [id]);
  const { user } = useContext(AuthContext);
  const [deleteError, setDeleteError] = useState(null);
  const history = useHistory();

  // The API also enforces this; hiding the button is just UX.
  const isOwner = blog && user && blog.author.id === user.id;

  const handleDelete = () => {
    api.deleteBlog(blog.id)
      .then(() => history.push('/home'))
      .catch((err) => setDeleteError(err.message));
  };

  return (
    <div className="blog-details">
      {isPending && <div>Loading...</div>}
      {error && <div>{error}</div>}
      {blog && (
        <article>
          <h2>{blog.title}</h2>
          <p>Written by {blog.author.name}</p>
          <div className="blog-body">{replaceNewlinesWithBreaks(blog.body)}</div>
          {isOwner && <button onClick={handleDelete}>Delete</button>}
          {deleteError && <p className="red-alert">{deleteError}</p>}
        </article>
      )}
    </div>
  );
}

export default BlogDetails;
