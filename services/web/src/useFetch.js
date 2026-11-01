import { useState, useEffect } from 'react';

// `fetcher` receives { signal } and returns a promise, e.g. (opts) => api.getBlog(id, opts)
const useFetch = (fetcher, deps = []) => {
  const [data, setData] = useState(null);
  const [isPending, setIsPending] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const abortCont = new AbortController();
    setIsPending(true);

    fetcher({ signal: abortCont.signal })
      .then((data) => {
        setData(data);
        setError(null);
        setIsPending(false);
      })
      .catch((err) => {
        if (err.name === 'AbortError') return;
        setError(err.message);
        setIsPending(false);
      });

    return () => abortCont.abort();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps);

  return { data, isPending, error };
};

export default useFetch;
