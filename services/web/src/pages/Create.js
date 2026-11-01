import React, { useState } from 'react';
import { useHistory } from 'react-router-dom';
import { api } from '../api';

const Create = () => {
  const [title, setTitle] = useState('');
  const [body, setBody] = useState('');
  const [error, setError] = useState(null);
  const [isPending, setIsPending] = useState(false);
  const history = useHistory();

  const handleSubmit = (e) => {
    e.preventDefault();
    setIsPending(true);
    // No author fields: the API takes the author from the login token.
    api.createBlog({ title, body })
      .then(() => history.push('/home'))
      .catch((err) => {
        setError(err.message);
        setIsPending(false);
      });
  };

  return (
    <div className="create">
      <h2>Add a New Blog</h2>
      <form onSubmit={handleSubmit}>
        <label>Blog title:</label>
        <input
          type="text"
          required
          maxLength={200}
          value={title}
          onChange={(e) => setTitle(e.target.value)}
        />
        <label>Blog body:</label>
        <textarea
          required
          value={body}
          onChange={(e) => setBody(e.target.value)}
        ></textarea>
        <button disabled={isPending}>{isPending ? 'Adding...' : 'Add Blog'}</button>
        {error && <p className="red-alert">{error}</p>}
      </form>
    </div>
  );
}

export default Create;
