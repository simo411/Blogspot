import React, { useContext } from 'react';
import { AuthContext } from '../context/AuthContext';
import { FaUser } from 'react-icons/fa';
import Modal from '../Components/Modal';

const Profile = () => {
  const { user } = useContext(AuthContext);

  return (
    <div className="profile">
      <div className="profile-header">
        <h2>Profile</h2>
        <div className="user-icon-container">
          {user.avatar ? (
            <img src={`${process.env.PUBLIC_URL}/images/${user.avatar}-user.jpg`} alt="Avatar" className="avatar-icon" />
          ) : (
            <FaUser className="user-icon" />
          )}
        </div>
      </div>
      <div className="profile-details">
        <p>Name: {user.name}</p>
        <p>Username: {user.username}</p>
        <p>Email: {user.email}</p>
        <p>Member since: {new Date(user.created_at).toLocaleDateString()}</p>
        <Modal />
      </div>
    </div>
  );
};

export default Profile;
