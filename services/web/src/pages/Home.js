import BlogList from "./BlogList";
import useFetch from "../useFetch";
import { api } from "../api";

const Home = () => {
  const { error, isPending, data: blogs } = useFetch((opts) => api.listBlogs(opts), []);

  return (
    <div className="home">
      { error && <div>{ error }</div> }
      { isPending && <div>Loading...</div> }
      { blogs && blogs.length === 0 && <div>No blogs yet. Be the first to write one!</div> }
      { blogs && <BlogList blogs={blogs} /> }
    </div>
  );
}

export default Home;
