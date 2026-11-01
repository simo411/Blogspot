import React, { useState, useContext, useEffect } from "react";
import './modal.css';
import { AuthContext } from "../context/AuthContext";
import { api } from "../api";

const AVATARS = [
    { n: 1, alt: "Female User" },
    { n: 2, alt: "Male User" },
    { n: 3, alt: "Boy User" },
    { n: 4, alt: "Female with Glasses User" },
    { n: 5, alt: "Female Profile User" },
];

const Modal = () => {
    const [modal, setModal] = useState(false);
    const [error, setError] = useState(null);
    const { setUser } = useContext(AuthContext);

    const toggleModal = () => setModal(!modal);

    useEffect(() => {
        document.body.classList.toggle('active-modal', modal);
        return () => document.body.classList.remove('active-modal');
    }, [modal]);

    const handleAvatarClick = (avatarNumber) => {
        api.setAvatar(avatarNumber)
            .then((updatedUser) => {
                setUser(updatedUser); // Profile re-renders with the new avatar
                setModal(false);
            })
            .catch((err) => setError(err.message));
    };

    return (
        <>
            <button onClick={toggleModal} className="btn-modal">
                Change Avatar
            </button>

            {modal && (
                <div className="modal">
                    <div onClick={toggleModal} className="overlay"></div>
                    <div className="modal-content">
                        <h2>Choose Your Avatar</h2>
                        <div className="avatar">
                            {AVATARS.map(({ n, alt }) => (
                                <img
                                    key={n}
                                    src={`${process.env.PUBLIC_URL}/images/${n}-user.jpg`}
                                    alt={alt}
                                    className="avatar-img"
                                    onClick={() => handleAvatarClick(n)}
                                />
                            ))}
                        </div>
                        {error && <p className="red-alert">{error}</p>}
                        <button className="close-modal" onClick={toggleModal}>
                            X
                        </button>
                    </div>
                </div>
            )}
        </>
    );
}
export default Modal;
