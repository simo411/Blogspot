import React, { useState, useEffect } from "react";
import { Link } from 'react-router-dom';


const Start = () => {
  const [showText, setShowText] = useState(false);

  useEffect(() => {
    setShowText(true);
  }, []);

  return (
    <div className={`start ${showText ? 'show-text' : ''}`}>
      <div className="image-container">
        <img src= {process.env.PUBLIC_URL +"/images/blogspot.png"} alt="blogspot" className="blogspot" />
      </div>

      <h1 >Welcome to Blogspot: Exploring the World Through Words </h1>
      <p>
        Embark on a captivating journey of discovery and inspiration with Blogspot, your ultimate destination for thought-provoking narratives, insightful perspectives, and a treasure trove of knowledge. In this digital haven, we bring you an exquisite collection of blogs that traverse the spectrum of human experience, encapsulating tales of adventure, wisdom, creativity, and reflection.
      </p>
      <br />
      <h3>
        At Blogspot, we believe in the power of words to transcend boundaries, to ignite conversations, and to foster a global community bonded by the love for storytelling. Our platform serves as a melting pot of diverse voices, where writers from all corners of the globe converge to share their unique stories, visions, and insights. Whether you're an avid explorer seeking tales of far-off lands, a curious mind hungry for knowledge, or a creative spirit in search of artistic musings, Blogspot has something for you.
      </h3>
      <br />
      <h4>Step into Blogspot and let the journey begin. Your adventure in the realm of words awaits.</h4>
      <div className="start-button-container">
        <Link to="/login" className="get-started-button">Get Started <span>&#10148;</span></Link>
      </div>
    </div>


  );
}

export default Start;