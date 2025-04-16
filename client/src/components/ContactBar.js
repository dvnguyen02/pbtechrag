import React from 'react';

const ContactBar = ({ email = "duynguyen290502@gmail.com" }) => {
  return (
    <div className="contact-bar">
      Need help? Contact me at <a href={`mailto:${email}`}>{email}</a>
    </div>
  );
};

export default ContactBar;